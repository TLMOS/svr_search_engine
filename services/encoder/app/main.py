from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from transformers import TFCLIPModel, CLIPTokenizer

from common.config import settings


model_id = settings.encoder.model
model = TFCLIPModel.from_pretrained(model_id)
tokenizer = CLIPTokenizer.from_pretrained(model_id)


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
def root():
    """Root endpoint, redirects to docs"""
    return RedirectResponse(url='/docs')


@app.get(
    '/encode',
    summary='Encode text into an embedding vector',
    response_description='Encoded text',
    response_class=Response,
)
def encode(text: str):
    """
    Encode text into an embedding vector.

    Parameters:
    - text (str): text to encode

    Returns:
    - bytes: encoded text
    """
    inputs = tokenizer(text, return_tensors="tf")
    text_embeddings = model.get_text_features(**inputs)
    encoded = text_embeddings[0].numpy().astype('float32').tobytes()
    return Response(
        content=encoded,
        media_type='application/octet-stream'
    )
