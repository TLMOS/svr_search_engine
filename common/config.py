import os
from pathlib import Path

from pydantic import BaseModel, BaseSettings


basedir = Path(__file__).parent.parent.absolute()


class WebSettings(BaseModel):
    client_id: str = 'search_engine_web_ui'
    max_content_length: int = 1024 * 1024 * 200
    upload_extensions: list[str] = ['.jpg', '.png', '.mp4', '.avi']


class EncoderSettings(BaseModel):
    url: str = 'http://encoder:8000'
    model: str = 'RN50'


class SearchEngineSettings(BaseModel):
    url: str = 'http://search_engine:8000'


class RedisSettings(BaseModel):
    host: str = 'redis'
    port: int = 6379


class RabbitMQSettings(BaseModel):
    sm_username: str = 'source_manager'
    sm_password: str = 'source_manager'


class SecuritySettings(BaseModel):
    secret_key: str = os.urandom(32)  # Make sure to redefine it in production
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


class PathsSettings(BaseModel):
    static_dir = (basedir / 'static')
    media_dir = (basedir / 'media')


class Settings(BaseSettings):
    web: WebSettings = WebSettings()
    encoder: EncoderSettings = EncoderSettings()
    search_engine: SearchEngineSettings = SearchEngineSettings()
    redis: RedisSettings = RedisSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    security: SecuritySettings = SecuritySettings()
    paths: PathsSettings = PathsSettings()

    class Config:
        env_nested_delimiter = '__'


settings = Settings()

settings.paths.static_dir = settings.paths.static_dir.resolve().absolute()
settings.paths.media_dir = settings.paths.media_dir.resolve().absolute()
settings.paths.static_dir.mkdir(exist_ok=True)
settings.paths.media_dir.mkdir(exist_ok=True)
