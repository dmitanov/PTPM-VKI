"""Класс взаимодействия с пользователем (пункт «c»).

Интерфейс задан абстрактным базовым классом UserInterface.
Конкретная реализация ConsoleUserInterface читает данные из консоли.
"""

from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Абстрактный интерфейс получения данных от пользователя."""

    @abstractmethod
    def get_registration_data(self) -> tuple[str, str, str]:
        """Возвращает тройку (логин, пароль, подтверждение пароля)."""

        raise NotImplementedError


class ConsoleUserInterface(UserInterface):
    """Реализация ввода данных через консоль."""

    def get_registration_data(self) -> tuple[str, str, str]:
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        password_confirmation = input("Подтвердите пароль: ")

        return login, password, password_confirmation
