# NetTools Web

A **Flask**-based web application with built-in network utilities.  
It allows running basic network commands via a web interface:

* `Ping` with configurable parameters (packet count, timeout, etc.);
* `Traceroute` with adjustable options;
* Color-coded results (success, warning, error);
* Logging of all requests into an SQLite database;
* History view with detailed request information;
* Ability to delete single logs or the entire history;
* User authentication (Flask-Login) with password hashing;
* User registration through the web interface;
* User roles (regular user / administrator);
* Access control:
  * guest → only run commands;
  * authenticated user → run commands + view/manage logs.

---

## 🚀 Installation & Run

### 1. Clone the repository

```bash
git clone https://github.com/Latesch/Network-Tools.git
cd Network-Tools
````

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

* Linux/macOS:

  ```bash
  source venv/bin/activate
  ```
* Windows (cmd):

  ```cmd
  venv\Scripts\activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
flask run
```

Once started, the app will be available at:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📂 Project Structure

```
Network-Tools/
│
├── app.py              # Flask app factory (create_app)
├── extensions.py       # Extensions (db, login_manager, etc.)
├── models.py           # SQLAlchemy models (User, Log)
├── view.py             # Main routes (Blueprint "main")
├── nettools.py         # Ping & traceroute logic
├── run.py              # Entry point (flask run → create_app())
├── instance/           # Local data (ignored by Git)
│   └── nettools.db     # SQLite database
├── templates/          # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── history.html
│   └── history_detail.html
├── static/             # Static files (CSS, JS)
│   └── style.css
├── requirements.txt    # Dependencies list
└── README.md           # This file
```

---

## 🔑 Authentication & Roles

The app uses **Flask-Login** for authentication.

User registration is available at `/register` (passwords are stored as hashes).

👉 Invalid credentials trigger an error message.
👉 Login/Logout buttons update dynamically depending on user state.

---

## 🗄 Database

* All requests are stored in `nettools.db`.
* **Log** model stores:

  * `id`, `timestamp`, `action`, `host`, `params`, `status`, `output`
* **User** model stores:

  * `id`, `timestamp`, `username`, `password_hash`, `role`

---

## 📌 TODO (future improvements)

* xtermjs integration;
* SSH access to devices & command execution (Paramiko);
* Ansible integration;
* Inventory database (auto-discovery);
* SNMP/NetFlow integration;
* Network diagrams & topology visualization;
* OpenAPI.json support.

---

## 🛠 Tech Stack

* Python 3.x
* Flask + Flask-Login
* SQLAlchemy (SQLite)
* Bootstrap (via CDN)
* PythonPing / Subprocess / Scapy
* Werkzeug (password hashing)

---

## 🤝 Contributing Guide

Thank you for contributing! 🚀

### 📌 Rules

* All new features and bugfixes go into **separate branches**:

  ```bash
  git checkout -b feature/my-feature
  git checkout -b fix/my-bug
  ```
* Before opening a PR, check code style:

  ```bash
  flake8
  ```
* Use clear commit messages:

  * `feat: added ...`
  * `fix: fixed ...`
  * `docs: updated ...`

### 🔀 Pull Requests

1. Fork the repository and create a new branch.
2. Run the project and ensure everything works.
3. Run the linter:

   ```bash
   flake8
   ```
4. Open a PR into `main` with a description of your changes.

---

## 👤 Author

Project created for practicing Python & Flask.
Author: **Late** ([@telegram\Latesch](https://t.me/Latesch))