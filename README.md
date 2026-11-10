# Лабораторная работа №5. Парсинг и тестирование на Python

Проект собирает данные о ноутбуках Apple с каталога
[biggeek.ru/catalog/noutbuki-apple](https://biggeek.ru/catalog/noutbuki-apple),
сохраняет их в SQLite и проверяется unit-тестами.

## Возможности

- `BigGeekParser` — загрузка страницы через `requests` с `User-Agent`,
  разбор через `BeautifulSoup`, извлечение ID, названия и цены товара.
- `BigGeekParser.parse_page(url)` — скачать и разобрать страницу.
- `BigGeekParser.parse_html(html)` — разобрать готовый HTML (для тестов).
- `BigGeekParser.save_to_db(data, repository)` — сохранить товары в БД.
- `DatabaseRepository` — работа с таблицей `comments` в SQLite:
  `add`, `get_by_id`, `get_by_name`, `update`, `delete`, `get_all`.
- Валидация типов и длины строк: `name` до 256 символов, `message` до 8096.
- Пользовательские исключения: `ValidationError`, `DuplicateIdError`,
  `CommentNotFoundError`.
- Тесты на `unittest`; парсер проверяется на живом сайте BigGeek (нужен интернет).
- `demo.py` — простой пример в стиле `requests` + `bs4`, как в методичке.

## Структура проекта

```
lab5_mitanov/
├── .gitignore
├── README.md
├── requirements.txt
├── demo.py
├── src/
│   ├── __init__.py
│   ├── database.py
│   └── parser.py
└── tests/
    ├── test_database.py
    └── test_parser.py
```

## Установка

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Запуск

Простой пример парсинга каталога:

```powershell
.\venv\Scripts\python.exe demo.py
```

Пример вывода:

```text
Ноутбук Apple MacBook Neo 13" MHFA4 (A18 Pro 6-Core, GPU 5-Core, 8GB, 256GB) (Серебристый | Silver) - 68 990 ₽
Ноутбук Apple MacBook Pro 14" с нанотекстурой, кастомный (M5 10-Core, GPU 10-Core, 32GB, 2TB) (Серебристый | Silver) - 311 990 ₽
...
Всего товаров: 24
```

Использование класса парсера:

```python
from src.database import DatabaseRepository
from src.parser import BigGeekParser

repo = DatabaseRepository("biggeek.db")
parser = BigGeekParser()

products = parser.parse_page()
parser.save_to_db(products, repo)

print(repo.get_by_id(37079))
repo.close()
```

## Формат разобранных данных

`parse_page` и `parse_html` возвращают список словарей:

```python
{
    "id": 37079,
    "name": "Ноутбук Apple MacBook Neo 13\" MHFA4 ...",
    "price": "68 990 ₽",
    "message": "68 990 ₽",
    "url": "https://biggeek.ru/products/noutbuk-apple-macbook-neo-13-mhfa4",
}
```

Поле `message` дублирует `price` для совместимости с таблицей `comments`:
ID товара записывается в `id`, название — в `name`, цена — в `message`.

## Селекторы BigGeek

| Данные | Селектор |
|---|---|
| Карточка товара | `div.catalog-card` |
| Название | `a.catalog-card__title` |
| Цена | `a.catalog-card__price b.cart-modal-count` |
| ID товара | `[data-product-id]` |

## Запуск тестов

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Ожидаемый результат: `Ran 19 tests` и `OK`.

Тесты парсера обращаются к живому сайту BigGeek, поэтому для них нужен
доступ в интернет. Количество товаров на странице может меняться.
