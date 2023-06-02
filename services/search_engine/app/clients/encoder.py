from typing import Optional

import numpy as np

from common.config import settings
from common.http_client import ClientSession


session = ClientSession(settings.encoder.url)


def encode(text: str) -> Optional[np.ndarray]:
    """
    Encode text into an embedding vector.

    Parameters:
    - text (str): text to encode

    Returns:
    - np.ndarray: embedding vector
    """
    response = session.request('GET', '/encode', params={'text': text})
    if response.status_code == 200:
        return np.frombuffer(bytes.fromhex(response.json()['encoded']), dtype=np.float32)
