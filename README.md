# NetTools Web

Веб-приложение на **Flask** с сетевыми утилитами.  
Позволяет выполнять базовые сетевые команды через веб-интерфейс:

- `Ping` с настраиваемыми параметрами (количество пакетов, таймаут и др.);
- `Traceroute` с выбором опций;
- Цветовая индикация результата (успех, предупреждение, ошибка);
- Логирование всех запросов в базу данных SQLite;
- Просмотр истории и деталей каждого запроса;
- Возможность очистки истории или удаления отдельной записи;

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/username/nettools-web.git
cd nettools-web
````

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
```

Активация:

* Linux/macOS:

  ```bash
  source venv/bin/activate
  ```
* Windows (cmd):

  ```cmd
  venv\Scripts\activate
  ```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск приложения

```bash
flask run
```

После запуска приложение будет доступно по адресу:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📂 Структура проекта

```
nettools-web/
│
├── app.py              # Основное приложение Flask
├── nettools.py         # Логика ping и traceroute
├── hettools.db         # База данных (игнорируется в Git)
├── templates/          # HTML-шаблоны (Jinja2)
│   ├── index.html
│   ├── history.html
│   └── history_detail.html
├── static/             # Статические файлы (CSS, JS)
├── requirements.txt    # Список зависимостей
└── README.md           # Этот файл
```

---

## 🗄 Работа с базой данных

* Все выполненные запросы сохраняются в `nettools.db`
* Реализованы функции:

  * `create_db()` — создать базу, если она отсутствует
  * `delete_logs()` — очистить все записи
  * `delete_log(id)` — удалить отдельный лог

База данных **не загружается в Git** (см. `.gitignore`).

---

## 📌 TODO (идеи для развития)

* Добавить поддержку `nslookup` / `dig`
* Визуализировать `traceroute` (например, на карте или графе)
* Добавить авторизацию пользователей
* Сделать REST API для интеграции с другими системами
* Dockerfile для удобного деплоя

---

## 🛠 Технологии

* Python 3.x
* Flask
* SQLite
* Bootstrap (через CDN)
* PythonPing / Subprocess

---

## 👤 Автор

Проект создан для практики Python и Flask.
Автор: **Late** ([@github\Latesch](https://github.com/Latesch))