# NetTools Web

A web application built with **Flask** that provides network utilities.
It allows you to run basic network commands via a web interface:

* `Ping` with customizable parameters (packet count, timeout, etc.);
* `Traceroute` with configurable options;
* Color-coded results (success, warning, error);
* Logging of all requests into an SQLite database;
* View history and details of each request;
* Delete individual logs or the entire history;
* User authentication (Flask-Login) with password hashing;
* User registration via web interface;
* User roles (regular user / administrator);
* Access control:

  * guest → only execute commands;
  * authenticated user → execute commands + view/manage logs.

---

## 🚀 Installation & Run

### 1. Clone the repository

```bash
git clone https://github.com/Latesch/Network-Tools.git
cd Network-Tools
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activation:

* Linux/macOS:

  ```bash
  source .venv/bin/activate
  ```
* Windows (cmd):

  ```cmd
  .venv\Scripts\activate
  ```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

#### Local run (development)

```bash
flask run
```

By default, the app will be available at:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

#### Access from other devices (external)

```bash
flask run --host=0.0.0.0
```

If your computer IP is `192.168.1.10`, the app will be available at:
👉 [http://192.168.1.10:5000](http://192.168.1.10:5000)

---

#### Run on a custom port

```bash
flask run --host=0.0.0.0 --port=8080
```

Now the server is available on port `8080`:
👉 [http://192.168.1.10:8080](http://192.168.1.10:8080)

---

## 📂 Project Structure

```
Network-Tools/
│
├── nettools/
│   ├── app.py              # Flask application factory (create_app)
│   ├── extensions.py       # Extensions (db, login_manager, etc.)
│   ├── models.py           # SQLAlchemy models (User, Log)
│   ├── view.py             # Main routes (Blueprint "main")
│   └── nettools.py         # Logic for ping and traceroute
│
├── instance/               # Local data (ignored by Git)
│   └── nettools.db         # SQLite database
│
├── templates/              # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── connect.html
│   ├── history.html
│   └── history_detail.html
│
├── static/                 # Static files (CSS, JS)
│   ├── apple-touch-icon.png
│   ├── favicon.png
│   ├── favicon.ico
│   └── style.css
│
├── requirements.txt        # Dependencies
├── README.md               # Documentation project
└── run.py                  # Entry point (flask run → create_app())
```

---

## 🔑 Authentication & Roles

Using **Flask-Login**.

Users can register via `/register` (passwords are stored as hashes).

👉 Invalid login or password will trigger an error message.
👉 Login/Logout button dynamically updates depending on auth state.

---

## 🗄 Database

* All executed requests are stored in `nettools.db`.
* **Log** model stores:

  * `id`, `timestamp`, `action`, `host`, `params`, `status`, `output`.
* **User** model stores:

  * `id`, `timestamp`, `username`, `password_hash`, `role`.

---

## 📌 TODO (future improvements)

* Integration with **xterm.js** for live terminal;
* Real-time interactive sessions;
* Ansible integration;
* Network inventory database (auto-discovery);
* SNMP/NetFlow integration;
* Network topology visualization;
* Jumphost support;
* OpenAPI.json.

---

## 🛠 Tech Stack

* Python 3.x
* Flask + Flask-Login
* SQLAlchemy (SQLite)
* Bootstrap (via CDN)
* PythonPing / Subprocess
* Paramiko + telnetlib
* Werkzeug (for password hashing)

---

## 🤝 Contributing Guide

[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 👤 Author

Project created for **Python & Flask practice**.
Author: **Late**
[Telegram @Latesch](https://t.me/Latesch)
