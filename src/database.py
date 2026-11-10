"""Репозиторий для хранения сообщений форума в SQLite."""

from __future__ import annotations

import sqlite3
from typing import Optional

MAX_NAME_LENGTH = 256
MAX_MESSAGE_LENGTH = 8096


class ValidationError(ValueError):
    """Некорректные входные данные для операций с БД."""


class DuplicateIdError(sqlite3.IntegrityError):
    """Попытка добавить запись с уже существующим ID."""


class CommentNotFoundError(LookupError):
    """Запись с указанным ID не найдена."""


class DatabaseRepository:
    """Класс-репозиторий для работы с таблицей comments."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._connection = sqlite3.connect(db_path)
        self._connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK (length(name) <= 256),
                message TEXT NOT NULL CHECK (length(message) <= 8096)
            );
            """
        )
        self._connection.commit()

    @staticmethod
    def _validate_comment_id(comment_id: int) -> None:
        if isinstance(comment_id, bool) or not isinstance(comment_id, int):
            raise ValidationError("ID должен быть целым числом")

    @staticmethod
    def _validate_username(username: str) -> None:
        if not isinstance(username, str):
            raise ValidationError("Имя пользователя должно быть строкой")
        if len(username) > MAX_NAME_LENGTH:
            raise ValidationError(
                f"Имя пользователя не должно превышать {MAX_NAME_LENGTH} символов"
            )

    @staticmethod
    def _validate_message(message: str) -> None:
        if not isinstance(message, str):
            raise ValidationError("Сообщение должно быть строкой")
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValidationError(
                f"Сообщение не должно превышать {MAX_MESSAGE_LENGTH} символов"
            )

    def get_by_id(self, comment_id: int) -> Optional[dict]:
        """Возвращает запись по ID или None, если записи нет."""
        self._validate_comment_id(comment_id)
        row = self._connection.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,),
        ).fetchone()
        return dict(row) if row is not None else None

    def get_by_name(self, username: str) -> list[dict]:
        """Возвращает все записи пользователя с указанным name."""
        self._validate_username(username)
        rows = self._connection.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id",
            (username,),
        ).fetchall()
        return [dict(row) for row in rows]

    def add(self, comment_id: int, username: str, message: str) -> bool:
        """Добавляет запись. Возвращает True при успехе."""
        self._validate_comment_id(comment_id)
        self._validate_username(username)
        self._validate_message(message)

        try:
            with self._connection:
                self._connection.execute(
                    "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                    (comment_id, username, message),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicateIdError(f"Запись с ID {comment_id} уже существует") from exc
        return True

    def update(self, comment_id: int, new_message: str) -> bool:
        """Обновляет message существующей записи. Возвращает True при успехе."""
        self._validate_comment_id(comment_id)
        self._validate_message(new_message)

        cursor = self._connection.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id),
        )
        self._connection.commit()
        if cursor.rowcount == 0:
            raise CommentNotFoundError(f"Запись с ID {comment_id} не найдена")
        return True

    def delete(self, comment_id: int) -> bool:
        """Удаляет запись по ID. Возвращает True при успехе."""
        self._validate_comment_id(comment_id)
        cursor = self._connection.execute(
            "DELETE FROM comments WHERE id = ?",
            (comment_id,),
        )
        self._connection.commit()
        if cursor.rowcount == 0:
            raise CommentNotFoundError(f"Запись с ID {comment_id} не найдена")
        return True

    def get_all(self) -> list[dict]:
        """Возвращает все записи, отсортированные по ID."""
        rows = self._connection.execute(
            "SELECT id, name, message FROM comments ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "DatabaseRepository":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
