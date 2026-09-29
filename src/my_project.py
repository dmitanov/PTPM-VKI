import hashlib
import logging
import os
import sys

from validator import validate_registration


os.makedirs("logs", exist_ok=True)


log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            "logs/file_txt.log",
            encoding="utf-8"
        )
    ]
)


def mask_password(password: str) -> str:
    """
    Создаёт детерминированную маску пароля.

    Один и тот же пароль -> одна и та же маска.
    Разные пароли -> разные маски.

    ИСПРАВЛЕНО (ЛР2): нестроковые значения больше не вызывают AttributeError,
    а приводятся к строке. Раньше register_user падал ещё до входа в блок try.
    """

    raw = password if isinstance(password, str) else str(password)

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def register_user(
    login: str,
    password: str,
    password_confirmation: str
) -> tuple[bool, str]:

    # ИСПРАВЛЕНО (ЛР2): логирование запроса перенесено внутрь блока try,
    # чтобы любая ошибка на этапе подготовки к запросу не вылетала наружу.
    try:
        logging.info(
            "Запрос регистрации: login=%s, password_hash=%s",
            login,
            mask_password(password)
        )

        result, message = validate_registration(
            login,
            password,
            password_confirmation
        )

        if result:
            logging.info(
                "Регистрация успешна: login=%s, result=True",
                login
            )

            return True, ""

        logging.warning(
            "Регистрация отклонена: login=%s, error=%s",
            login,
            message
        )

        return False, message

    except Exception:
        logging.exception(
            "Критическая ошибка при обработке регистрации: login=%s",
            login
        )

        return False, "Внутренняя ошибка программы"


def main():
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    test_users = [
        (
            "student_123",
            "Пароль1!",
            "Пароль1!"
        ),
        (
            "admin",
            "Пароль1!",
            "Пароль1!"
        ),
        (
            "student",
            "пароль1!",
            "Пароль1!"
        ),
        (
            "student_123",
            "Пароль1!",
            "Пароль2!"
        ),
        (
            "student@example.com",
            "Пароль123!",
            "Пароль123!"
        ),
        (
            "+1-123-456-7890",
            "Пароль123!",
            "Пароль123!"
        )
    ]

    for login, password, confirmation in test_users:

        success, message = register_user(
            login,
            password,
            confirmation
        )

        if success:
            print(
                f"Регистрация {login}: успешно"
            )
        else:
            print(
                f"Регистрация {login}: ошибка — {message}"
            )


if __name__ == "__main__":
    main()
