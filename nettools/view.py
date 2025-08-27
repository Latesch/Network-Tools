from .networktools import ping_host, traceroute_host, nslookup
from .networktools import ssh_command, telnet_command
from flask import Blueprint, render_template, redirect, url_for, flash
from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Log
from .app import db, login_manager
import ipaddress
import socket
import re


bp = Blueprint("main", __name__)


def valid_ip(value: str) -> bool:
    if not value or len(value) > 255:
        return False

    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        pass

    if value.endswith("."):
        value = value[:-1]

    labels = value.split(".")
    hostname_regex = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
    if not all(hostname_regex.match(label) for label in labels):
        return False

    try:
        socket.gethostbyname(value)
        return True
    except socket.gaierror:
        return False


@bp.route('/', methods=['GET', 'POST'])
def index():
    result = None
    status = None
    action = request.form.get("action")
    if request.method == "POST":
        host = request.form.get("host")
        command = action

        if not valid_ip(host):
            flash("Некорректный IP или доменное имя", "danger")
            return render_template(
                "index.html", result=None, status=None, action=command
            )
        else:
            match command:
                case "ping":
                    ping_timeout = float(request.form.get("ping_timeout"))
                    ping_count = int(request.form.get("ping_count"))
                    result, status = ping_host(host, ping_count, ping_timeout)
                    params = {"count": ping_count, "timeout": ping_timeout}
                    Log.save("ping", host, params, status, str(result))

                case "traceroute":
                    tr_max_hops = int(request.form.get("tr_max_hops"))
                    tr_queries = int(request.form.get("tr_queries"))
                    tr_wait = float(request.form.get("tr_wait"))
                    result, status = traceroute_host(
                        host, tr_max_hops, tr_wait, tr_queries
                    )
                    params = {
                        "max_hops": tr_max_hops,
                        "q": tr_queries,
                        "wait": tr_wait
                    }
                    Log.save("traceroute", host, params, status, str(result))

                case "nslookup":
                    ns_type = str(request.form.get("ns_type"))
                    dns_server = str(request.form.get("dns_server"))
                    result, status = nslookup(host, ns_type, dns_server)
                    params = {"ns_type": ns_type, "dns_server": dns_server}
                    Log.save("nslookup", host, params, status, str(result))

                case _:
                    flash("Unknown command", "danger")

    return render_template(
        "index.html", result=result, status=status, action=action
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Пользователь не найден", "danger")
            return redirect(url_for("main.login"))

        if not user.check_password(password):
            flash("Неверный пароль", "warn")
            return redirect(url_for("main.login"))

        login_user(user)
        flash(f"Добро пожаловать, {user.username}!", "ok")
        return redirect(url_for("main.index"))

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if User.query.filter_by(username=username).first():
            flash("Такой пользователь уже есть", "danger")
            return redirect(url_for("main.register"))

        if password != confirm_password:
            flash("Пароли не совпадают", "warn")
            return redirect(url_for("main.register"))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Пользователь успешно зарегистрирован! "
            "Войдите в систему.",
            "ok",
        )
        return redirect(url_for("main.login"))

    return render_template("register.html")


@bp.route("/users")
@login_required
def users():
    if current_user.role != "admin":
        flash(
            "Только администратор может просматривать пользователей.",
            "danger"
        )
        return redirect(url_for("main.index"))

    users = User.query.all()
    return render_template("users.html", users=users)


@bp.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        flash("Только администратор может удалять пользователей.", "danger")
        return redirect(url_for("main.users"))

    if User.delete_user(user_id):
        flash("Пользователь удалён.", "ok")
    else:
        flash("Пользователь не найден или это администратор.", "danger")

    return redirect(url_for("main.users"))


@bp.route('/history', methods=['GET'])
@login_required
def history():
    logs = Log.query.all()
    return render_template("history.html", logs=logs)


@bp.route('/history_detail/<int:log_id>', methods=['GET'])
@login_required
def history_detail(log_id):
    log = Log.query.get(log_id)
    return render_template("history_detail.html", log=log)


@bp.route('/delete_history', methods=['POST'])
def delete_history():
    Log.clear_all()
    flash("История логов очищена.")
    return redirect(url_for("main.history"))


@bp.route('/del_log_history/<int:log_id>', methods=['POST'])
def del_log_history(log_id):
    Log.delete_by_id(log_id)
    flash("Лог был удален.", "ok")
    return redirect(url_for("main.history"))


@bp.route("/export/json")
@login_required
def export_json():
    logs = Log.query.all()
    data = [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "action": log.action,
            "host": log.host,
            "params": log.params,
            "status": log.status,
            "output": log.output,
        }
        for log in logs
    ]
    return jsonify(data)


@bp.route("/connect", methods=["GET", "POST"])
@login_required
def connect():
    output, status = None, None

    if request.method == "POST":
        protocol = request.form.get("protocol")
        model = request.form.get("model")
        host = request.form.get("host")
        username = request.form.get("username")
        password = request.form.get("password")
        command = request.form.get("command")

        if protocol == "ssh":
            output, status = ssh_command(
                host, username, password, command, model
            )
        elif protocol == "telnet":
            output, status = telnet_command(
                host, username, password, command, model
            )

    return render_template("connect.html", output=output, status=status)
