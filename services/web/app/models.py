from redis_om import (EmbeddedJsonModel, Field, JsonModel)


class SourceManager(EmbeddedJsonModel):
    url: str = 'http://localhost'
    secret: str = 'secret'


class User(JsonModel):
    """
    Web UI user model.

    Attributes:
    - username (str): unique username, used as a key in Redis OM
    - password (str): hashed password
    - encryption_key (str): key used to encrypt/decrypt sub services' secrets,
    """

    username: str = Field(index=True, min_length=3, max_length=50)
    password: str

    source_manager: SourceManager = SourceManager()
