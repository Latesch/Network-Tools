import asyncio
import re
import subprocess
import sys
import time

import paramiko
import telnetlib3
from pythonping import ping

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

PAGING_COMMANDS = {
    "cisco": ["terminal length 0"],
    "huawei": ["screen-length 0 temporary"],
    "eltex": ["terminal datadump"],
    "ecorouter": [
        "configure terminal",
        "terminal length 0"
    ]
}


def ping_host(
    host: str,
    count: int = 4,
    timeout: int = 1,
) -> tuple[str, str]:
    """
    Выполняет ping до указанного хоста.


    Args:
    host (str): IP или доменное имя.
    count (int): Количество пакетов.
    timeout (int): Таймаут ожидания ответа (секунды).


    Returns:
    tuple[str, str]: (результат команды, статус: "ok", "warn" или "danger").
    """
    try:
        result = ping(host, count=count, timeout=timeout)
        if result.stats_packets_lost >= (count // 2):
            status = "warn"
        else:
            status = "ok"
        return result, status
    except OSError as e:
        return f"Ошибка сети: {e}", "danger"


def traceroute_host(
    host: str,
    max_hops: int = 15,
    timeout: int = 1,
    queries: int = 1
) -> tuple[str, str]:
    """
    Выполняет traceroute до указанного хоста.


    Args:
    host (str): IP или доменное имя.
    max_hops (int): Максимальное количество прыжков.
    timeout (int): Таймаут ожидания (секунды).
    queries (int): Количество запросов.


    Returns:
    tuple[str, str]: (результат команды, статус: "ok", "warn" или "danger").
    """
    try:
        is_windows = sys.platform.startswith("win")
        if is_windows:
            cmd = [
                "tracert",
                "-h", str(max_hops),
                "-w", f"{int(timeout * 1000)}",
                host,
            ]
        else:
            cmd = [
                "traceroute",
                "-m", str(max_hops),
                "-q", str(queries),
                "-w", str(int(timeout)),
                host,
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if is_windows:
            if "request timed out" in output.lower():
                status = "warn"
            elif host.lower() in output.lower():
                status = "ok"
            else:
                status = "danger"
        else:
            if host.lower() in output.lower():
                status = "warn" if "*" in output else "ok"
            else:
                status = "danger"

        return output.strip(), status

    except Exception as e:
        return f"Ошибка при выполнении traceroute: {e}", "danger"


def nslookup(
    host: str,
    qtype: str = "A",
    dns_server: str = "8.8.8.8",
    timeout: int = 2
) -> tuple[str, str]:
    """
    Выполняет DNS-запрос (nslookup).


    Args:
    host (str): Доменное имя.
    qtype (str): Тип записи (A, MX, AAAA и т.д.).
    dns_server (str): DNS-сервер.
    timeout (int): Таймаут ожидания (секунды).


    Returns:
    tuple[str, str]: (результат запроса, статус: "ok", "warn" или "danger").
    """
    try:
        cmd = ["nslookup", "-type=" + qtype, host, dns_server]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if "timed out" in output.lower() or "no response" in output.lower():
            status = "danger"
        elif (
            "non-existent domain" in output.lower()
            or "can't find" in output.lower()
        ):
            status = "danger"
        elif "name:" in output.lower() and "address" in output.lower():
            status = "ok"
        else:
            status = "warn"

        return output.strip(), status

    except subprocess.TimeoutExpired:
        return (
            f"*** Timeout: no response from DNS server {dns_server}",
            "danger",
        )
    except Exception as e:
        return f"Error while running nslookup: {e}", "danger"


def ssh_command(
    host: str,
    username: str,
    password: str,
    command: str,
    model: str = "cisco",
    port: int = 22,
    timeout: int = 5
) -> tuple[str, str]:
    """
    Выполняет SSH-подключение и выполнение команды.


    Args:
    host (str): IP или доменное имя.
    username (str): Имя пользователя.
    password (str): Пароль.
    command (str): Команда для выполнения.
    model (str): Модель оборудования (для отключения paging).
    port (int): Порт SSH.
    timeout (int): Таймаут (секунды).


    Returns:
    tuple[str, str]: (результат выполнения, статус: "ok" или "danger").
    """
    client = None
    chan = None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            host, port=port, username=username, password=password,
            timeout=timeout, look_for_keys=False, allow_agent=False
        )

        chan = client.invoke_shell()
        chan.settimeout(timeout)

        time.sleep(1)
        if chan.recv_ready():
            _ = chan.recv(4096)

        if model.lower() in PAGING_COMMANDS and model.lower() != "linux":
            for cmd in PAGING_COMMANDS[model.lower()]:
                chan.send(cmd + "\r")
                time.sleep(0.5)
                while chan.recv_ready():
                    chan.recv(4096)

        chan.send(command + "\r")
        buffer = ""
        end_markers = ["#", ">", "$"]

        while True:
            if chan.recv_ready():
                chunk = chan.recv(4096).decode("utf-8", errors="ignore")
                buffer += chunk

                if any(buffer.strip().endswith(m) for m in end_markers):
                    break
            else:
                time.sleep(0.1)

        clean_output = ANSI_ESCAPE.sub("", buffer)
        lines = clean_output.strip().splitlines()
        if lines and command.split()[0] in lines[0]:
            lines = lines[1:]

        return "\n".join(lines).strip(), "ok"

    except Exception as e:
        return f"SSH error: {e}", "danger"

    finally:
        if chan:
            chan.close()
        if client:
            client.close()


def telnet_command(
    host: str,
    username: str,
    password: str,
    command: str,
    model: str = "cisco",
    port: int = 23,
    timeout: int = 5
) -> tuple[str, str]:
    """
    Выполняет Telnet-подключение и выполнение команды (async).


    Args:
    host (str): IP или доменное имя.
    username (str): Имя пользователя.
    password (str): Пароль.
    command (str): Команда для выполнения.
    model (str): Модель оборудования (зарезервировано для будущего).
    port (int): Порт Telnet.
    timeout (int): Таймаут (секунды).


    Returns:
    tuple[str, str]: (результат выполнения, статус: "ok" или "danger").
    """
    async def run_telnet():
        reader, writer = await telnetlib3.open_connection(
            host, port=port, connect_minwait=0.5, connect_maxwait=1.0
        )
        try:
            await reader.readuntil(":", timeout=timeout)
            writer.write(username + "\n")

            await reader.readuntil(":", timeout=timeout)
            writer.write(password + "\n")

            if model.lower() in PAGING_COMMANDS and model.lower() != "linux":
                for prep_cmd in PAGING_COMMANDS[model.lower()]:
                    writer.write(prep_cmd + "\n")
                    await asyncio.sleep(0.3)

            writer.write(command + "\n")

            buffer = ""
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        reader.read(1024),
                        timeout=1,
                    )
                except asyncio.TimeoutError:
                    break
                if not chunk:
                    break
                buffer += chunk
                if any(buffer.strip().endswith(m) for m in ["#", ">", "$"]):
                    break

            clean_output = ANSI_ESCAPE.sub("", buffer).strip()
            return clean_output, "ok"

        finally:
            writer.close()
            await writer.wait_closed()

    try:
        return asyncio.run(asyncio.wait_for(run_telnet(), timeout=timeout))
    except asyncio.TimeoutError:
        return "Telnet error: session timeout", "danger"
    except Exception as e:
        return f"Telnet error: {e}", "danger"
