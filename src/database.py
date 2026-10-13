"""Класс работы с базой данных (пункт «b»).

Реализует хранение записей регистрации в SQLite. Одна запись содержит:
логин, пароль, подтверждение_пароля, результат_авторизации,
сообщение_об_ошибке. Запись идентифицируется по логину, паролю и
подтверждению пароля.
"""

import sqlite3


class RegistrationDatabase:
    """Хранилище записей регистрации на базе SQLite."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._connection = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                password_confirmation TEXT NOT NULL,
                authorization_result INTEGER NOT NULL,
                error_message TEXT NOT NULL,
                PRIMARY KEY (login, password, password_confirmation)
            )
            """
        )
        self._connection.commit()

    def add_record(
        self,
        login: str,
        password: str,
        password_confirmation: str,
        authorization_result: bool,
        error_message: str = ""
    ) -> None:
        """Добавляет запись, заменяя существующую с тем же ключом."""

        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO registrations
                (login, password, password_confirmation,
                 authorization_result, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                login,
                password,
                password_confirmation,
                int(bool(authorization_result)),
                error_message
            )
        )
        self._connection.commit()

    def get_record(
        self,
        login: str,
        password: str,
        password_confirmation: str
    ) -> tuple[bool, str] | None:
        """Возвращает запись по ключу или None, если записи нет."""

        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT authorization_result, error_message
            FROM registrations
            WHERE login = ? AND password = ? AND password_confirmation = ?
            """,
            (login, password, password_confirmation)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return bool(row[0]), row[1]

    def delete_record(
        self,
        login: str,
        password: str,
        password_confirmation: str
    ) -> bool:
        """Удаляет запись по ключу. Возвращает True, если запись была удалена."""

        cursor = self._connection.cursor()
        cursor.execute(
            """
            DELETE FROM registrations
            WHERE login = ? AND password = ? AND password_confirmation = ?
            """,
            (login, password, password_confirmation)
        )
        deleted = cursor.rowcount
        self._connection.commit()

        return deleted > 0

    def close(self) -> None:
        """Закрывает соединение с базой данных."""

        self._connection.close()
