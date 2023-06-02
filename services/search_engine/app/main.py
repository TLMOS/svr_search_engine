from typing import Optional

from fastapi import FastAPI
from redis_om import Migrator
import numpy as np

from common import schemas
from app.models import Embedding
from app.clients import encoder as text_encoder
from app.utils import euclidean_distance


description = """
TODO: Add description
"""


app = FastAPI(
    title='SVR Search Engine API',
    description=description,
    version='0.0.1',
    license_info={
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/mit-license.php'
    }
)


@app.get(
    '/search',
    response_model=list[schemas.Frame],
    summary='TODO',
    response_description='TODO'
)
async def search(
    sm_name: str,
    text: str,
    top_k: int = 10,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> list[schemas.Frame]:
    expression = Embedding.sm_name == sm_name
    if start_time is not None:
        expression &= Embedding.timestamp >= start_time
    if end_time is not None:
        expression &= Embedding.timestamp <= end_time
    db_embeddings = Embedding.find(expression).all()

    if len(db_embeddings) == 0:
        return []

    image_embeddings = np.array([
        np.frombuffer(bytes.fromhex(e.features), dtype=np.float32)
        for e in db_embeddings
    ])

    text_embedding = text_encoder.encode(text)

    scores = euclidean_distance(text_embedding, image_embeddings)
    top_k_indices = np.argsort(scores)[:top_k]

    return [
        schemas.Frame(
            source_id=db_embeddings[i].source_id,
            timestamp=db_embeddings[i].timestamp,
        )
        for i in top_k_indices
    ]


Migrator().run()
