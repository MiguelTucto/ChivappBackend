import hashlib
import re

import bcrypt

LEGACY_PREFIX = "$bcrypt-sha256$"


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if len(password) > 128:
        raise ValueError("La contraseña no debe superar los 128 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r"\d", password):
        raise ValueError("La contraseña debe contener al menos un número.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", password):
        raise ValueError("La contraseña debe contener al menos un carácter especial.")


def _password_digest(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_digest(password), bcrypt.gensalt()).decode("utf-8")


def _verify_legacy_passlib(plain: str, hashed: str) -> bool:
    try:
        from passlib.context import CryptContext

        ctx = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
        return ctx.verify(plain, hashed)
    except Exception:
        return False


def verify_password(plain: str, hashed: str) -> bool:
    if hashed.startswith(LEGACY_PREFIX):
        return _verify_legacy_passlib(plain, hashed)

    try:
        return bcrypt.checkpw(_password_digest(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
