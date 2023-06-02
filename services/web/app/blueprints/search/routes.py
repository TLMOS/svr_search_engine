import base64
from datetime import datetime

from flask import request, session
from flask_login import login_required, current_user

from app.blueprints.search import bp
from app.logic import render
from app.clients import search_engine, source_manager


@bp.before_request
@login_required
def before_request():
    pass


@bp.route('/', methods=['GET', 'POST'])
@render(template='search/index.html', endpoint='search.index')
def index():
    search_entry = request.args.get('search_entry', '')
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    time_start = request.args.get('time_start', '')
    time_end = request.args.get('time_end', '')
    top_k = request.args.get('top_k', 5)

    if date_start:
        date_start = datetime.strptime(date_start, '%Y-%m-%d')
    if date_end:
        date_end = datetime.strptime(date_end, '%Y-%m-%d')
    if time_start:
        time_start = datetime.strptime(time_start, '%I:%M %p')
    if time_end:
        time_end = datetime.strptime(time_end, '%I:%M %p')

    if time_start and date_start:
        time_start = datetime.combine(date_start,
                                      time_start.time()).timestamp()
    elif time_start:
        time_start = datetime.combine(datetime.today(),
                                      time_start.time()).timestamp()
    elif date_start:
        time_start = date_start.timestamp()
    else:
        time_start = None

    if time_end and date_end:
        time_end = datetime.combine(date_end,
                                    time_end.time()).timestamp()
    elif time_end:
        time_end = datetime.combine(datetime.today(),
                                    time_end.time()).timestamp()
    elif date_end:
        time_end = date_end.timestamp()
    else:
        time_end = None

    results = []
    if search_entry:
        frames = search_engine.search(
            sm_name=current_user.db.username,
            text=search_entry,
            start_time=time_start,
            end_time=time_end,
            top_k=top_k,
        )

        images = [
            source_manager.videos.get_frame(f.source_id,  f.timestamp)
            for f in frames
        ]

        images = [base64.b64encode(i).decode('utf-8') for i in images]

        all_sources = source_manager.sources.get_all()
        name_by_id = {s.id: s.name for s in all_sources}
        for frame in frames:
            frame.source_id = name_by_id[frame.source_id]

        results = zip(frames, images)
    session['search.index'] = {
        'search_entry': search_entry,
    }
    return {'results': results}
