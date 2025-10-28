import asyncio
import ipaddress
import re
import socket
import subprocess
import sys
import time
from contextlib import closing
from typing import Dict, List, Tuple

import paramiko
import telnetlib3
from pythonping import ping

from app.services import logs_service

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

PAGING_COMMANDS = {
    "cisco": ["terminal length 0"],
    "huawei": ["screen-length 0 temporary"],
    "eltex": ["terminal datadump"],
    "ecorouter": [
        "configure terminal",
        "terminal length 0",
    ],
}


def valid_ip(target: str) -> bool:
    """
    Проверяет корректность IP-адреса или доменного имени.

    Args:
        target (str): IP-адрес или доменное имя.

    Returns:
        bool: True, если target корректный IP или hostname.
    """
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        if len(target) > 253 or not re.match(r"^[a-zA-Z0-9.-]+$", target):
            return False
        try:
            socket.gethostbyname(target)
            return True
        except socket.error:
            return False


def run_commands(action: str, **kwargs) -> tuple[str, str]:
    """
    Выполняет сетевую команду по её имени и сохраняет результат в логи.

    Args:
        action (str): Тип действия ("ping", "traceroute", "nslookup").
        **kwargs: Параметры команды.

    Returns:
        tuple[str, str]: (результат, статус).
    """
    host = kwargs.get("host", "unknown")
    params = {k: v for k, v in kwargs.items() if k != "password"}

    match action.lower():
        case "ping":
            output, status = ping_host(
                kwargs.get("host"),
                count=kwargs.get("count", 4),
                timeout=kwargs.get("timeout", 1),
            )
        case "traceroute":
            output, status = traceroute_host(
                kwargs.get("host"),
                max_hops=kwargs.get("max_hops", 15),
                timeout=kwargs.get("timeout", 1),
                queries=kwargs.get("queries", 1),
            )
        case "nslookup":
            output, status = nslookup(
                kwargs.get("host"),
                qtype=kwargs.get("qtype", "A"),
                dns_server=kwargs.get("dns_server", "8.8.8.8"),
                timeout=kwargs.get("timeout", 2),
            )
        case _:
            output, status = f"Неизвестная команда: {action}", "danger"

    logs_service.create_log(
        action=action,
        host=host,
        params=params,
        status=status,
        output=str(output),
    )

    return output, status


