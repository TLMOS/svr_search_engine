from typing import Optional
from datetime import datetime, timedelta

from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from flask_login import UserMixin
from redis_om import NotFoundError

from common.config import settings
from app.database import models


class TokenData(BaseModel):
    """ OAuth2 access token data """
    user_pk: str
    source_manager_api_key: Optional[str] = None


class UserSession(BaseModel, UserMixin):
    token: str
    db_user: models.User
    source_manager_api_key: Optional[str] = None

    @staticmethod
    def from_token(token: str) -> 'UserSession':
        """
        Create UserSession from JWT token.

        Parameters:
        - token (str): encoded JWT access token

        Returns:
        - UserSession: UserSession object
        """
        token_data = decode_access_token(token)
        if token_data is None:
            return None

        try:
            db_user = models.User.get(token_data.user_pk)
        except NotFoundError:
            return None

        return UserSession(
            token=token,
            db_user=db_user,
            source_manager_api_key=token_data.source_manager_api_key,
        )

    def get_id(self):
        """
        ID used for Flask-Login. Can be any unique identifier.
        Part of UserMixin logic.
        """
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
        key=settings.web.secret_key,
        algorithm=settings.web.jwt_algorithm,
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
            key=settings.web.secret_key,
            algorithms=[settings.web.jwt_algorithm],
        )
        user_pk = payload.get('user_pk')
        source_manager_api_key = payload.get('source_manager_api_key', None)
        return TokenData(
            user_pk=user_pk,
            source_manager_api_key=source_manager_api_key,
        )
    except (JWTError, ValidationError):
        return None
