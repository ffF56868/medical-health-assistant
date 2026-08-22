import base64
import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta


PHONE_PATTERN = re.compile(r"(?:\+?86)?1[3-9]\d{9}")
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 32
SESSION_DAYS = 7


def normalize_account(value: str) -> str:
    """Normalize a Chinese mobile number or email into one stored format."""
    if not isinstance(value, str):
        raise ValueError("账号必须是有效的中国手机号或邮箱")

    normalized_value = value.strip()
    compact_value = re.sub(r"[\s-]", "", normalized_value)
    if PHONE_PATTERN.fullmatch(compact_value):
        if compact_value.startswith("+86"):
            mobile = compact_value[3:]
        elif compact_value.startswith("86") and len(compact_value) == 13:
            mobile = compact_value[2:]
        else:
            mobile = compact_value
        return f"+86{mobile}"

    if len(normalized_value) <= 200 and EMAIL_PATTERN.fullmatch(normalized_value):
        return normalized_value.lower()

    raise ValueError("账号必须是有效的中国手机号或邮箱")


def validate_password(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("密码必须是英文字母和数字的组合")
    if not PASSWORD_MIN_LENGTH <= len(value) <= PASSWORD_MAX_LENGTH:
        raise ValueError("密码长度必须是 8-32 位")
    if not re.search(r"[A-Za-z]", value):
        raise ValueError("密码至少需要包含一个英文字母")
    if not re.search(r"\d", value):
        raise ValueError("密码至少需要包含一个数字")
    return value


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
    encoded_hash = base64.urlsafe_b64encode(password_hash).decode("ascii")
    return f"scrypt$16384$8$1${encoded_salt}${encoded_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, n, r, p, encoded_salt, encoded_hash = stored_hash.split("$")
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected_hash = base64.urlsafe_b64decode(encoded_hash.encode("ascii"))
        actual_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
        )
    except (TypeError, ValueError, UnicodeError):
        return False
    return secrets.compare_digest(actual_hash, expected_hash)


def create_access_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=SESSION_DAYS)
    return token, expires_at


def hash_access_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_expired(value: datetime) -> bool:
    normalized_value = value.replace(tzinfo=UTC) if value.tzinfo is None else value
    return normalized_value <= datetime.now(UTC)
