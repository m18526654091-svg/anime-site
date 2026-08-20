import os
from datetime import datetime, timedelta

import bcrypt
from jose import jwt

# Known insecure / placeholder values that MUST never be used for signing.
_INSECURE_SECRETS = {
    "",
    "animehub-secret-key-change-me-in-production",
    "change-me-in-production",
    "changeme",
    "secret",
    "dev-secret-key",
}


def _load_secret_key() -> str:
    """Load SECRET_KEY from the environment and refuse insecure values.

    The JWTs are signed with this key, so a missing or well-known value would
    let anyone forge admin tokens. Fail fast with a clear message instead of
    silently running on an insecure default.
    """
    value = os.getenv("SECRET_KEY", "").strip()
    if not value:
        raise RuntimeError(
            "SECRET_KEY environment variable is required.\n"
            "Generate a strong random value before starting, e.g.\n"
            "  export SECRET_KEY=$(openssl rand -hex 32)\n"
            "Refusing to start without a secret key."
        )
    if value in _INSECURE_SECRETS or len(value) < 16:
        raise RuntimeError(
            "SECRET_KEY is missing, too short (<16 chars), or set to an insecure "
            "placeholder value.\n"
            "Production deployments MUST provide a unique strong random value via "
            "the SECRET_KEY environment variable. Refusing to start."
        )
    return value


SECRET_KEY = _load_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def hash_password(password: str) -> str:
    # bcrypt max input is 72 bytes
    pwd = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pwd = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd, hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

