from app.clients.source_manager import session


def update_client_secret() -> str:
    url = 'security/update_client_secret'
    return session.request('PUT', url).text()


def invalidate_client_secret():
    url = 'security/invalidate_client_secret'
    session.request('DELETE', url)


def set_rabbitmq_credentials(username: str, password: str,
                             sm_name: str):
    url = 'security/set_rabbitmq_credentials'
    params = {
        'username': username,
        'password': password,
        'sm_name': sm_name,
    }
    session.request('POST', url, params=params)
