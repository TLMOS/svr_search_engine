from redis_om import JsonModel, EmbeddedJsonModel, Field, Migrator

from app.database import connection


class SourceManager(EmbeddedJsonModel):
    """
    Source manager model.

    Attributes:
    - url (str): URL of the source manager
    - api_key_encrypted (str): API key used to access the source manager,
        encrypted with user password
    - client_id (str): part of basic auth credentials, which is used
        by the source manager to access the search engine
    - client_secret (str): part of basic auth credentials, which is used
        by the source manager to access the search engine
    """
    url: str
    api_key_encrypted: str

    client_id: str = Field(index=True)
    client_secret_hash: str

    class Meta:
        database = connection


class User(JsonModel):
    """
    Web UI user model.

    Attributes:
    - username (str): unique username, used as a key in Redis OM
    - password (str): password hash
    - source_manager (SourceManager): model of the source manager user owns
    """
    username: str = Field(index=True)
    password_hash: str

    source_manager: SourceManager

    class Meta:
        database = connection


Migrator().run()
