from pythonping import ping
import paramiko
import telnetlib
import subprocess
import time
import sys
import re


ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

PAGING_COMMANDS = {
    "cisco": "terminal length 0",
    "huawei": "screen-length 0 temporary",
    "eltex": "terminal datadump",
    "ecorouter": "terminal length 0",
}


def ping_host(host, count=4, timeout=1):
    try:
        result = ping(host, count=count, timeout=timeout)
        if result.stats_packets_lost >= (count // 2):
            status = "warn"
        else:
            status = "ok"
        return result, status
    except OSError as e:
        return f"Ошибка сети: {e}", "danger"


def traceroute_host(host, max_hops=15, timeout=1, queries=1):
    try:
        is_windows = sys.platform.startswith("win")
        if is_windows:
            cmd = [
                "tracert",
                "-h", str(max_hops),
                "-w", str(int(timeout * 1000)),
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


def nslookup(host, qtype="A", dns_server="8.8.8.8", timeout=2):
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
        elif "non-existent domain" in output.lower() or "can't find" in output.lower():
            status = "danger"
        elif "name:" in output.lower() and "address" in output.lower():
            status = "ok"
        else:
            status = "warn"

        return output.strip(), status

    except subprocess.TimeoutExpired:
        return f"*** Timeout: no response from DNS server {dns_server}", "danger"
    except Exception as e:
        return f"Error while running nslookup: {e}", "danger"


def ssh_command(host, username, password, command, model="cisco", port=22, timeout=5):
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

        if model.lower() in PAGING_COMMANDS:
            chan.send(PAGING_COMMANDS[model.lower()] + "\r")
            time.sleep(0.5)
            while chan.recv_ready():
                chan.recv(4096)

        chan.send(command + "\r")
        buffer = ""
        end_markers = ["#", ">"]

        while True:
            if chan.recv_ready():
                chunk = chan.recv(4096).decode("utf-8", errors="ignore")
                buffer += chunk

                if any(buffer.strip().endswith(m) for m in end_markers):
                    break
            else:
                time.sleep(0.1)

        chan.close()
        client.close()
        clean_output = ANSI_ESCAPE.sub("", buffer)
        lines = clean_output.strip().splitlines()
        if lines and command.split()[0] in lines[0]:
            lines = lines[1:]

        return "\n".join(lines).strip(), "ok"

    except Exception as e:
        return f"SSH error: {e}", "danger"


def telnet_command(host, username, password, command, model="cisco", port=23, timeout=5):
    try:
        tn = telnetlib.Telnet(host, port, timeout)

        idx, _, _ = tn.expect([b"login: ", b"Login: ", b"Username: "], timeout)
        if idx >= 0:
            tn.write(username.encode("utf-8") + b"\r")

        idx, _, _ = tn.expect([b"Password: ", b"password: "], timeout)
        if idx >= 0:
            tn.write(password.encode("utf-8") + b"\r")

        if model.lower() in PAGING_COMMANDS:
            tn.write(PAGING_COMMANDS[model.lower()].encode("utf-8") + b"\r")
            time.sleep(0.5)
            tn.read_very_eager()

        tn.write(command.encode("utf-8") + b"\r")
        buffer = ""
        end_markers = [b"#", b">"]
        start_time = time.time()

        while True:
            chunk = tn.read_very_eager().decode("utf-8", errors="ignore")
            if chunk:
                buffer += chunk
                if any(buffer.strip().endswith(m.decode()) for m in end_markers):
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
        return f"Telnet error: {e}", "danger"
