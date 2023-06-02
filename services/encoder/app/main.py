from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import numpy as np
import torch
import clip

from common.config import settings


model, preprocess = clip.load(settings.encoder.model)


description = """
Small serrvice to encode search entries into embeddings, using CLIP.
"""


app = FastAPI(
    title='SVR Search Engine Text Encoder',
    description=description,
    version='0.0.1',
    license_info={
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/mit-license.php'
    }
)


@app.get('/', include_in_schema=False)
async def root():
    """Root endpoint, redirects to docs"""
    return RedirectResponse(url='/docs')


@app.get('/encode')
async def encode(text: str) -> dict[str, str]:
    """
    Encode text into an embedding vector.

    Parameters:
    - text (str): text to encode

    Returns:
    - dict[str, str]: encoded text

    ```python
    {
        'encoded': 'hex string'
    }
    ```
    """
    text = clip.tokenize([text])
    with torch.no_grad():
        text_features = model.encode_text(text).cpu().numpy()[0]
    print(text_features.shape)
    return {
        'encoded': text_features.astype(np.float32).tobytes().hex()
    }
