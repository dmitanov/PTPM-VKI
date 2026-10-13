"""Класс-контроллер (пункт «e»).

Реализует сквозной сценарий регистрации: получает данные пользователя,
ищет запись в БД, при её отсутствии вычисляет результат и сохраняет его,
отправляет строку-результат сторонней зависимости и возвращает результат.
"""


class Controller:
    """Бизнес-логика сквозного сценария регистрации."""

    def __init__(
        self,
        calculator,
        database,
        user_interface,
        notification_service
    ) -> None:
        self._calculator = calculator
        self._database = database
        self._user_interface = user_interface
        self._notification_service = notification_service

    def process_registration(self) -> tuple[bool, str]:
        """Выполняет полный сценарий регистрации и возвращает результат."""

        login, password, password_confirmation = (
            self._user_interface.get_registration_data()
        )

        record = self._database.get_record(
            login,
            password,
            password_confirmation
        )

        if record is None:
            result = self._calculator.calculate(
                login,
                password,
                password_confirmation
            )
            self._database.add_record(
                login,
                password,
                password_confirmation,
                result[0],
                result[1]
            )
        else:
            result = record

        success, message = result

        if success:
            result_line = f"Регистрация {login}: успешно"
        else:
            result_line = f"Регистрация {login}: ошибка — {message}"

        self._notification_service.send_result(result_line)

        return success, message
