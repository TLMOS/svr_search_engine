from app.clients.source_manager import session


def get_last_frame(source_id: int) -> bytes:
    url = 'videos/get/frame/last'
    params = {'source_id': source_id}
    return session.request('GET', url, params=params).content


def get_frame(chunk_id: int, frame_id: int) -> bytes:
    url = f'videos/get/frame/{chunk_id}/{frame_id}'
    return session.request('GET', url).content
