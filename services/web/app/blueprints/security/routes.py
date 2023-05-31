import uuid

from flask import request
from flask_login import login_required, current_user, logout_user

from common.utils import is_valid_url
from app.blueprints.security import bp
from app.logic import render, action, flash, session
from app.clients import source_manager
from app.clients.source_manager import session as sm_session
from app.security import auth, secrets


@bp.before_request
@login_required
def before_request():
    pass


@bp.route('/')
@render(template='security/index.html', endpoint='security.index')
def index():
    if 'tmp' in session:
        sm_secret = session['tmp']
        del session['tmp']
        return {
            'sm_secret': sm_secret
        }


@bp.route('/update_password', methods=['POST'])
@action(endpoint='security.index')
def update_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']

    if new_password == '':
        flash(message='New password can\'t be empty.', category='error')
        return
    elif new_password != confirm_new_password:
        flash(message='Passwords don\'t match.', category='error')
        return
    elif old_password == new_password:
        flash(message='New password must be different from old one.',
              category='error')
        return

    if not secrets.verify(old_password, current_user.db.password):
        flash(message='Incorrect password.', category='error')
        return

    sm_secret = current_user.db.source_manager.secret
    sm_secret = secrets.decrypt(sm_secret, old_password)
    sm_secret = secrets.encrypt(sm_secret, new_password)
    current_user.db.password.source_manager.secret = sm_secret
    current_user.db.password = secrets.hash(new_password)
    current_user.db.password.save()

    logout_user()

    flash(message='Password updated.', category='success')


@bp.route('/set_source_manager_credentials', methods=['POST'])
@action(endpoint='security.index')
def set_source_manager_credentials():
    user_password = request.form['password']
    if not secrets.verify(user_password, current_user.db.password):
        flash(message='Wrong password.', category='error')
        return

    new_url = request.form['url']
    new_secret = request.form['secret']

    if not is_valid_url(new_url):
        flash(message='Invalid URL.', category='error')
        return

    sm_session.base_url = new_url
    sm_session.secret = new_secret

    current_user.sm_secret = new_secret
    new_secret = secrets.encrypt(new_secret, user_password)
    current_user.db.source_manager.url = new_url
    current_user.db.source_manager.secret = new_secret
    current_user.db.save()

    flash(message='Source manager credentials updated.', category='success')


@bp.route('/update_source_manager_secret', methods=['POST'])
@action(endpoint='security.index')
def update_source_manager_secret():
    user_password = request.form['password']
    if not secrets.verify(user_password, current_user.db.password):
        flash(message='Wrong password.', category='error')
        return

    new_secret = source_manager.security.update_client_secret()
    sm_session.secret = new_secret

    current_user.sm_secret = new_secret
    session['tmp'] = new_secret
    new_secret = secrets.encrypt(new_secret, user_password)
    current_user.db.source_manager.secret = new_secret
    current_user.db.save()

    flash(message='Source manager secret updated.', category='success')


@bp.route('/invalidate_source_manager_secret', methods=['POST'])
@action(endpoint='security.index')
def invalidate_source_manager_secret():
    user_password = request.form['password']
    if not secrets.verify(user_password, current_user.db.password):
        flash(message='Wrong password.', category='error')
        return

    source_manager.security.invalidate_client_secret()
    sm_session.secret = ''

    current_user.sm_secret = ''
    current_user.db.source_manager.secret = secrets.encrypt('', user_password)
    current_user.db.save()

    flash(message='Source manager secret invalidated.', category='success')
