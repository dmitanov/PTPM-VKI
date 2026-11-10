# Лабораторная работа №5. Парсинг и тестирование на Python

Проект демонстрирует автоматизированный сбор данных с HTML-страницы и их
сохранение в SQLite, а также покрытие модулей unit-тестами.

## Возможности

- `DatabaseRepository` — работа с таблицей `comments` в SQLite:
  `add`, `get_by_id`, `get_by_name`, `update`, `delete`, `get_all`.
- Валидация типов и длины строк: `name` до 256 символов, `message` до 8096.
- Пользовательские исключения: `ValidationError`, `DuplicateIdError`,
  `CommentNotFoundError`.
- `ForumParser` — загрузка страницы через `requests` с `User-Agent`,
  разбор через `BeautifulSoup`, извлечение ID, автора и текста поста
  с сохранением внутренней HTML-разметки.
- `ForumParser.save_to_db` — сохранение результатов парсинга в репозиторий.
- Тесты на `unittest` с локальной HTML-фикстурой (без зависимости от сети).

## Структура проекта

```
lab5_mitanov/
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── database.py
│   └── parser.py
└── tests/
    ├── fixtures/
    │   └── forum_page.html
    ├── test_database.py
    └── test_parser.py
```

## Установка

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск тестов

```powershell
python -m unittest discover -s tests -v
```

## Пример использования

```python
from src.database import DatabaseRepository
from src.parser import ForumParser

repo = DatabaseRepository("forum.db")
parser = ForumParser()

posts = parser.parse_page("https://example.com/forum/thread/1")
parser.save_to_db(posts, repo)

print(repo.get_by_name("alice"))
repo.close()
```

## Формат разобранных данных

`parse_page` и `parse_html` возвращают список словарей:

```python
{"id": 101, "name": "alice", "message": "<p>Привет, <strong>мир</strong>!</p>"}
```

Парсер поддерживает типовые селекторы контейнеров (`.post`, `.message`,
`.comment`), авторов (`.author`, `.username`, `.login`, `[data-author]`) и
текста (`.message-body`, `.post-content`, `.message-content` и др.).
