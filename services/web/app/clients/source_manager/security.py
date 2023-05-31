from app.clients.source_manager import session


def update_client_secret() -> str:
    url = 'security/update_client_secret'
    return session.request('PUT', url).text()


def invalidate_client_secret():
    url = 'security/invalidate_client_secret'
    session.request('DELETE', url)
