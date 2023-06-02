from typing import Optional, Callable
from urllib.error import HTTPError

from common.config import settings
from common import schemas
from common.http_client import ClientSession


session = ClientSession(settings.search_engine.url)


@session.middleware
def middleware(call: Callable, url, **kwargs):
    response = call(url, **kwargs)
    if response.status_code >= 400:
        msg = 'Unparsable response'
        content_type = response.headers.get('Content-Type', None)
        if 'Content-Type' in response.headers:
            if content_type == 'application/json':
                msg = response.json()
            elif content_type == 'text/html; charset=utf-8':
                msg = response.text
            elif content_type == 'text/plain; charset=utf-8':
                msg = response.text
        if isinstance(msg, dict) and 'detail' in msg:
            msg = msg['detail']
        if isinstance(msg, list):
            msg = msg[0]
        if isinstance(msg, dict) and 'msg' in msg:
            msg = msg['msg']
        detail = f'Got `{msg}` while sending request to source manager'
        raise HTTPError(
            url=url,
            code=response.status_code,
            msg=detail,
            hdrs=response.headers,
            fp=None
        )
    return response


def search(
    sm_name: str,
    text: str,
    top_k: int = 10,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> list[schemas.Frame]:
    params = {
        'sm_name': sm_name,
        'text': text,
        'top_k': top_k,
        'start_time': start_time,
        'end_time': end_time,
    }
    response = session.request('GET', '/search', params=params)
    return [schemas.Frame(**frame) for frame in response.json()]
