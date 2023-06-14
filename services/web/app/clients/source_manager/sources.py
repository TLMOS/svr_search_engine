from common.schemas import Source
from app.clients.source_manager import session


def create_from_url(name: str, source_url: str) -> dict:
    url = 'sources/create/url'
    params = {'name': name, 'url': source_url}
    return session.request('POST', url, params=params).json()


def creare_from_file(name: str, file_name: str, content: bytes) -> dict:
    url = 'sources/create/file'
    params = {'name': name}
    files = {'file': (file_name, content)}
    return session.request('POST', url, params=params, files=files).json()


def get(id: int) -> Source:
    url = f'sources/get/{id}'
    source = session.request('GET', url).json()
    return Source(**source)


def get_all() -> list[Source]:
    url = 'sources/get/all'
    sources = session.request('GET', url).json()
    return [Source(**source) for source in sources]


def get_time_coverage(id: int) -> list[tuple[float, float]]:
    url = 'sources/get/time_coverage'
    params = {'id': id}
    return session.request('GET', url, params=params).json()


def start(id: int):
    url = 'sources/start'
    params = {'id': id}
    session.request('PUT', url, params=params)


def start_all(start_finished: bool = False):
    url = 'sources/start/all'
    params = {'start_finished': start_finished}
    session.request('PUT', url, params=params)


def pause(id: int):
    url = 'sources/pause'
    params = {'id': id}
    session.request('PUT', url, params=params)


def pause_all():
    url = 'sources/pause/all'
    session.request('PUT', url)


def finish(id: int):
    url = 'sources/finish'
    params = {'id': id}
    session.request('PUT', url, params=params)


def delete(id: int):
    url = 'sources/delete'
    params = {'id': id}
    session.request('DELETE', url, params=params)
