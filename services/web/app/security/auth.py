from typing import Optional
from datetime import datetime, timedelta
from base64 import b64decode

from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from flask import request, jsonify
from flask_login import UserMixin
from redis_om import NotFoundError

from common.config import settings
from app.database import models
from app.security.secrets import verify


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


def validate_source_manager_token(token: str) -> bool:
    """
    Validate basic authentication token for source manager.

    Parameters:
    - token (str): basic authentication token

    Returns:
    - bool: True if valid, False otherwise
    """
    try:
        token = token.split(' ')[1]
        token = b64decode(token.encode()).decode()
        client_id, client_secret = token.split(':')
        db_user = models.User.find(
            models.User.source_manager.client_id == client_id
        ).first()
        return verify(client_secret, db_user.source_manager.client_secret_hash)
    except Exception:
        return False


def source_manager_auth_required(func):
    """
    Decorator for Flask routes that require source manager authentication.
    """

    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not validate_source_manager_token(auth):
            return jsonify({'message': 'Unauthorized'}), 401
        return func(*args, **kwargs)

    return wrapper
