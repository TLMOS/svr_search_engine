from typing import Optional

from pydantic import BaseModel
from redis.exceptions import ResponseError
from redis.commands.search.indexDefinition import IndexDefinition
from redis.commands.search.field import VectorField, TagField, NumericField
from redis.commands.search.query import Query

from common.config import settings
from app.database import connection


index_def = IndexDefinition(
    prefix=['frame:'],
)

schema = (
    TagField('source_manager_id'),
    TagField('source_id'),
    NumericField('timestamp'),
    VectorField(
        name='embedding',
        algorithm='HNSW',
        attributes={
            'TYPE': 'FLOAT32',
            'DIM': settings.web.hnsw_dim,
            'DISTANCE_METRIC': settings.web.hnsw_distance_metric,
            'INITIAL_CAP': settings.web.hnsw_initial_cap,
            'M': settings.web.hnsw_m,
            'EF_CONSTRUCTION': settings.web.hnsw_ef_construction,
            'EF_RUNTIME': settings.web.hnsw_ef_runtime,
            'EPSILON': settings.web.hnsw_epsilon,
        }
    ),
)

# Create index if it doesn't exist, or recreate it if such option is enabled
try:
    connection.ft('frame_idx').info()
    if settings.web.hnsw_recreate_index_on_startup:
        connection.ft('frame_idx').dropindex(delete_documents=False)
        connection.ft('frame_idx').create_index(schema, definition=index_def)
except ResponseError:
    connection.ft('frame_idx').create_index(schema, definition=index_def)


class Frame(BaseModel):
    source_id: int
    chunk_id: int
    position: int
    timestamp: float
    box: list[int]


def find(
    query_embedding: bytes,
    top_k: int,
    source_manager_id: int,
    time_start: Optional[float],
    time_end: Optional[float],
):
    if time_start is None:
        time_start = '-inf'
    if time_end is None:
        time_end = '+inf'

    filter = '@source_manager_id:{{{}}} @timestamp:[{} {}]'.format(
        source_manager_id, time_start, time_end
    )
    query = f'({filter})=>[KNN {top_k} @embedding $query_embedding AS score]'
    query_params = {'query_embedding': query_embedding}
    results = connection.ft('frame_idx').search(
        Query(query).sort_by('score').dialect(2),
        query_params=query_params
    )

    frames = []
    for doc in results.docs:
        frame = Frame(
            source_id=doc.source_id,
            chunk_id=doc.chunk_id,
            position=doc.position,
            timestamp=doc.timestamp,
            box=list(map(int, doc.box.split(',')))
        )
        frames.append(frame)
    return frames
