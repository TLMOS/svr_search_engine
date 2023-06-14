from typing import Optional

from pydantic import BaseModel

from common.constants import SourceStatus


class RabbitMQCredentials(BaseModel):
    host: str
    port: int
    virtual_host: str
    username: str
    password: str


class ClientCredentials(BaseModel):
    client_id: str
    client_secret: str


class SourceManagerRegister(BaseModel):
    api_key: str
    search_engine: ClientCredentials


class SourceBase(BaseModel):
    name: str
    url: str


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int
    status_code: SourceStatus
    status_msg: Optional[str] = None

    class Config:
        orm_mode = True


class VideoChunkBase(BaseModel):
    source_id: int
    file_path: str
    start_time: float
    end_time: float
    farme_count: int


class VideoChunkCreate(VideoChunkBase):
    pass


class VideoChunk(VideoChunkBase):
    id: int

    class Config:
        orm_mode = True
