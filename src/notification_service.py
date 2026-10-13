"""Класс сторонней зависимости (пункт «d»).

Интерфейс задан абстрактным базовым классом NotificationService.
Реализация EmailNotificationService имитирует передачу строки-результата
стороннему процессу (email-серверу).
"""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """Абстрактный интерфейс отправки результата сторонней зависимости."""

    @abstractmethod
    def send_result(self, result: str) -> None:
        """Передаёт строку-результат стороннему процессу."""

        raise NotImplementedError


class EmailNotificationService(NotificationService):
    """Имитация отправки результата на email-сервер."""

    def send_result(self, result: str) -> None:
        print(f"[EMAIL] Отправка результата на внешний сервер: {result}")
