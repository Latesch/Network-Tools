from networktools import ping_host, traceroute_host
from init_db import save_log, delete_log, delete_logs
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import ipaddress
import socket


def valid_ip(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        pass
    try:
        socket.gethostbyname(address)
        return True
    except socket.error:
        return False

app = Flask(__name__)
app.secret_key = "secret"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    status = None
    if request.method == "POST":
        host = request.form.get("host")
        command = request.form.get("command")

        if not valid_ip(host):
          flash("Некорректный IP-адрес или имя хоста.")
          return redirect(url_for("index"))
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

@app.route('/history', methods=['GET'])
def history():
    conn = sqlite3.connect("nettools.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cur.fetchall()
    conn.close()
    return render_template("history.html", logs=logs)

@app.route('/history_detail/<int:log_id>', methods=['GET'])
def history_detail(log_id):
    conn = sqlite3.connect("nettools.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs WHERE id = ?", (str(log_id),))
    row = cur.fetchone()
    conn.close()

    return render_template("history_detail.html", row=row)

@app.route('/delete_history', methods=['POST'])
def delete_history():
    delete_logs()
    flash("История логов очищена.")
    return redirect(url_for("history"))

@app.route('/del_log_history/<int:log_id>', methods=['POST'])
def del_log_history(log_id):
    delete_log(log_id)
    flash("Лог был удален.")
    return redirect(url_for("history"))

if __name__ == '__main__':
    app.run(debug=True)
