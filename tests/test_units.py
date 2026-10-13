"""Лабораторная работа №3 — модульные тесты изоляции компонентов.

Проверяют каждый класс по отдельности. Пользовательский ввод и вывод
подменяются тестовыми заглушками из unittest.mock.
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from database import RegistrationDatabase
from notification_service import EmailNotificationService, NotificationService
from registration_calculator import RegistrationCalculator
from user_interface import ConsoleUserInterface, UserInterface

VALID_PASSWORD = "Пароль1!"


class TestConsoleUserInterface(unittest.TestCase):
    """Изоляция ввода данных пользователя через заглушку input."""

    @patch("builtins.input", side_effect=["login1", "pass1", "pass2"])
    def test_reads_login_password_and_confirmation_in_order(self, mocked_input):
        """Метод возвращает три введённых значения именно в требуемом порядке."""
        data = ConsoleUserInterface().get_registration_data()

        self.assertEqual(data, ("login1", "pass1", "pass2"))
        self.assertEqual(mocked_input.call_count, 3)


class TestAbstractInterfaces(unittest.TestCase):
    """Абстрактные базовые классы не могут быть созданы напрямую."""

    def test_user_interface_cannot_be_instantiated(self):
        """UserInterface — интерфейс, прямое создание запрещено."""
        with self.assertRaises(TypeError):
            UserInterface()

    def test_notification_service_cannot_be_instantiated(self):
        """NotificationService — интерфейс, прямое создание запрещено."""
        with self.assertRaises(TypeError):
            NotificationService()


class TestEmailNotificationService(unittest.TestCase):
    """Изоляция отправки данных сторонней зависимости через заглушку print."""

    @patch("builtins.print")
    def test_imitates_sending_result_line(self, mocked_print):
        """Метод имитирует передачу строки-результата на внешний сервер."""
        EmailNotificationService().send_result(
            "Регистрация student_123: успешно"
        )

        mocked_print.assert_called_once_with(
            "[EMAIL] Отправка результата на внешний сервер: "
            "Регистрация student_123: успешно"
        )


class TestRegistrationCalculator(unittest.TestCase):
    """Класс вычислений делегирует работу методу из ЛР1."""

    def test_returns_success_for_valid_data(self):
        """Корректные данные дают успешный результат."""
        self.assertEqual(
            RegistrationCalculator().calculate(
                "student_123", VALID_PASSWORD, VALID_PASSWORD
            ),
            (True, "")
        )

    def test_returns_error_for_invalid_data(self):
        """Некорректные данные дают результат с сообщением об ошибке."""
        self.assertEqual(
            RegistrationCalculator().calculate(
                "admin", VALID_PASSWORD, VALID_PASSWORD
            ),
            (False, "Логин находится в черном списке")
        )


class TestRegistrationDatabaseIsolation(unittest.TestCase):
    """Изоляция работы класса БД."""

    def test_close_releases_connection(self):
        """После закрытия соединение больше не принимает запросы."""
        database = RegistrationDatabase()
        database.close()

        with self.assertRaises(sqlite3.ProgrammingError):
            database.get_record("student_123", VALID_PASSWORD, VALID_PASSWORD)

    def test_uses_provided_file_path_and_persists_data(self):
        """Указанный файл БД сохраняет данные между подключениями."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            db_path = str(Path(temporary_directory) / "registrations.db")

            database = RegistrationDatabase(db_path)
            database.add_record(
                "student_123", VALID_PASSWORD, VALID_PASSWORD, True, ""
            )
            database.close()

            reopened = RegistrationDatabase(db_path)
            self.assertEqual(
                reopened.get_record(
                    "student_123", VALID_PASSWORD, VALID_PASSWORD
                ),
                (True, "")
            )
            reopened.close()


if __name__ == "__main__":
    unittest.main()
