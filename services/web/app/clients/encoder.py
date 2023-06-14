from typing import Callable
from urllib.error import HTTPError

from common.config import settings
from common.clients.http import ClientSession
from common.utils.fastapi import get_error_msg


session = ClientSession(settings.encoder.url)


@session.middleware
def middleware(call: Callable, url: str, **kwargs):
    response = call(url, **kwargs)
    if response.status_code >= 400:
        msg = get_error_msg(response)
        detail = f'Got `{msg}` while sending request to text encoder'
        raise HTTPError(url, response.status_code, detail, response.headers)
    return response


def encode(text: str) -> bytes:
    params = {'text': text}
    response = session.request('GET', '/encode', params=params)
    return response.content
