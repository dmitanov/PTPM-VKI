"""Класс вычислений/валидации (пункт «a»).

Оборачивает метод register_user, реализованный в Лабораторной работе №1,
и предоставляет его как единственный метод calculate.
"""

from my_project import register_user


class RegistrationCalculator:
    """Класс вычислений/валидации регистрации."""

    def calculate(
        self,
        login: str,
        password: str,
        password_confirmation: str
    ) -> tuple[bool, str]:
        """Вычисляет результат регистрации методом из ЛР1."""

        return register_user(login, password, password_confirmation)
