"""
Лабораторная работа №2 — юнит-тесты для кода Лабораторной работы №1.

Тестируемые модули:
  src/my_project.py — точка входа регистрации пользователя, маскирование пароля;
  src/validator.py  — правила валидации логина, пароля и самой регистрации.

Каждый тест проверяет одно правило из бизнес-требований ЛР1 и не зависит
от результатов остальных тестов.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from my_project import mask_password, register_user
from validator import validate_login, validate_password, validate_registration

VALID_PASSWORD = "Пароль1!"


class TestValidateLogin(unittest.TestCase):
    """Проверка правил валидации логина."""

    def test_accepts_username_with_latin_letters_digits_and_underscore(self):
        """Логин из 5 и более латинских букв, цифр и подчёркивания корректен."""
        self.assertEqual(validate_login("student_123"), (True, ""))

    def test_accepts_username_of_exactly_five_characters(self):
        """Ровно 5 символов — минимально допустимая длина логина."""
        self.assertEqual(validate_login("stude"), (True, ""))

    def test_accepts_login_formatted_as_phone_number(self):
        """Логин по маске +x-xxx-xxx-xxxx распознаётся как телефон."""
        self.assertEqual(validate_login("+7-999-123-4567"), (True, ""))

    def test_rejects_phone_number_that_does_not_match_mask(self):
        """Сплошной номер телефона без разделителей не соответствует маске."""
        result, message = validate_login("+79991234567")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_accepts_login_formatted_as_email(self):
        """Корректный e-mail принимается в качестве логина."""
        self.assertEqual(validate_login("student@example.com"), (True, ""))

    def test_accepts_email_with_subdomain_and_plus_tag(self):
        """Допустимы поддомены и тег в локальной части e-mail."""
        self.assertEqual(validate_login("student+lab@mail.example.com"), (True, ""))

    def test_rejects_email_without_dot_in_domain(self):
        """Домен без точки и домена верхнего уровня не является e-mail."""
        result, message = validate_login("student@example")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_email_with_consecutive_dots_in_local_part(self):
        """Локальная часть e-mail не может содержать две точки подряд."""
        result, message = validate_login("stu..dent@example.com")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_email_with_consecutive_dots_in_domain(self):
        """Домен не может содержать две точки подряд: это невалидный адрес."""
        result, message = validate_login("student@exam..ple.com")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_email_with_hyphen_at_start_of_domain(self):
        """Домен не может начинаться с дефиса."""
        result, message = validate_login("student@-example.com")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_email_with_one_letter_top_level_domain(self):
        """Домен верхнего уровня короче двух букв невалиден."""
        result, message = validate_login("student@example.c")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_empty_login(self):
        """Пустая строка отклоняется с отдельным сообщением."""
        self.assertEqual(validate_login(""), (False, "Логин не может быть пустым"))

    def test_rejects_login_that_is_not_a_string(self):
        """Число вместо логина отклоняется, а не приводится к строке неявно."""
        self.assertEqual(validate_login(12345), (False, "Логин должен быть строкой"))

    def test_rejects_username_shorter_than_five_characters(self):
        """Логин из 4 символов короче минимально допустимых 5."""
        self.assertEqual(
            validate_login("abcd"),
            (False, "Логин должен содержать минимум 5 символов")
        )

    def test_rejects_username_with_cyrillic_characters(self):
        """Логин должен содержать только латиницу, цифры и подчёркивание."""
        result, message = validate_login("студент")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_username_with_space(self):
        """Пробел не входит в разрешённый набор символов логина."""
        result, message = validate_login("user name")
        self.assertFalse(result)
        self.assertIn("Логин должен содержать только", message)

    def test_rejects_login_from_blacklist(self):
        """Логин из чёрного списка блокируется."""
        self.assertEqual(
            validate_login("admin"),
            (False, "Логин находится в черном списке")
        )

    def test_rejects_blacklisted_login_regardless_of_letter_case(self):
        """Проверка чёрного списка не должна зависеть от регистра."""
        self.assertEqual(
            validate_login("ADMIN"),
            (False, "Логин находится в черном списке")
        )


class TestValidatePassword(unittest.TestCase):
    """Проверка правил валидации пароля."""

    def test_accepts_password_meeting_all_requirements(self):
        """Кириллица в обоих регистрах, цифра и спецсимвол — пароль корректен."""
        self.assertEqual(validate_password(VALID_PASSWORD), (True, ""))

    def test_accepts_password_of_exactly_seven_characters(self):
        """Ровно 7 символов — минимально допустимая длина пароля."""
        self.assertEqual(validate_password("Пар0ль!"), (True, ""))

    def test_accepts_password_with_letter_yo(self):
        """Буквы «Ё» и «ё» входят в разрешённый алфавит."""
        self.assertEqual(validate_password("Ёжик123!"), (True, ""))

    def test_rejects_password_that_is_not_a_string(self):
        """Число вместо пароля отклоняется."""
        self.assertEqual(
            validate_password(1234567),
            (False, "Пароль должен быть строкой")
        )

    def test_rejects_password_shorter_than_seven_characters(self):
        """Пароль длиной 5 символов короче минимально допустимых 7."""
        self.assertEqual(
            validate_password("Пар1!"),
            (False, "Пароль должен содержать минимум 7 символов")
        )

    def test_rejects_password_with_latin_letters(self):
        """Латиница запрещена: пароль должен состоять из кириллицы, цифр и спецсимволов."""
        result, message = validate_password("Password1!")
        self.assertFalse(result)
        self.assertIn("Пароль может содержать только", message)

    def test_rejects_password_with_space(self):
        """Пробел не входит в разрешённый набор символов пароля."""
        result, message = validate_password("Пароль 1!")
        self.assertFalse(result)
        self.assertIn("Пароль может содержать только", message)

    def test_rejects_password_without_uppercase_letter(self):
        """Требование обязательной заглавной буквы."""
        self.assertEqual(
            validate_password("пароль1!"),
            (False, "Пароль должен содержать хотя бы одну заглавную букву")
        )

    def test_rejects_password_without_lowercase_letter(self):
        """Требование обязательной строчной буквы."""
        self.assertEqual(
            validate_password("ПАРОЛЬ1!"),
            (False, "Пароль должен содержать хотя бы одну строчную букву")
        )

    def test_rejects_password_without_digit(self):
        """Требование обязательной цифры."""
        self.assertEqual(
            validate_password("Пароль!"),
            (False, "Пароль должен содержать хотя бы одну цифру")
        )

    def test_rejects_password_without_special_character(self):
        """Требование обязательного специального символа."""
        self.assertEqual(
            validate_password("Пароль1"),
            (False, "Пароль должен содержать хотя бы один специальный символ")
        )

    def test_rejects_password_with_only_digits_and_special_characters(self):
        """Пароль без букв отклоняется на проверке заглавной."""
        self.assertEqual(
            validate_password("1234567!"),
            (False, "Пароль должен содержать хотя бы одну заглавную букву")
        )


class TestValidateRegistration(unittest.TestCase):
    """Проверка сводного сценария регистрации."""

    def test_registers_user_with_valid_username_and_password(self):
        """Корректная тройка данных успешно проходит регистрацию."""
        self.assertEqual(
            validate_registration("student_123", VALID_PASSWORD, VALID_PASSWORD),
            (True, "")
        )

    def test_registers_user_with_phone_number_as_login(self):
        """Регистрация с телефоном в качестве логина разрешена."""
        self.assertEqual(
            validate_registration("+7-999-123-4567", VALID_PASSWORD, VALID_PASSWORD),
            (True, "")
        )

    def test_reports_login_error_before_password_error(self):
        """Если неверны и логин, и пароль, приоритет у ошибки логина."""
        self.assertEqual(
            validate_registration("admin", "пароль", "пароль"),
            (False, "Логин находится в черном списке")
        )

    def test_reports_password_error_when_login_is_valid(self):
        """При корректном логине возвращается ошибка пароля."""
        self.assertEqual(
            validate_registration("student_123", "пароль1!", VALID_PASSWORD),
            (False, "Пароль должен содержать хотя бы одну заглавную букву")
        )

    def test_rejects_mismatched_password_confirmation(self):
        """Пароль и его подтверждение должны совпадать."""
        self.assertEqual(
            validate_registration("student_123", VALID_PASSWORD, "Пароль2!"),
            (False, "Пароль и подтверждение пароля не совпадают")
        )

    def test_rejects_empty_password_confirmation(self):
        """Пустое подтверждение не совпадает с паролем."""
        self.assertEqual(
            validate_registration("student_123", VALID_PASSWORD, ""),
            (False, "Пароль и подтверждение пароля не совпадают")
        )


class TestMaskPassword(unittest.TestCase):
    """Проверка детерминированного маскирования пароля в логах."""

    def test_produces_same_mask_for_same_password(self):
        """Одинаковые пароли должны давать одинаковую маску."""
        self.assertEqual(
            mask_password(VALID_PASSWORD),
            mask_password(VALID_PASSWORD)
        )

    def test_produces_different_masks_for_different_passwords(self):
        """Разные пароли должны давать разные маски."""
        self.assertNotEqual(
            mask_password(VALID_PASSWORD),
            mask_password("Пароль2!")
        )

    def test_mask_is_hexadecimal_string_of_sha256_length(self):
        """Маска — 64 шестнадцатеричных символа (SHA-256)."""
        mask = mask_password(VALID_PASSWORD)
        self.assertEqual(len(mask), 64)
        self.assertTrue(all(char in "0123456789abcdef" for char in mask))

    def test_mask_does_not_contain_plain_password(self):
        """Пароль в открытом виде не попадает в маску."""
        self.assertNotIn(VALID_PASSWORD, mask_password(VALID_PASSWORD))


class TestRegisterUser(unittest.TestCase):
    """Проверка публичной функции регистрации из ЛР1."""

    def test_returns_success_and_empty_message_for_valid_data(self):
        """Успешная регистрация возвращает True и пустое сообщение."""
        self.assertEqual(
            register_user("student_123", VALID_PASSWORD, VALID_PASSWORD),
            (True, "")
        )

    def test_returns_error_message_for_blacklisted_login(self):
        """Причину отказа в регистрации метод возвращает вторым элементом."""
        self.assertEqual(
            register_user("admin", VALID_PASSWORD, VALID_PASSWORD),
            (False, "Логин находится в черном списке")
        )

    def test_returns_error_instead_of_exception_for_non_string_password(self):
        """
        Регрессионный тест: нестроковый пароль не должен приводить к аварийному
        завершению — метод обязан вернуть сообщение об ошибке валидации.
        """
        try:
            result = register_user("student_123", None, None)
        except Exception as error:
            self.fail(
                f"Метод упал с {type(error).__name__}: {error} вместо "
                f"возврата кортежа с сообщением об ошибке"
            )
        self.assertEqual(result, (False, "Пароль должен быть строкой"))

    def test_returns_error_instead_of_exception_for_non_string_login(self):
        """Нестроковый логин обрабатывается штатно."""
        self.assertEqual(
            register_user(None, VALID_PASSWORD, VALID_PASSWORD),
            (False, "Логин должен быть строкой")
        )

    def test_returns_error_for_non_string_password_confirmation(self):
        """Нестроковое подтверждение пароля считается несовпадением."""
        self.assertEqual(
            register_user("student_123", VALID_PASSWORD, 1234567),
            (False, "Пароль и подтверждение пароля не совпадают")
        )


if __name__ == "__main__":
    unittest.main()
