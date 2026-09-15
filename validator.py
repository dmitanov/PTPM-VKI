import re


BLACKLIST = {
    "admin",
    "administrator",
    "root",
    "user",
    "test",
    "guest"
}


def validate_login(login: str) -> tuple[bool, str]:
    """Проверяет логин."""

    if not isinstance(login, str):
        return False, "Логин должен быть строкой"

    if not login:
        return False, "Логин не может быть пустым"

    phone_pattern = r"^\+\d-\d{3}-\d{3}-\d{4}$"

    if re.fullmatch(phone_pattern, login):
        return True, ""

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if re.fullmatch(email_pattern, login):
        return True, ""

    username_pattern = r"^[A-Za-z0-9_]+$"

    if not re.fullmatch(username_pattern, login):
        return False, (
            "Логин должен содержать только латинские буквы, "
            "цифры и знак подчеркивания"
        )

    if len(login) < 5:
        return False, "Логин должен содержать минимум 5 символов"

    if login.lower() in BLACKLIST:
        return False, "Логин находится в черном списке"

    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Проверяет пароль."""

    if not isinstance(password, str):
        return False, "Пароль должен быть строкой"

    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    
    allowed_pattern = r"^[А-Яа-яЁё0-9!@#$%^&*()_+\-=\[\]{};:,.<>?/\\|`~]+$"

    if not re.fullmatch(allowed_pattern, password):
        return False, (
            "Пароль может содержать только кириллицу, "
            "цифры и специальные символы"
        )

    if not re.search(r"[А-ЯЁ]", password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"

    if not re.search(r"[а-яё]", password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"

    if not re.search(r"\d", password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    special_pattern = r"[!@#$%^&*()_+\-=\[\]{};:,.<>?/\\|`~]"

    if not re.search(special_pattern, password):
        return False, "Пароль должен содержать хотя бы один специальный символ"

    return True, ""


def validate_registration(
    login: str,
    password: str,
    password_confirmation: str
) -> tuple[bool, str]:

    login_valid, login_error = validate_login(login)

    if not login_valid:
        return False, login_error

    password_valid, password_error = validate_password(password)

    if not password_valid:
        return False, password_error

    if password != password_confirmation:
        return False, "Пароль и подтверждение пароля не совпадают"

    return True, ""