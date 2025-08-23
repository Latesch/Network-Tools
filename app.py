from networktools import ping_host, traceroute_host
from init_db import save_log, delete_log, delete_logs, create_user
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import sqlite3
import ipaddress
import socket
import re

class User(UserMixin):
    def __init__(self, id, username, password_hash, role="user"):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

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

app = Flask(__name__)
app.secret_key = "secret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" 

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    status = None
    if request.method == "POST":
        host = request.form.get("host")
        command = request.form.get("action")

        if not valid_ip(host):
          flash("❌ Некорректный IP или доменное имя", "danger")
          return render_template("index.html", result=None, status=None)
        else:            
          if command == "ping":
              ping_timeout = float(request.form.get("ping_timeout"))
              ping_count = int(request.form.get("ping_count"))
              result, status = ping_host(host, ping_count, ping_timeout)
              save_log("ping", host, {"count": ping_count, "timeout": ping_timeout}, status, str(result))
          elif command == "traceroute":
              tr_max_hops = int(request.form.get("tr_max_hops"))
              tr_queries = int(request.form.get("tr_queries"))
              tr_wait = float(request.form.get("tr_wait"))
              result, status = traceroute_host(host, tr_max_hops, tr_wait, tr_queries)
              save_log("traceroute", host, {"max_hops": tr_max_hops, "q": tr_queries, "wait": tr_wait}, status, str(result))

    return render_template("index.html", result=result, status=status)

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("nettools.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, role FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("nettools.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            flash("Пользователь не найден", "danger")
            return redirect(url_for("login"))

        if check_password_hash(row[2], password):
            user = User(*row)
            login_user(user)
            flash("Успешный вход!", "success")
            return redirect(url_for("index"))
        else:
            flash("Неверный пароль", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("index"))

@app.route('/history', methods=['GET'])
@login_required
def history():
    conn = sqlite3.connect("nettools.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cur.fetchall()
    conn.close()
    return render_template("history.html", logs=logs, username=current_user.username)

@app.route('/history_detail/<int:log_id>', methods=['GET'])
@login_required
def history_detail(log_id):
    conn = sqlite3.connect("nettools.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs WHERE id = ?", (str(log_id),))
    row = cur.fetchone()
    conn.close()

    return render_template("history_detail.html", log=row)

@app.route('/delete_history', methods=['POST'])
def delete_history():
    delete_logs()
    flash("История логов очищена.")
    return redirect(url_for("history"))

@app.route('/del_log_history/<int:log_id>', methods=['POST'])
def del_log_history(log_id):
    delete_log(log_id)
    flash("Лог был удален.", "ok")
    return redirect(url_for("history"))

if __name__ == '__main__':
    app.run(debug=True)
