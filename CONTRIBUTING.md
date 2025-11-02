# 🤝 Contributing Guide

---

## 🇷🇺 Руководство по вкладу в проект

Спасибо, что хотите помочь развивать **NetTools Web**! 🚀
Мы стремимся к чистому, стабильному и тестируемому коду.

---

### ⚙️ Основные правила

1. **Создавайте отдельные ветки** для каждой задачи:

   ```bash
   git checkout -b feature/my-feature
   git checkout -b fix/my-bug
   ```

2. **Перед коммитом** убедитесь, что код форматирован и проходит линтеры:

   ```bash
   black .
   flake8
   ```

3. **Один коммит — одно изменение.**
   Это помогает отслеживать, что и зачем было сделано.

   ```text
   feat: add jumphost SSH support
   fix: correct IP validation in nettools_service
   docs: update README with test and CI info
   ```

4. **Не коммитьте "мусорные" фиксы**, вроде “fix lint”, “update main.py”.
   Объединяйте такие исправления перед пушем с помощью:

   ```bash
   git rebase -i HEAD~N
   ```

---

### 🧪 Тестирование

* Все новые функции должны иметь **юнит-тесты**.
* Тесты пишутся в папке `tests/` — один тест = одна проверяемая фича.
* Для запуска:

  ```bash
  pytest -v
  ```

* Тесты **изолированы** и не влияют на реальную базу (`sqlite:///:memory:`).

---

### 🧰 Линтеры и стиль кода

Проект следует стандартам **PEP8 + Black + Flake8**
Конфигурация хранится в `.flake8` и `pyproject.toml`.

Используемые инструменты:

| Инструмент              | Назначение                             |
| ----------------------- | -------------------------------------- |
| **black**               | автоформатирование кода                |
| **flake8**              | общий анализ стиля                     |
| **flake8-import-order** | порядок импортов (Google style)        |
| **pep8-naming**         | проверка имён переменных и функций     |
| **flake8-quotes**       | проверка использования двойных кавычек |

---

### 🔁 CI/CD

* Репозиторий использует **GitHub Actions** для автоматической проверки кода.
* При каждом push или PR выполняются:

  1. **Lint stage** — проверка стиля `black` и `flake8`.
  2. **Test stage** — выполнение `pytest` в изолированном окружении.

Чтобы локально проверить то же, что и на CI:

```bash
black --check .
flake8
pytest -v
```

---

### 🔀 Pull Requests

1. Сделайте fork репозитория.
2. Внесите изменения в отдельной ветке.
3. Убедитесь, что всё проходит тесты и линтеры.
4. Откройте Pull Request в `main` с кратким, но информативным описанием.

---

## 🇬🇧 English Contributing Guide

Thank you for contributing to **NetTools Web**! 🚀
We value clean, stable, and testable code.

---

### ⚙️ Basic Rules

1. **Create a separate branch** for each feature or fix:

   ```bash
   git checkout -b feature/my-feature
   git checkout -b fix/my-bug
   ```

2. **Before committing**, make sure your code is formatted and linted:

   ```bash
   black .
   flake8
   ```

3. **One commit = one meaningful change.**
   Examples:

   ```text
   feat: add SSH jumphost support
   fix: correct hostname validation
   docs: update README with test section
   ```

4. Avoid meaningless commits like *“fix lint”* or *“update main.py”* —
   instead, squash them with:

   ```bash
   git rebase -i HEAD~N
   ```

---

### 🧪 Testing

* Each new feature must include **unit tests**.
* Tests are located under `tests/` — one function per case.
* To run tests locally:

  ```bash
  pytest -v
  ```

* Tests are **fully isolated** (in-memory SQLite).

---

### 🧰 Linters and Code Style

The project uses **PEP8 + Black + Flake8** standards.

Linters used:

| Tool                    | Purpose                     |
| ----------------------- | --------------------------- |
| **black**               | automatic code formatting   |
| **flake8**              | style analysis              |
| **flake8-import-order** | import order (Google style) |
| **pep8-naming**         | name validation             |
| **flake8-quotes**       | enforce double quotes       |

---

### 🇬🇧 🔁 CI/CD

* CI/CD runs via **GitHub Actions**.
* Each commit triggers:

  1. **Lint stage** — `flake8` and `black --check`
  2. **Test stage** — `pytest` with isolated SQLite DB

To verify locally:

```bash
black --check .
flake8
pytest -v
```

---

### 🇬🇧 🔀 Pull Requests

1. Fork the repo and create a new branch.
2. Implement your changes.
3. Ensure tests and linters pass.
4. Open a PR to `main` with a clear description.