def run_connect(protocol: str, **kwargs) -> tuple[str, str]:
    """
    Устанавливает подключение по SSH или Telnet, выполняет команду
    и сохраняет результат в логи.

    Args:
        protocol (str): Протокол подключения ("ssh" или "telnet").
        **kwargs: Параметры подключения и команды.

    Returns:
        tuple[str, str]: (результат, статус).
    """
    host = kwargs.get("host", "unknown")
    params = {k: v for k, v in kwargs.items() if k != "password"}

    match protocol.lower():
        case "ssh":
            jumphosts = kwargs.get("jumphosts")
            if jumphosts and isinstance(jumphosts, list):
                dest = {
                    "host": host,
                    "username": kwargs.get("username"),
                    "password": kwargs.get("password"),
                }
                try:
                    output, status = ssh_via_jumphost(
                        jumphosts,
                        dest,
                        kwargs.get("command"),
                        model=kwargs.get("model", "cisco"),
                        port=kwargs.get("port", 22),
                        timeout=kwargs.get("timeout", 5),
                    )
                except Exception as e:
                    return f"JumpHost error: {e}", "danger"
            else:
                output, status = ssh_command(
                    kwargs.get("host"),
                    kwargs.get("username"),
                    kwargs.get("password"),
                    kwargs.get("command"),
                    model=kwargs.get("model", "cisco"),
                    port=kwargs.get("port", 22),
                    timeout=kwargs.get("timeout", 5),
                )

        case "telnet":
            output, status = telnet_command(
                kwargs.get("host"),
                kwargs.get("username"),
                kwargs.get("password"),
                kwargs.get("command"),
                model=kwargs.get("model", "cisco"),
                port=kwargs.get("port", 23),
                timeout=kwargs.get("timeout", 5),
            )
        case _:
            output, status = f"Неизвестный протокол: {protocol}", "danger"

    logs_service.create_log(
        action=protocol,
        host=host,
        params=params,
        status=status,
        output=str(output),
    )

    return output, status


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
        status = "warn" if result.stats_packets_lost >= (count // 2) else "ok"
        return result, status
    except OSError as e:
        return f"Ошибка сети: {e}", "danger"


def traceroute_host(
    host: str,
    max_hops: int = 15,
    timeout: int = 1,
    queries: int = 1,
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

        cmd = (
            [
                "tracert",
                "-h",
                str(max_hops),
                "-w",
                f"{int(timeout * 1000)}",
                host,
            ]
            if is_windows
            else [
                "traceroute",
                "-m",
                str(max_hops),
                "-q",
                str(queries),
                "-w",
                str(int(timeout)),
                host,
            ]
        )

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if is_windows:
            status = (
                "warn"
                if "request timed out" in output.lower()
                else "ok" if host.lower() in output.lower() else "danger"
            )
        else:
            status = (
                "warn"
                if host.lower() in output.lower() and "*" in output
                else "ok" if host.lower() in output.lower() else "danger"
            )

        return output.strip(), status

    except Exception as e:
        return f"Ошибка при выполнении traceroute: {e}", "danger"


def nslookup(
    host: str,
    qtype: str = "A",
    dns_server: str = "8.8.8.8",
    timeout: int = 2,
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
        cmd = ["nslookup", f"-type={qtype}", host, dns_server]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        lower_output = output.lower()

        checks = [
            (
                lambda o: "timed out" in o or "no response" in o,
                "danger",
            ),
            (
                lambda o: "non-existent domain" in o or "can't find" in o,
                "danger",
            ),
            (
                lambda o: "name:" in o and "address" in o,
                "ok",
            ),
        ]

        status = next((s for cond, s in checks if cond(lower_output)), "warn")

        return output.strip(), status

    except subprocess.TimeoutExpired:
        return (
            f"*** Timeout: no response from DNS server {dns_server}",
            "danger",
        )
    except Exception as e:
        return (
            f"Error while running nslookup: {e}",
            "danger",
        )


def ssh_command(
    host: str,
    username: str,
    password: str,
    command: str,
    model: str = "cisco",
    port: int = 22,
    timeout: int = 5,
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
    try:
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                look_for_keys=False,
                allow_agent=False,
            )

            with closing(client.invoke_shell()) as chan:
                chan.settimeout(timeout)
                time.sleep(1)

                if chan.recv_ready():
                    _ = chan.recv(4096)

                match model.lower():
                    case "linux":
                        pass
                    case m if m in PAGING_COMMANDS:
                        for cmd in PAGING_COMMANDS[m]:
                            chan.send(cmd + "\r")
                            time.sleep(0.5)
                            while chan.recv_ready():
                                chan.recv(4096)
                    case _:
                        pass

                chan.send(command + "\r")
                buffer = ""
                end_markers = ["#", ">", "$"]

                start_time = time.time()
                while True:
                    if chan.recv_ready():
                        chunk = chan.recv(4096).decode(
                            "utf-8",
                            errors="ignore",
                        )
                        buffer += chunk
                        ends_with_marker = (
                            buffer.strip().endswith(m) for m in end_markers
                        )
                        if any(ends_with_marker):
                            break
                    if time.time() - start_time > timeout:
                        break
                    time.sleep(0.1)

                clean_output = ANSI_ESCAPE.sub("", buffer)
                lines = clean_output.strip().splitlines()
                if lines and command.split()[0] in lines[0]:
                    lines = lines[1:]

                return "\n".join(lines).strip(), "ok"

    except Exception as e:
        return f"SSH error: {e}", "danger"


def telnet_command(
    host: str,
    username: str,
    password: str,
    command: str,
    model: str = "cisco",
    port: int = 23,
    timeout: int = 5,
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
        async with telnetlib3.open_connection(
            host, port=port, connect_minwait=0.5, connect_maxwait=1.0
        ) as (reader, writer):
            await reader.readuntil(":", timeout=timeout)
            writer.write(username + "\n")

            await reader.readuntil(":", timeout=timeout)
            writer.write(password + "\n")

            match model.lower():
                case "linux":
                    pass
                case m if m in PAGING_COMMANDS:
                    for prep_cmd in PAGING_COMMANDS[m]:
                        writer.write(prep_cmd + "\n")
                        await asyncio.sleep(0.3)
                case _:
                    pass

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

    try:
        return asyncio.run(asyncio.wait_for(run_telnet(), timeout=timeout))
    except asyncio.TimeoutError:
        return "Telnet error: session timeout", "danger"
    except Exception as e:
        return f"Telnet error: {e}", "danger"


def ssh_via_jumphost(
    jump_chain: List[Dict[str, str]],
    dest: Dict[str, str],
    command: str,
    model: str = "cisco",
    port: int = 22,
    timeout: int = 5,
) -> Tuple[str, str]:
    """
    Подключение к целевому устройству через один или несколько jump host'ов.
    Поддерживает рекурсивную схему переходов:
        localhost → jumphost1 → jumphost2 → ... → destination

    Args:
        jump_chain (List[Dict[str, str]]): Список промежуточных хостов.
            Пример:
            [
            {"host": "192.168.1.1", "username": "jump1", "password": "pass1"},
            {"host": "10.0.0.5", "username": "jump2", "password": "pass2"},
            ]
        dest (Dict[str, str]): Конечное устройство.
            {"host": "10.0.0.10", "username": "admin", "password": "secret"}
        command (str): Команда для выполнения на конечном устройстве.
        model (str): Вендор (Cisco, Huawei и т.д.).
        port (int): SSH порт.
        timeout (int): Таймаут подключения.

    Returns:
        Tuple[str, str]: (output, status)
    """
    try:
        current_jump = jump_chain[0]
        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        jump_client.connect(
            current_jump["host"],
            port=current_jump.get("port", 22),
            username=current_jump["username"],
            password=current_jump["password"],
            timeout=timeout,
        )

        if len(jump_chain) > 1:
            next_jump_chain = jump_chain[1:]
            next_host = next_jump_chain[0]

            transport = jump_client.get_transport()
            chan = transport.open_channel(
                "direct-tcpip",
                (next_host["host"], next_host.get("port", 22)),
                ("127.0.0.1", 0),
            )

            with paramiko.SSHClient() as inner_client:
                inner_client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy()
                )
                inner_client.connect(
                    next_host["host"],
                    username=next_host["username"],
                    password=next_host["password"],
                    sock=chan,
                    timeout=timeout,
                )

                return ssh_via_jumphost(
                    next_jump_chain, dest, command, model, port, timeout
                )

        else:
            transport = jump_client.get_transport()
            chan = transport.open_channel(
                "direct-tcpip",
                (dest["host"], dest.get("port", 22)),
                ("127.0.0.1", 0),
            )

            with paramiko.SSHClient() as dest_client:
                dest_client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy()
                )
                dest_client.connect(
                    dest["host"],
                    username=dest["username"],
                    password=dest["password"],
                    sock=chan,
                    timeout=timeout,
                )

                stdin, stdout, stderr = dest_client.exec_command(
                    command, timeout=timeout
                )
                output = stdout.read().decode("utf-8") + stderr.read().decode(
                    "utf-8"
                )

        return output, "ok"

    except Exception as e:
        return f"Ошибка при подключении через jumphost: {e}", "danger"

    finally:
        try:
            jump_client.close()
        except Exception:
            pass
