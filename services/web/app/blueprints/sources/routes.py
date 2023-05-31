from datetime import datetime
from datetime import timedelta
from urllib.error import HTTPError
import base64
import time

from flask import request, session, flash
from flask_login import login_required

from common.config import settings
from common.constants import SOURCE_STATUS_TO_STR
from common.constants import SourceStatus
from app.blueprints.sources import bp
from app.clients import source_manager
from app.logic import action, render
from app.utils import float_to_color


def sm_rabbitmq_ensure_opened():
    """Ensure that RabbitMQ connection is opened by source manager."""
    if 'sm_rabbitmq' not in session:
        session['sm_rabbitmq'] = {
            'is_opened': source_manager.rabbitmq.is_opened(),
            'last_update': time.time(),
        }
    sm_rabbit_mq = session['sm_rabbitmq']
    since_last_update = time.time() - sm_rabbit_mq['last_update']
    if since_last_update > settings.web.session_state_update_interval:
        sm_rabbit_mq['is_opened'] = source_manager.rabbitmq.is_opened()
        sm_rabbit_mq['last_update'] = time.time()
    if not sm_rabbit_mq['is_opened']:
        source_manager.rabbitmq.startup()
        sm_rabbit_mq['is_opened'] = True


@bp.before_request
@login_required
def before_request():
    pass


@bp.route('/', methods=['GET', 'POST'])
@render(template='sources/index.html', endpoint='sources.index')
def index():
    sm_rabbitmq_ensure_opened()

    search_entry = request.args.get('search_entry', '')
    show_finished = request.args.get('show_finished', 'off')

    sources = source_manager.sources.get_all()
    if show_finished == 'off':
        sources = [
            s for s in sources if s.status_code != SourceStatus.FINISHED
        ]
    if search_entry:
        sources = [s for s in sources if search_entry in s.name]
    sources.sort(key=lambda s: s.name)
    sources.sort(key=lambda s: s.status_code != SourceStatus.ACTIVE)
    statuses = [SOURCE_STATUS_TO_STR[s.status_code] for s in sources]

    session['sources.index'] = {
        'search_entry': search_entry,
        'show_finished': show_finished
    }
    return {
        'sources_with_status': zip(sources, statuses)
    }


@bp.route('rabbitmq/startup', methods=['POST'])
@action(endpoint='sources.index')
def rabbitmq_startup():
    source_manager.rabbitmq.startup()


@bp.route('/add', methods=['POST'])
@action(endpoint='sources.index')
def add():
    name = request.form['name']
    url = request.form['url']
    file = request.files['file']
    if name == '':
        flash(message='Source name can\'t be empty.', category='error')
    elif file:
        source_manager.sources.creare_from_file(
            name, file.filename, file.read()
        )
    else:
        source_manager.sources.create_from_url(name, url)


@bp.route('/start/<int:id>', methods=['POST'])
@action(endpoint='sources.index')
def start(id: int):
    source_manager.sources.start(id)


@bp.route('/start/all', methods=['POST'])
@action(endpoint='sources.index')
def start_all():
    source_manager.sources.start_all()


@bp.route('/pause/<int:id>', methods=['POST'])
@action(endpoint='sources.index')
def pause(id: int):
    source_manager.sources.pause(id)


@bp.route('/pause/all', methods=['POST'])
@action(endpoint='sources.index')
def pause_all():
    source_manager.sources.pause_all()


@bp.route('/finish/<int:id>', methods=['POST'])
@action(endpoint='sources.index')
def finish(id: int):
    source_manager.sources.finish(id)


@bp.route('/delete/<int:id>', methods=['POST'])
@action(endpoint='sources.index')
def delete(id: int):
    source_manager.sources.delete(id)


@bp.route('/<int:id>', methods=['GET'])
@render(template='sources/source.html')
def source(id: int):
    source = source_manager.sources.get(id)
    status = SOURCE_STATUS_TO_STR[source.status_code]

    try:
        frame = source_manager.videos.get_last_frame(id)
        frame = base64.b64encode(frame).decode('utf-8')
    except HTTPError:
        frame = None

    intervals = source_manager.sources.get_time_coverage(id)
    day_coverage = {}
    for (start, end) in intervals:
        dt = datetime.fromtimestamp(start)
        day_coverage[dt.date()] = day_coverage.get(dt.date(), 0) + end - start
    if day_coverage:
        for day, count in day_coverage.items():
            cov = count / 24 / 60 / 60
            cov = cov * 0.8 + 0.2
            day_coverage[day] = cov

    calendar = []
    row = [{'day': None, 'color': None} for _ in range(7)]
    for i in range(30, -1, -1):
        dt = datetime.now() - timedelta(days=i)
        cov = day_coverage.get(dt.date(), 0)
        row[dt.weekday()]['day'] = dt.day
        row[dt.weekday()]['color'] = f'rgb{float_to_color(cov)}'
        if dt.weekday() == 6 or i == 0:
            calendar.append(row)
            row = [{'day': None, 'color': None} for _ in range(7)]

    return {
        'source': source,
        'status': status,
        'frame': frame,
        'calendar': calendar,
    }
