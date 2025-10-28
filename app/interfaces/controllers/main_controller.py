from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app.infrastructure.extensions import login_manager
from app.services import logs_service, user_service
from app.services.nettools_service import run_commands, run_connect, valid_ip

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET", "POST"])
def index():
    result, status, action = None, None, request.form.get("action")

    if request.method == "POST":
        host = request.form.get("host")
        if not valid_ip(host):
            flash("Некорректный IP или доменное имя", "danger")
        else:
            match action:
                case "ping":
                    params = {
                        "count": int(request.form.get("ping_count", 4)),
                        "timeout": float(request.form.get("ping_timeout", 1)),
                    }
                case "traceroute":
                    params = {
                        "max_hops": int(request.form.get("tr_max_hops", 15)),
                        "queries": int(request.form.get("tr_queries", 1)),
                        "timeout": float(request.form.get("tr_wait", 1)),
                    }
                case "nslookup":
                    params = {
                        "qtype": request.form.get("ns_type", "A"),
                        "dns_server": request.form.get(
                            "dns_server",
                            "8.8.8.8",
                        ),
                    }
                case _:
                    flash("Неизвестная команда", "danger")
                    params = {}

            result, status = run_commands(action, host=host, **params)

    return render_template(
        "index.html",
        result=result,
        status=status,
        action=action,
    )


@login_manager.user_loader
def load_user(user_id):
    return user_service.get_user_by_id(user_id)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = user_service.authenticate_user(username, password)
        if not user:
            flash("Неверный логин или пароль", "danger")
            return redirect(url_for("main.login"))

        login_user(user)
        flash(f"Добро пожаловать, {user.username}!", "ok")
        return redirect(url_for("main.index"))

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not user_service.register_user(
            username,
            password,
            confirm_password,
        ):
            flash("Ошибка при регистрации", "danger")
            return redirect(url_for("main.register"))

        flash("Пользователь успешно зарегистрирован! Войдите в систему.", "ok")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "ok")
    return redirect(url_for("main.index"))


@bp.route("/users")
@login_required
def users():
    users = user_service.get_all_users(current_user.role)
    if users is None:
        flash("Нет доступа", "danger")
        return redirect(url_for("main.index"))
    return render_template("users.html", users=users)


@bp.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if user_service.delete_user(user_id, current_user.role):
        flash("Пользователь удалён", "success")
    else:
        flash("Ошибка при удалении пользователя", "danger")
    return redirect(url_for("main.users"))


@bp.route("/history")
@login_required
def history():
    logs = logs_service.get_all_logs()
    return render_template("history.html", logs=logs)


@bp.route("/history_detail/<int:log_id>")
@login_required
def history_detail(log_id):
    log = logs_service.get_log_by_id(log_id)
    if not log:
        flash("Лог не найден", "danger")
        return redirect(url_for("main.history"))
    return render_template("history_detail.html", log=log)


@bp.route("/delete_history", methods=["POST"])
@login_required
def delete_history():
    logs_service.delete_all_logs()
    flash("История очищена", "success")
    return redirect(url_for("main.history"))


@bp.route("/del_log_history/<int:log_id>", methods=["POST"])
@login_required
def del_log_history(log_id):
    if logs_service.delete_log(log_id):
        flash("Лог удалён", "success")
    else:
        flash("Ошибка при удалении", "danger")
    return redirect(url_for("main.history"))


@bp.route("/export/json")
@login_required
def export_json():
    logs = logs_service.export_logs_to_json()
    return jsonify(logs)


@bp.route("/connect", methods=["GET", "POST"])
@login_required
def connect():
    result, status = None, None

    if request.method == "POST":
        protocol = request.form.get("protocol")
        host = request.form.get("host")
        username = request.form.get("username")
        password = request.form.get("password")
        command = request.form.get("command")
        model = request.form.get("model", "cisco")

        jumphosts = []
        for key in request.form:
            if key.startswith("jumphosts[") and key.endswith("][host]"):
                index = key.split("[")[1].split("]")[0]
                jh_host = request.form.get(f"jumphosts[{index}][host]")
                jh_user = request.form.get(f"jumphosts[{index}][username]")
                jh_pass = request.form.get(f"jumphosts[{index}][password]")
                if jh_host and jh_user and jh_pass:
                    jumphosts.append(
                        {
                            "host": jh_host,
                            "username": jh_user,
                            "password": jh_pass,
                        }
                    )

        result, status = run_connect(
            protocol,
            host=host,
            username=username,
            password=password,
            command=command,
            model=model,
            jumphosts=jumphosts,
        )

    return render_template(
        "connect.html",
        output=result,
        status=status,
    )
