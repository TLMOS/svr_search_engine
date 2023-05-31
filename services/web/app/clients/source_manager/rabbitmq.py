from app.clients.source_manager import session


def set_credentials(username: str, password: str):
    url = 'rabbitmq/set_credentials'
    params = {'username': username, 'password': password}
    session.request('POST', url, params=params)


def startup():
    url = 'rabbitmq/startup'
    session.request('POST', url)


def shutdown():
    url = 'rabbitmq/shutdown'
    session.request('POST', url)


def is_opened() -> bool:
    url = 'rabbitmq/is_opened'
    return session.request('GET', url).json()
