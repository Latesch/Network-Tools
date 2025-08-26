# NetTools Web

Веб-приложение на **Flask** с сетевыми утилитами.
Позволяет выполнять базовые сетевые команды через веб-интерфейс:

* `Ping` с настраиваемыми параметрами (количество пакетов, таймаут и др.);
* `Traceroute` с выбором опций;
* Цветовая индикация результата (успех, предупреждение, ошибка);
* Логирование всех запросов в базу данных SQLite;
* Просмотр истории и деталей каждого запроса;
* Удаление отдельных логов или всей истории;
* Авторизация пользователей (Flask-Login) с хэшированием паролей;
* Регистрация новых пользователей через веб-интерфейс;
* Роли пользователей (обычный пользователь / администратор);
* Разграничение доступа:

  * гость → только выполнение команд;
  * авторизованный пользователь → выполнение команд + просмотр/управление логами.

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/Latesch/Network-Tools.git
cd Network-Tools
```

### 2. Создание виртуального окружения

```bash
python3 -m venv .venv
```

Активация:

* Linux/macOS:

  ```bash
  source .venv/bin/activate
  ```
* Windows (cmd):

  ```cmd
  .venv\Scripts\activate
  ```
### 3. Обновление pip

```bash
pip install --upgrade pip
```

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 5. Запуск приложения

#### Локальный запуск (разработка)

```bash
flask run
```

По умолчанию приложение будет доступно по адресу:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

#### Доступ с других устройств (внешний доступ)

```bash
flask run --host=0.0.0.0
```

Если твой компьютер в сети имеет IP `192.168.1.10`, то приложение будет доступно по адресу:
👉 [http://192.168.1.10:5000](http://192.168.1.10:5000)

---

#### Запуск на кастомном порту

```bash
flask run --host=0.0.0.0 --port=8080
```

Теперь сервер будет доступен на порту `8080`.
👉 [http://192.168.1.10:8080](http://192.168.1.10:8080)


---

## 📂 Структура проекта

```
Network-Tools/
│
├── nettools/
│   ├── app.py              # Фабрика Flask-приложения (create_app)
│   ├── extensions.py       # Подключение расширений (db, login_manager и др.)
│   ├── models.py           # SQLAlchemy модели (User, Log)
│   ├── view.py             # Основные маршруты (Blueprint "main")
│   └── nettools.py         # Логика ping/traceroute/ssh/telnet
│
├── instance/               # Локальные данные (игнорируется в Git)
│   └── nettools.db         # База данных SQLite
│
├── templates/              # HTML-шаблоны (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── connect.html
│   ├── history.html
│   └── history_detail.html
│
├── static/                 # Статические файлы (CSS, JS)
│   ├── apple-touch-icon.png
│   ├── favicon.png
│   ├── favicon.ico
│   └── style.css
│
├── requirements.txt        # Список зависимостей
├── README.md               # Документация проекта
└── run.py                  # Точка входа (flask run → create_app())
```

---

## 🔑 Авторизация и роли

Используется библиотека **Flask-Login**.

Регистрация пользователей производится на странице /register (пароли сохраняются в виде хэша).

👉 Если ввести неверный логин или пароль, система выдаст уведомление.
👉 Кнопка входа/выхода динамически меняется в зависимости от состояния.

---

## 🗄 Работа с базой данных

* Все выполненные запросы сохраняются в `nettools.db`.
* Модель **Log** хранит:

  * `id`, `timestamp`, `action`, `host`, `params`, `status`, `output`.
* Модель **User** хранит:

  * `id`, `timestamp`, `username`, `password_hash`, `role`.

---

## 📌 TODO (идеи для развития)

* Возможность подключения xtermjs;
* Создание живого-подключения (сессии);
* Интеграция Ansible;
* Создание инвентарной базы (Автоинвентаризация);
* Интеграция SNMP/NetFlow;
* Возможность рисования схем/топологий;
* Решение проблемы с Jumphost;
* OpenAPI.json

---

## 🛠 Технологии

* Python 3.x
* Flask + Flask-Login
* SQLAlchemy (SQLite)
* Bootstrap (через CDN)
* PythonPing / Subprocess
* Paramiko + telnetlib
* Werkzeug (для хэширования паролей)

---

## 🤝 Contributing guide

[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 👤 Автор

Проект создан для практики Python и Flask.
Автор: **Late**
[Telegram @Latesch](https://t.me/Latesch)
