from typing import Optional
from datetime import datetime, timedelta

from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from flask_login import UserMixin

from common.config import settings
from app import models


class TokenData(BaseModel):
    """ OAuth2 access token data """
    username: str
    sm_secret: str


class UserSession(BaseModel, UserMixin):
    db: models.User
    sm_secret: str
    token: Optional[str] = None

    def get_id(self):
        """
        ID used for Flask-Login. Can be any unique identifier.
        Part of UserMixin logic.
        """
        if self.token is None:
            raise AttributeError('token is not set')
        return self.token


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Parameters:
    - data (dict): data to encode
    - expires_delta (timedelta): token expiration time

    Returns:
    - str: encoded JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.security.secret_key,
        algorithm=settings.security.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode JWT access token.

    Parameters:
    - token (str): encoded JWT access token

    Returns:
    - Optional[TokenData]: decoded JWT access token if valid, None otherwise
    """

    try:
        payload = jwt.decode(
            token=token,
            key=settings.security.secret_key,
            algorithms=[settings.security.jwt_algorithm],
        )
        username = payload.get('sub')
        sm_secret = payload.get('sm_secret')
        return TokenData(
            username=username,
            sm_secret=sm_secret,
        )
    except (JWTError, ValidationError):
        return None
