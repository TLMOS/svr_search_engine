import os
from pathlib import Path

from pydantic import BaseModel, BaseSettings


basedir = Path(__file__).parent.parent.absolute()


class WebSettings(BaseModel):
    client_id: str = 'search_engine_web_ui'
    max_content_length: int = 1024 * 1024 * 200
    upload_extensions: list[str] = ['.jpg', '.png', '.mp4', '.avi']


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
    redis: RedisSettings = RedisSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    security: SecuritySettings = SecuritySettings()
    paths: PathsSettings = PathsSettings()


settings = Settings()

settings.paths.static_dir = settings.paths.static_dir.resolve().absolute()
settings.paths.media_dir = settings.paths.media_dir.resolve().absolute()
settings.paths.static_dir.mkdir(exist_ok=True)
settings.paths.media_dir.mkdir(exist_ok=True)
