# NetTools Web

![Python](https://img.shields.io/badge/python-3.13-blue.svg)  
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey.svg)  
![CI/CD](https://github.com/Latesch/Network-Tools/actions/workflows/ci.yml/badge.svg)  
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)  
![License](https://img.shields.io/github/license/Latesch/Network-Tools)

A **Flask**-based web application with built-in network utilities.
It allows you to run basic network commands through a web interface:

* **Network commands via web interface**:

  * `Ping` with configurable parameters (packet count, timeout, etc.);
  * `Traceroute` with customizable options;
  * `NSLookup` with record type and DNS server selection;
  * Device connection via **SSH** and **Telnet**;
  * Jumphost support for chained connections.

* **Modern interface**:

  * Bootstrap 5 and Bootstrap Icons;
  * color-coded results (success, warning, error);
  * cards, tables, and UI elements in a unified style.

* **Log management**:

  * automatic logging of all requests in **SQLite**;
  * view history and detailed logs of each request;
  * delete individual records or the entire history;
  * export logs to JSON.

* **Users and roles**:

  * authentication and registration via Flask-Login;
  * password hashing;
  * user roles (**user** / **admin**);
  * access control.

---

## 🚀 Installation and Run

### 1. Clone the repository

```bash
git clone https://github.com/Latesch/Network-Tools.git
cd Network-Tools
```

### 2. Create a virtual environment

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (cmd)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

#### Local run (development)

```bash
flask run
```

By default, the app will be available at:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

#### Access from other devices (external access)

```bash
flask run --host=0.0.0.0
```

If your machine has IP `192.168.1.10`, the app will be available at:
👉 [http://192.168.1.10:5000](http://192.168.1.10:5000)

---

#### Run on a custom port

```bash
flask run --host=0.0.0.0 --port=8080
```

Now the server will run on port `8080`:
👉 [http://192.168.1.10:8080](http://192.168.1.10:8080)

---

## 📂 Project Structure

```text
Network-Tools/
│
├── app/
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── config.py             # Config (env, flaskenv)
│   │   ├── db.py                 # SQLAlchemy setup
│   │   └── extensions.py         # Flask-Login, SQLAlchemy, migrations
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py
│   │   └── log.py
│   │
│   ├── interfaces/               # External layer (controllers, repositories)
│   │   ├── controllers/          # Flask views (routes)
│   │   │   └── main_controller.py
│   │   └── repositories/         # Database repositories
│   │       ├── user_repo.py
│   │       └── logs_repo.py
│   │
│   ├── services/                 # Business logic
│   │   ├── user_service.py
│   │   ├── logs_service.py
│   │   └── nettools_service.py
│   │
│   └── app.py                    # Flask app factory (create_app)
│
├── migrations/                   # Alembic migrations (created after init)
│
├── tests/                        # Unit tests
│   ├── conftest.py
│   ├── test_logs_service.py
│   ├── test_nettools_service.py
│   └── test_user_service.py
│
├── instance/                     # Local data (ignored by Git)
│   └── nettools.db               # SQLite database
│
├── templates/                    # HTML templates (Jinja2)
├── static/                       # Static assets (CSS, JS)
├── .github/workflows/ci.yml      # CI/CD (lint + tests)
├── requirements/                 # Dependencies
│   ├── dev.txt
│   └── prod.txt
├── pyproject.toml                # black formatter config
├── .flake8                       # flake8 config
├── template.env                  # Template environment variables
├── .env                          # Environment variables
├── CONTRIBUTING.md               # Contributing guide
├── LICENSE                       # Apache 2.0 license
└── README.md                     # English documentation
```

---

## 🔑 Authentication and Roles

The app uses **Flask-Login** for authentication and session management.

* **Registration** is available at `/register`.
  Passwords are securely hashed before being stored in the database.

* **Login** is available at `/login`.
  Invalid credentials trigger an error notification.

* The interface dynamically updates buttons:

  * when logged in → username and **Logout** button;
  * when logged out → **Login** button.

### User roles

* **Guest (unauthenticated)** — can run network commands but has no access to logs or user management.
* **User** — can run commands, view, and manage log history.
* **Admin** — has all user rights plus user management.

---

## 🗄 Database

* All executed requests are stored in `nettools.db`.
* **Log** model stores:

  * `id`, `timestamp`, `action`, `host`, `params`, `status`, `output`.
* **User** model stores:

  * `id`, `timestamp`, `username`, `password_hash`, `role`.

---

## 🔁 Migrations

Migrations are implemented via **Flask-Migrate (Alembic)**:

```bash
flask db init      # initialize migrations
flask db migrate   # create migration
flask db upgrade   # apply changes
```

> Migrations are designed but not activated by default.

---

## 🧪 Testing

Tests are automatically executed via CI/CD on GitHub Actions.  
Run them locally:

```bash
pytest -v
```

Each test is **independent** — they don’t share state or data.  
Unit tests focus on small, isolated features.

---

## 📌 TODO (future improvements)

* Integration with xtermjs;
* Interactive live sessions;
* Ansible integration;
* Inventory database (auto-inventory);
* SNMP/NetFlow integration;
* Network diagram/topology visualization;
* OpenAPI.json.

---

## 🛠 Technologies

* Python 3.x
* Flask + Flask-Login + Flask-SQLAlchemy
* SQLAlchemy (SQLite)
* Bootstrap (via CDN)
* PythonPing / Subprocess
* Paramiko + telnetlib3
* Werkzeug (password hashing)

---

## 🤝 Contributing Guide

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🧩 License

This project is licensed under the **Apache License 2.0**.  
Copyright © 2025 **Late**

---

## 👤 Author

Author: **Late**
[Telegram @Latesch](https://t.me/Latesch)
