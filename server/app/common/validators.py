import re

PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{7,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_RE = re.compile(r"^(?=.*[0-9])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$")


def is_valid_phone(phone):
    return bool(phone and PHONE_RE.match(phone))


def is_valid_email(email):
    return bool(email and EMAIL_RE.match(email))


def is_strong_password(password):
    return bool(password and PASSWORD_RE.match(password))


def whatsapp_link(phone: str, message: str) -> str:
    from urllib.parse import quote

    if not is_valid_phone(phone):
        raise ValueError("Invalid phone number")

    clean = re.sub(r"\D", "", phone)
    if clean.startswith("00"):
        clean = clean[2:]
    elif clean.startswith("0"):
        clean = f"254{clean[1:]}"
    elif len(clean) == 9:
        clean = f"254{clean}"

    if not 8 <= len(clean) <= 15 or clean.startswith("0"):
        raise ValueError("Phone number must be in international format")

    return f"https://wa.me/{clean}?text={quote(message, safe='')}"