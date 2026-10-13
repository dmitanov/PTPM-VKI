"""Лабораторная работа №3 — интеграционные тесты базы данных.

Проверяют реальное взаимодействие класса работы с БД и SQLite без заглушек.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from database import RegistrationDatabase

VALID_PASSWORD = "Пароль1!"


class TestRegistrationDatabaseIntegration(unittest.TestCase):
    """Совместная работа методов добавления, получения и удаления записей."""

    def setUp(self):
        self.database = RegistrationDatabase()

    def tearDown(self):
        self.database.close()

    def test_add_get_delete_roundtrip(self):
        """Добавленная запись читается и затем успешно удаляется."""
        self.assertIsNone(
            self.database.get_record("student_123", VALID_PASSWORD, VALID_PASSWORD)
        )

        self.database.add_record(
            "student_123", VALID_PASSWORD, VALID_PASSWORD, True, ""
        )
        self.assertEqual(
            self.database.get_record("student_123", VALID_PASSWORD, VALID_PASSWORD),
            (True, "")
        )

        self.assertTrue(
            self.database.delete_record(
                "student_123", VALID_PASSWORD, VALID_PASSWORD
            )
        )
        self.assertIsNone(
            self.database.get_record("student_123", VALID_PASSWORD, VALID_PASSWORD)
        )

    def test_record_is_identified_by_all_three_fields(self):
        """Запись находится только при полном совпадении логина, пароля и подтверждения."""
        self.database.add_record(
            "student_123", VALID_PASSWORD, "Пароль2!", False, "несовпадение"
        )

        self.assertIsNone(
            self.database.get_record("student_123", VALID_PASSWORD, VALID_PASSWORD)
        )
        self.assertEqual(
            self.database.get_record("student_123", VALID_PASSWORD, "Пароль2!"),
            (False, "несовпадение")
        )

    def test_add_record_overwrites_record_with_same_key(self):
        """Повторное добавление того же ключа обновляет результат."""
        self.database.add_record(
            "student_123", VALID_PASSWORD, VALID_PASSWORD, False, "старое"
        )
        self.database.add_record(
            "student_123", VALID_PASSWORD, VALID_PASSWORD, True, ""
        )

        self.assertEqual(
            self.database.get_record("student_123", VALID_PASSWORD, VALID_PASSWORD),
            (True, "")
        )

    def test_delete_record_returns_false_when_record_is_absent(self):
        """Удаление несуществующей записи возвращает False."""
        self.assertFalse(
            self.database.delete_record("ghost", VALID_PASSWORD, VALID_PASSWORD)
        )


if __name__ == "__main__":
    unittest.main()
