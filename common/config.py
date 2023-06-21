from typing import Literal, Optional
from pathlib import Path
import os

from pydantic import (
    BaseModel,
    BaseSettings,
    Field,
    validator,
    PositiveInt,
)


class WebSettings(BaseModel):
    max_content_length: PositiveInt = 1024 * 1024 * 200
    upload_extensions: list[str] = ['.jpg', '.png', '.mp4', '.avi']

    username_min_length: PositiveInt = 3
    username_max_length: PositiveInt = 32
    password_min_length: PositiveInt = 8
    password_max_length: PositiveInt = 64

    secret_key: str = os.urandom(32)  # Make sure to redefine it in production
    jwt_algorithm: Literal['HS256'] = 'HS256'
    jwt_access_token_expire_minutes: PositiveInt = 60 * 24 * 7  # 7 days

    hnsw_recreate_index_on_startup: bool = False
    hnsw_dim: PositiveInt = 512
    hnsw_distance_metric: Literal['L2', 'IP', 'COSINE'] = 'IP'
    hnsw_initial_cap: PositiveInt = 50000
    hnsw_m: PositiveInt = 40
    hnsw_ef_construction: PositiveInt = 200
    hnsw_ef_runtime: PositiveInt = 100
    hnsw_epsilon: float = 0.8


class EncoderSettings(BaseModel):
    url: str = 'http://encoder:8080'
    model: str = 'openai/clip-vit-base-patch32'


class SearchEngineSettings(BaseModel):
    url: str = 'http://search_engine:8080'


class RedisSettings(BaseModel):
    host: str = '0.0.0.0'
    port: PositiveInt = 6379
    db: PositiveInt = 0
    username: Optional[str] = None
    password: Optional[str] = None


class RabbitMQSettings(BaseModel):
    host: str = '0.0.0.0'
    port: PositiveInt = 5672
    virtual_host: str = '/'
    source_manager_username: str = 'source_manager'
    source_manager_password: str = 'source_manager'


class PathsSettings(BaseModel):
    static_dir: Path = Path('./static')
    media_dir: Path = Path('./media')

    @validator('*')
    def validate_path(cls, v: Path, field: Field):
        if field.name.endswith('_dir'):
            v.mkdir(parents=True, exist_ok=True)
        return v.resolve()


class VideoSettings(BaseModel):
    frame_width: int = Field(640, ge=28, le=1920)
    frame_height: int = Field(480, ge=28, le=1080)
    chunk_duration: float = Field(60, gt=1, le=600)
    chunk_fps: float = Field(1, gt=0, le=60)
    draw_timestamp: bool = True


class Settings(BaseSettings):
    web: WebSettings = WebSettings()
    encoder: EncoderSettings = EncoderSettings()
    search_engine: SearchEngineSettings = SearchEngineSettings()
    redis: RedisSettings = RedisSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    paths: PathsSettings = PathsSettings()
    video: VideoSettings = VideoSettings()

    class Config:
        env_nested_delimiter = '__'


settings = Settings()
