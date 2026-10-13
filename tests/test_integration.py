"""Лабораторная работа №3 — интеграционные тесты.

Проверяют совместную работу контроллера с реальной базой данных SQLite,
классом вычислений из ЛР1 и классом взаимодействия с пользователем.
Пользовательский ввод и отправка данных на внешний сервер подменяются
тестовыми заглушками из unittest.mock.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from controller import Controller
from database import RegistrationDatabase
from registration_calculator import RegistrationCalculator
from user_interface import ConsoleUserInterface

VALID_PASSWORD = "Пароль1!"


class TestControllerIntegration(unittest.TestCase):
    """Сквозной сценарий контроллера на реальной базе данных."""

    def setUp(self):
        self.database = RegistrationDatabase()
        self.notification = MagicMock()

    def tearDown(self):
        self.database.close()

    @patch(
        "builtins.input",
        side_effect=["student_123", VALID_PASSWORD, VALID_PASSWORD]
    )
    def test_full_scenario_saves_new_record_and_sends_result(self, mocked_input):
        """Новые корректные данные вычисляются, сохраняются и отправляются."""
        controller = Controller(
            RegistrationCalculator(),
            self.database,
            ConsoleUserInterface(),
            self.notification
        )

        result = controller.process_registration()

        self.assertEqual(result, (True, ""))
        self.assertEqual(
            self.database.get_record(
                "student_123", VALID_PASSWORD, VALID_PASSWORD
            ),
            (True, "")
        )
        self.notification.send_result.assert_called_once_with(
            "Регистрация student_123: успешно"
        )
        self.assertEqual(mocked_input.call_count, 3)

    @patch(
        "builtins.input",
        side_effect=["admin", VALID_PASSWORD, VALID_PASSWORD]
    )
    def test_full_scenario_persists_failed_registration(self, mocked_input):
        """Отклонённая регистрация сохраняется вместе с сообщением об ошибке."""
        controller = Controller(
            RegistrationCalculator(),
            self.database,
            ConsoleUserInterface(),
            self.notification
        )

        result = controller.process_registration()

        self.assertEqual(result, (False, "Логин находится в черном списке"))
        self.assertEqual(
            self.database.get_record("admin", VALID_PASSWORD, VALID_PASSWORD),
            (False, "Логин находится в черном списке")
        )
        self.notification.send_result.assert_called_once_with(
            "Регистрация admin: ошибка — Логин находится в черном списке"
        )

    @patch(
        "builtins.input",
        side_effect=["student_123", VALID_PASSWORD, VALID_PASSWORD]
    )
    def test_full_scenario_reuses_cached_record(self, mocked_input):
        """При наличии записи результат берётся из БД, вычисление не вызывается."""
        self.database.add_record(
            "student_123", VALID_PASSWORD, VALID_PASSWORD, False, "из кэша"
        )
        calculator = MagicMock()
        controller = Controller(
            calculator,
            self.database,
            ConsoleUserInterface(),
            self.notification
        )

        result = controller.process_registration()

        self.assertEqual(result, (False, "из кэша"))
        calculator.calculate.assert_not_called()
        self.notification.send_result.assert_called_once_with(
            "Регистрация student_123: ошибка — из кэша"
        )

    @patch(
        "builtins.input",
        side_effect=[
            "student_123", VALID_PASSWORD, VALID_PASSWORD,
            "student_123", VALID_PASSWORD, VALID_PASSWORD
        ]
    )
    def test_repeated_scenario_reads_result_from_database(self, mocked_input):
        """Повторный вызов не пересчитывает уже сохранённую запись."""
        controller = Controller(
            RegistrationCalculator(),
            self.database,
            ConsoleUserInterface(),
            self.notification
        )

        first_result = controller.process_registration()
        second_result = controller.process_registration()

        self.assertEqual(first_result, (True, ""))
        self.assertEqual(second_result, (True, ""))
        self.assertEqual(self.notification.send_result.call_count, 2)


if __name__ == "__main__":
    unittest.main()
