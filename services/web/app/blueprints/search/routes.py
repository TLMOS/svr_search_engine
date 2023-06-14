from PIL import Image
import io
import base64
from datetime import datetime

from flask import request, session
from flask_login import login_required, current_user

from common.utils.frontend import (
    draw_bounding_box,
    date_time_form_to_timestamp,
)
from app.blueprints.search import bp
from app import logic
from app.clients import encoder, source_manager
from app.database.frame_search import find


@bp.before_request
@login_required
def before_request():
    pass


@bp.route('/', methods=['GET', 'POST'])
@logic.render(template='search/index.html', endpoint='search.index')
def index():
    search_entry = request.args.get('search_entry', '')
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    time_start = request.args.get('time_start', '')
    time_end = request.args.get('time_end', '')
    top_k = request.args.get('top_k', 5)

    time_start = date_time_form_to_timestamp(date_start, time_start)
    time_end = date_time_form_to_timestamp(date_end, time_end)

    results = []
    if search_entry:
        # Encode text query to CLIP embedding
        query_embedding = encoder.encode(search_entry)

        # Search for frames with similar embeddings
        # (approximate nearest neighbors search)
        frames = find(
            query_embedding=query_embedding,
            top_k=top_k,
            source_manager_id=current_user.db_user.source_manager.client_id,
            time_start=time_start,
            time_end=time_end,
        )

        # Get images for found frames from source manager, draw bounding boxes
        images = []
        for frame in frames:
            image_data = source_manager.videos.get_frame(
                frame.chunk_id,  frame.position
            )
            image = Image.open(io.BytesIO(image_data))
            draw_bounding_box(image, frame.box, (255, 0, 0), 3)
            # Encode image to base64
            encoded = io.BytesIO()
            image.save(encoded, format='PNG')
            encoded = base64.b64encode(encoded.getvalue()).decode('utf-8')
            images.append(encoded)

        # Get source names, convert timestamps to human-readable format
        all_sources = source_manager.sources.get_all()
        name_by_id = {s.id: s.name for s in all_sources}
        for frame in frames:
            frame.source_id = name_by_id[frame.source_id]
            dt = datetime.fromtimestamp(frame.timestamp)
            frame.timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')

        results = zip(frames, images)
    session['search.index'] = {
        'search_entry': search_entry,
    }
    return {'results': results}
