# NetTools Web

A **Flask**-based web application with built-in network utilities.
It allows you to run basic network commands through a web interface:

* **Network commands via web interface**:

  * `Ping` with configurable parameters (packet count, timeout, etc.);
  * `Traceroute` with customizable options;
  * `NSLookup` with record type and DNS server selection.
  * Device connection via **SSH** and **Telnet**.

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
  * access control:

    * guest → only execute commands,
    * authenticated user → execute commands and manage logs,
    * admin → all user features plus user management.

---

## 🚀 Installation and Run

### 1. Clone the repository

```bash
git clone https://github.com/Latesch/Network-Tools.git
cd Network-Tools
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate:

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
│   │   ├── config.py             # Configuration (.env, .flaskenv)
│   │   ├── db.py                 # SQLAlchemy database setup
│   │   └── extensions.py         # Flask extensions (db, login_manager, etc.)
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py
│   │   └── log.py
│   │
│   ├── interfaces/               # Interfaces (controllers, repositories)
│   │   ├── controllers/          # Flask routes
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
├── instance/                     # Local data (ignored by Git)
│   └── nettools.db               # SQLite database
│
├── templates/                    # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── connect.html
│   ├── history.html
│   ├── history_detail.html
│   └── users.html
│
├── static/                       # Static files (CSS, JS)
│   ├── apple-touch-icon.png
│   ├── favicon.png
│   ├── favicon.ico
│   └── style.css
│
├── requirements.txt              # Dependencies
├── .flaskenv                     # Flask environment variables
├── CONTRIBUTING.md               # Contribution guide
└── README.md                     # Project documentation
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

## 📌 TODO (future improvements)

* Integration with xtermjs;
* Interactive live sessions;
* Ansible integration;
* Inventory database (auto-inventory);
* SNMP/NetFlow integration;
* Network diagram/topology visualization;
* Jumphost support;
* OpenAPI.json.

---

## 🛠 Technologies

* Python 3.x
* Flask + Flask-Login
* SQLAlchemy (SQLite)
* Bootstrap (via CDN)
* PythonPing / Subprocess
* Paramiko + telnetlib3
* Werkzeug (password hashing)

---

## 🤝 Contributing Guide

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 👤 Author

This project was created for practicing Python and Flask.
Author: **Late**
[Telegram @Latesch](https://t.me/Latesch)
