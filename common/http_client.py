from typing import Optional, Callable
from functools import partial

import requests


def concat_url(url: str, route: str) -> str:
    """Concatenate url and route."""
    if url[-1] != '/':
        url += '/'
    route = route.strip('/')
    return url + route


class ClientSession:
    """
    Requests wrapper with authentication and middleware support.

    Parameters:
    - url (str): base url
    - id (Optional[str]): client id, used for authentication
    - secret (Optional[str]): client secret, used for authentication

    Usage:
    ```python
    session = ClientSession('http://example.com')

    @session.middleware
    def middleware(request: ClientRequest, call: Callable):
        requset.headers['X-Auth'] = '123'
        response = call(request)
        if response.status_code == 401:
            raise UnauthorizedError()
        return response

    def ping():
        response = session.request('ping', method='GET')
        print(response.text())
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._middleware: Optional[Callable] = None

    def _call_factory(self, method: str):
        return partial(requests.request, method)

    def request(self, method: str, route: str, **kwargs) -> requests.Response:
        url = concat_url(self.base_url, route)
        call = self._call_factory(method)
        if self._middleware:
            return self._middleware(call, url, **kwargs)
        else:
            return call(url, **kwargs)

    def middleware(self, func: Callable):
        self._middleware = func
        return func


class AuthClientSession(ClientSession):
    def __init__(self, base_url: str):
        super().__init__(base_url)

        self.token_route: Optional[str] = None
        self.id: Optional[str] = None
        self.secret: Optional[str] = None

        self._token: Optional[str] = None

    def _call_factory(self, method: str):
        def base_call(url, **kwargs):
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            if self._token:
                kwargs['headers']['Authorization'] = f'Bearer {self._token}'
            return requests.request(method, url, **kwargs)

        def auth_call(url, **kwargs):
            response = base_call(url, **kwargs)
            if response.status_code == 401:
                self.login()
                response = base_call(url, **kwargs)
            return response

        return auth_call

    def login(self):
        if self.token_route is None:
            raise ValueError('Token route is required.')
        if self.id is None:
            raise ValueError('Client id is required.')

        protocol, host = self.base_url.split('://')
        if self.secret is not None:
            base_url = f'{protocol}://{self.id}:{self.secret}@{host}'
        else:
            base_url = f'{protocol}://{self.id}@{host}'
        url = concat_url(base_url, self.token_route)

        response = requests.request('POST', url)
        if response.status_code == 200:
            json = response.json()
            if isinstance(json, dict):
                if 'token' in json:
                    self._token = json['token']
                elif 'access_token' in json:
                    self._token = json['access_token']
            else:
                self._token = json

    def set_auth(self, token_route: str, id: str, secret: str):
        self.token_route = token_route
        self.id = id
        self.secret = secret
