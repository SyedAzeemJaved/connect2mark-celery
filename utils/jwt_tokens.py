from datetime import datetime, timedelta, timezone

from jose import jwt


def create_access_token(
    data: dict, expires_delta: timedelta, key: str, algorithm: str
) -> str:
    """Generate JWT based access token"""
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=key, algorithm=algorithm)

    return encoded_jwt
