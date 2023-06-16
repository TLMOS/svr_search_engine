from typing import Callable
from urllib.error import HTTPError
from secrets import token_urlsafe
from uuid import uuid4

from common.clients.http import ClientSession
from common.utils.fastapi import get_error_msg
from common import schemas
from app.database import models
from app.security import secrets


session = ClientSession('0.0.0.0:8080')  # Base url is set with user login


@session.middleware
def middleware(call: Callable, url: str, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    if 'api_key' in session.state:
        api_key = session.state['api_key']
        kwargs['headers']['Authorization'] = f'Bearer {api_key}'
    response = call(url, **kwargs)
    if response.status_code >= 400:
        msg = get_error_msg(response)
        detail = f'Got `{msg}` while sending request to source manager'
        raise HTTPError(url, response.status_code, detail,
                        response.headers, None)
    return response


def is_registered() -> bool:
    url = '/is_registered'
    response = session.request('GET', url)
    return response.json()['is_registered']


def register() -> tuple[str, str, str]:
    """
    Register source manager and return credentials.

    Returns:
    - api_key (str): API key to access source manager after registration
    - client_id (str): OAuth2 client ID, used to authenticate source manager
        with the search engine
    - client_secret (str): OAuth2 client secret, used to authenticate source
        manager with the search engine
    """
    api_key = token_urlsafe(32)
    client_id = str(uuid4()).replace('-', '')
    client_secret = token_urlsafe(32)

    # Create temporary user, which will be used by source manager for
    # first authorization
    db_tmp_user = models.User(
        username='',
        password_hash='',
        source_manager=models.SourceManager(
            url='',
            api_key_encrypted='',
            client_id=client_id,
            client_secret_hash=secrets.hash(client_secret),
        ),
    )
    db_tmp_user.save()
    db_tmp_user.expire(60)

    credentials = schemas.SourceManagerRegister(
        api_key=api_key,
        search_engine=schemas.ClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        ),
    )

    session.request('POST', '/register', json=credentials.dict())
    session.state['api_key'] = api_key

    return api_key, client_id, client_secret


def unregister():
    session.request('POST', '/unregister')
    session.base_url = '0.0.0.0:8080'
    session.state = {}
