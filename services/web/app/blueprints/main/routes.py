from datetime import timedelta

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from redis_om import NotFoundError

from common.config import settings
from app.blueprints.main import bp
from app.security import secrets, auth
from app import logic
from app.database import models
from app.clients import source_manager


def validate_login_form(username: str, password: str) -> tuple[bool, str]:
    """
    Validate login/register form data (username and password).

    Parameters:
    - username (str): username
    - password (str): password

    Returns:
    - bool: True if form data is valid, False otherwise
    - str: reason why form data is invalid
    """
    if len(username) < settings.web.username_min_length or \
            len(username) > settings.web.username_max_length:
        reason = 'Username must be between {} and {} characters long'.format(
            settings.web.username_min_length,
            settings.web.username_max_length
        )
        return False, reason
    if len(password) < settings.web.password_min_length or \
            len(password) > settings.web.password_max_length:
        reason = 'Password must be between {} and {} characters long'.format(
            settings.web.password_min_length,
            settings.web.password_max_length
        )
        return False, reason
    if username.startswith(' ') or username.endswith(' '):
        reason = 'Username must not start or end with a space'
        return False, reason
    if password.startswith(' ') or password.endswith(' '):
        reason = 'Password must not start or end with a space'
        return False, reason
    return True, ''


@bp.route('/')
def index():
    return render_template('main/index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('main/login.html')

    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Check if user credentials meet the basic requirements
    valid, reason = validate_login_form(username, password)
    if not valid:
        flash(reason, 'error')
        return redirect(url_for('main.login'))

    # Check if user exists
    try:
        db_user = models.User.find(models.User.username == username).first()
    except NotFoundError:
        flash('Incorrect username or password', 'error')
        return redirect(url_for('main.login'))

    # Check if password is correct
    if not secrets.verify(password, db_user.password_hash):
        flash('Incorrect username or password', 'error')
        return redirect(url_for('main.login'))

    # Retrieve source manager url and api key from database
    source_manager_api_key = secrets.decrypt(
        db_user.source_manager.api_key_encrypted, password
    )
    source_manager.session.base_url = db_user.source_manager.url
    source_manager.session.state['api_key'] = source_manager_api_key

    # Check if source manager is registered, if not, register it
    # This may happen if the source manager credentials file was deleted or
    # the source manager was manually unregistered
    try:
        if not source_manager.is_registered():
            api_key, client_id, client_secret = source_manager.register()
            api_key_encrypted = secrets.encrypt(api_key, password)
            client_secret_hash = secrets.hash(client_secret)
            db_user.source_manager.api_key_encrypted = api_key_encrypted
            db_user.source_manager.client_id = client_id
            db_user.source_manager.client_secret_hash = client_secret_hash
            db_user.save()
            source_manager_api_key = api_key
    except Exception as e:
        flash('Failed to register source manager: {}'.format(e), 'error')
        return redirect(url_for('main.login'))

    # Create JWT access token
    token_expires = timedelta(
        minutes=settings.web.jwt_access_token_expire_minutes
    )
    token = auth.create_access_token(
        data={
            'user_pk': db_user.pk,
            'source_manager_api_key': source_manager_api_key},
        expires_delta=token_expires,
    )

    # Create user session and log user in
    user = auth.UserSession(
        token=token,
        db_user=db_user,
        source_manager_api_key=source_manager_api_key,
    )
    login_user(user, remember=remember)

    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('main/register.html')

    username = request.form.get('username')
    password = request.form.get('password')
    source_manager_url = request.form.get('source_manager_url')

    # Check if user credentials meet the basic requirements
    valid, reason = validate_login_form(username, password)
    if not valid:
        flash(reason, 'error')
        return redirect(url_for('main.register'))

    # Check if username is already taken
    try:
        models.User.find(models.User.username == username).first()
        flash('User already exists', 'error')
        return redirect(url_for('main.register'))
    except NotFoundError:
        pass

    # Check if source manager is already registered by another user, if not
    # register it
    source_manager.session.base_url = source_manager_url
    try:
        if source_manager.is_registered():
            flash('Source manager is already registered', 'error')
            return redirect(url_for('main.register'))
        sm_api_key, sm_client_id, sm_client_secret = source_manager.register()
    except Exception as e:
        flash(f'Failed to communicate with source manager: {e}', 'error')
        return redirect(url_for('main.register'))

    # Save user to database
    db_user = models.User(
        username=username,
        password_hash=secrets.hash(password),
        source_manager=models.SourceManager(
            url=source_manager_url,
            api_key_encrypted=secrets.encrypt(sm_api_key, password),
            client_id=sm_client_id,
            client_secret_hash=secrets.hash(sm_client_secret),
        ),
    )
    db_user.save()

    return redirect(url_for('main.login'))


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
@logic.action(endpoint='main.index')
def logout():
    logout_user()


@bp.route('/unregister', methods=['POST'])
@login_required
@logic.action(endpoint='main.index')
def unregister():
    models.User.delete(current_user.db_user.pk)
    source_manager.unregister()
    logout_user()


@bp.route('/profile')
@login_required
@logic.render('main/profile.html')
def profile():
    source_manager_status = 'Online'
    try:
        if not source_manager.is_registered():
            source_manager_status = 'Unregistred, please relogin'
    except Exception:
        source_manager_status = 'Offline'
    return {
        'source_manager_status': source_manager_status,
    }
