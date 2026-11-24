# UI-тестирование Simple Calculator с Page Object Model

Проект демонстрирует автоматизированное тестирование веб-приложения Simple Calculator с помощью Selenium WebDriver, unittest и паттерна Page Object Model (POM).

Цель: показать разделение локаторов и действий с интерфейсом от тестовой логики. Тесты работают с публичными методами `CalculatorPage` и не обращаются к `driver.find_element` напрямую.

## Структура проекта

```text
calculator_tests/
├── .gitignore
├── README.md
├── requirements.txt
├── pages/
│   ├── __init__.py
│   └── calculator_page.py
└── tests/
    ├── __init__.py
    └── test_calculator.py
```

## Подготовка окружения

```bash
python -m venv venv
```

Активация:

```cmd
venv\Scripts\activate
```

```bash
source venv/bin/activate
```

Установка зависимостей:

```bash
python -m pip install --upgrade pip
python -m pip install selenium
python -m pip freeze > requirements.txt
```

Selenium 4 автоматически подбирает драйвер через Selenium Manager. Дополнительно скачивать `msedgedriver` или `chromedriver` вручную не требуется.

## Запуск тестов

Из корня проекта `calculator_tests`:

```bash
python -m unittest discover -s tests
```

По умолчанию используется Microsoft Edge в headless-режиме. Переменные окружения:

| Переменная | Значение по умолчанию | Описание |
| --- | --- | --- |
| `BROWSER` | `edge` | `edge`, `chrome` или `firefox` |
| `HEADLESS` | `true` | `false` показывает окно браузера |

Пример для Windows:

```cmd
set BROWSER=chrome
set HEADLESS=false
python -m unittest discover -s tests
```

Пример для Linux/macOS:

```bash
export BROWSER=chrome
export HEADLESS=false
python -m unittest discover -s tests
```

## Покрытие тестами

- начальное состояние калькулятора;
- сложение, вычитание, умножение, деление;
- десятичные, отрицательные и большие числа;
- деление на ноль: `10 / 0` и `0 / 0` отображаются как `null`, поскольку Angular 1.0.7 не выводит `Infinity` и `NaN` через интерполяцию;
- кнопки `+1` и `-1` для обоих операндов;
- проверка доступного списка операций.

Всего: 15 независимых тестов. Браузер создаётся в `setUp()`, сессия закрывается в `tearDown()`.

## Ограничение тестируемого приложения

На странице [Simple Calculator](https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/) выпадающий список содержит только операции `+`, `-`, `*`, `/`. Операция `**` в интерфейсе отсутствует, поэтому тест `test_power_operation_is_not_available_in_application` фиксирует фактический список операций. Попытка выбрать `**` через UI невозможна без изменения DOM страницы, что не является честным UI-тестом.

## Page Object Model

`CalculatorPage` хранит локаторы в защищённых переменных в виде кортежей `(By.CSS_SELECTOR, ...)` и предоставляет методы:

- `enter_first_number(num)`;
- `enter_second_number(num)`;
- `select_operation(op)`;
- `increment_first()`, `decrement_first()`;
- `increment_second()`, `decrement_second()`;
- `get_result_text()`, `get_calculated_value()`, `calculate(...)`.

Такой подход упрощает поддержку: при изменении разметки достаточно обновить локатор в одном месте.
