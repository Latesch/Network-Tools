import asyncio
from unittest import mock
from unittest.mock import Mock

import pytest

from app.services.nettools_service import (
    ssh_command,
    ssh_via_jumphost,
    telnet_command,
    valid_ip,
)


class FakeChannel:
    """Фейковый SSH-канал для имитации чтения/записи в тестах."""

    def __init__(self, recv_sequence, ready_sequence):
        self._recv_sequence = list(recv_sequence)
        self._ready_sequence = list(ready_sequence)
        self.sent = []

    def settimeout(self, timeout):
        self.timeout = timeout

    def recv_ready(self):
        if self._ready_sequence:
            return self._ready_sequence.pop(0)
        return False

    def recv(self, _size):
        if not self._recv_sequence:
            return b""
        return self._recv_sequence.pop(0)

    def send(self, data):
        self.sent.append(data)

    def close(self):
        return None


class FakeTelnetReader:
    """Асинхронный reader для эмуляции telnet-приглашений и вывода."""

    def __init__(self, readuntil_responses, read_responses):
        self._readuntil_responses = iter(readuntil_responses)
        self._read_responses = iter(read_responses)

    async def readuntil(self, *args, **kwargs):
        return next(self._readuntil_responses)

    async def read(self, _size):
        return next(self._read_responses)


class FakeTelnetConnection:
    """Асинхронный контекст-менеджер, возвращающий reader/writer."""

    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer

    async def __aenter__(self):
        return self._reader, self._writer

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture()
def patch_asyncio_run(monkeypatch):
    """Подменяет asyncio.run на loop.run_until_complete для тестов."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    monkeypatch.setattr(asyncio, "run", loop.run_until_complete)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)


def test_valid_ip_correct_ipv4():
    """Корректный IPv4 должен пройти валидацию."""
    assert valid_ip("192.168.1.1") is True


def test_valid_ip_invalid_ipv4():
    """Некорректный IPv4 должен быть отклонён."""
    assert valid_ip("192.168.1.999") is False


def test_valid_ip_correct_ipv6():
    """Корректный IPv6 должен пройти валидацию."""
    assert valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True


def test_valid_ip_invalid_ipv6():
    """Некорректный IPv6 должен быть отклонён."""
    assert valid_ip("2001:db8:85g3::8a2e:370:7334") is False


def test_valid_hostname():
    """Корректное доменное имя."""
    assert valid_ip("example.com") is True


def test_valid_hostname_with_invalid_chars():
    """Недопустимые символы в имени узла."""
    assert valid_ip("exa$mple!.com") is False


def test_ssh_command_success_invokes_connect_with_expected_args():
    """Проверяет успешный SSH-вызов и корректные параметры connect."""
    channel = FakeChannel(
        recv_sequence=[
            b"Welcome!\n",
            b"terminal length 0\n#",
            b"show version\nVersion 1.0\n#",
        ],
        ready_sequence=[True, True, False, True],
    )
    mock_client = mock.MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.invoke_shell.return_value = channel

    with mock.patch(
        "app.services.nettools_service.paramiko.SSHClient",
        return_value=mock_client,
    ):
        output, status = ssh_command(
            host="192.0.2.1",
            username="admin",
            password="secret",
            command="show version",
            model="cisco",
            port=2222,
            timeout=3,
        )

    assert status == "ok"
    assert output == "Version 1.0\n#"
    mock_client.connect.assert_called_once_with(
        "192.0.2.1",
        port=2222,
        username="admin",
        password="secret",
        timeout=3,
        look_for_keys=False,
        allow_agent=False,
    )
    assert "terminal length 0\r" in channel.sent
    assert "show version\r" in channel.sent


def test_ssh_command_returns_danger_on_exception():
    """Проверяет, что при ошибке подключения возвращается статус danger."""
    mock_client = mock.MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.connect.side_effect = RuntimeError("boom")

    with mock.patch(
        "app.services.nettools_service.paramiko.SSHClient",
        return_value=mock_client,
    ):
        output, status = ssh_command(
            host="192.0.2.2",
            username="user",
            password="bad",
            command="show ip",
        )

    assert status == "danger"
    assert output.startswith("SSH error:")


def test_ssh_via_jumphost_connects_through_chain():
    """Проверяет подключение к целевому устройству через jumphost."""
    jump_client = mock.MagicMock()
    dest_client = mock.MagicMock()
    dest_client.__enter__.return_value = dest_client

    transport = mock.MagicMock()
    jump_client.get_transport.return_value = transport
    transport.open_channel.return_value = mock.Mock()

    stdout = mock.MagicMock()
    stderr = mock.MagicMock()
    stdout.read.return_value = b"OK\n"
    stderr.read.return_value = b""
    dest_client.exec_command.return_value = (mock.Mock(), stdout, stderr)

    with mock.patch(
        "app.services.nettools_service.paramiko.SSHClient",
        side_effect=[jump_client, dest_client],
    ):
        output, status = ssh_via_jumphost(
            jump_chain=[
                {
                    "host": "203.0.113.10",
                    "username": "jump",
                    "password": "jump-pass",
                }
            ],
            dest={
                "host": "203.0.113.20",
                "username": "admin",
                "password": "dest-pass",
            },
            command="show clock",
            model="cisco",
            port=22,
            timeout=4,
        )

    assert status == "ok"
    assert output == "OK\n"
    jump_client.connect.assert_called_once_with(
        "203.0.113.10",
        port=22,
        username="jump",
        password="jump-pass",
        timeout=4,
    )
    dest_client.connect.assert_called_once_with(
        "203.0.113.20",
        username="admin",
        password="dest-pass",
        sock=transport.open_channel.return_value,
        timeout=4,
    )


def test_telnet_command_ok(monkeypatch, patch_asyncio_run):
    """Проверяет успешное выполнение telnet-команды."""

    reader = FakeTelnetReader(["login:", "Password:"], ["command output", ""])
    writer = Mock()
    connection = FakeTelnetConnection(reader, writer)
    monkeypatch.setattr(
        "app.services.nettools_service.telnetlib3.open_connection",
        lambda *args, **kwargs: connection,
    )

    output, status = telnet_command(
        host="10.0.0.1",
        username="admin",
        password="secret",
        command="show version",
        model="linux",
    )

    assert status == "ok"
    assert output == "command output"
    writer.write.assert_any_call("admin\n")
    writer.write.assert_any_call("secret\n")
    writer.write.assert_any_call("show version\n")


def test_telnet_command_timeout(monkeypatch, patch_asyncio_run):
    """Проверяет обработку таймаута telnet-сессии."""

    class TimeoutReader:
        """Читалка, создающая задержку для срабатывания таймаута."""

        async def readuntil(self, *args, **kwargs):
            await asyncio.sleep(0.05)
            return "login:"

        async def read(self, _size):
            return ""

    reader = TimeoutReader()
    writer = Mock()
    connection = FakeTelnetConnection(reader, writer)
    monkeypatch.setattr(
        "app.services.nettools_service.telnetlib3.open_connection",
        lambda *args, **kwargs: connection,
    )

    output, status = telnet_command(
        host="10.0.0.1",
        username="admin",
        password="secret",
        command="show version",
        model="linux",
        timeout=0.01,
    )

    assert status == "danger"
    assert output == "Telnet error: session timeout"
