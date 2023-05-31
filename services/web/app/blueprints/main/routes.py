from datetime import timedelta

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user
from redis_om import NotFoundError

from common.config import settings
from app.blueprints.main import bp
from app.security import secrets, auth
from app.logic import action
from app.models import User
from app.clients.source_manager import session as sm_session


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

    try:
        db_user = User.find(User.username == username).first()
    except NotFoundError:
        flash('Incorrect username or password', 'error')
        return redirect(url_for('main.login'))

    if not secrets.verify(password, db_user.password):
        flash('Incorrect username or password', 'error')
        return redirect(url_for('main.login'))

    sm_secret = secrets.decrypt(db_user.source_manager.secret, password)

    token_expires = timedelta(
        minutes=settings.security.jwt_access_token_expire_minutes
    )
    token = auth.create_access_token(
        data={'sub': username, 'sm_secret': sm_secret},
        expires_delta=token_expires,
    )

    sm_session.base_url = db_user.source_manager.url
    sm_session.secret = sm_secret

    user = auth.UserSession(db=db_user, sm_secret=sm_secret, token=token)
    login_user(user, remember=remember)

    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('main/register.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('main.register'))

    try:
        if User.find(User.username == username).first():
            flash('User already exists', 'error')
            return redirect(url_for('main.register'))
    except NotFoundError:
        pass

    password_hash = secrets.hash(password)
    user = User(
        username=username,
        password=password_hash,
    )
    user.source_manager.secret = secrets.encrypt(
        user.source_manager.secret, password
    )
    user.save()

    return redirect(url_for('main.login'))


@bp.route('/logout')
@action(endpoint='main.index')
def logout():
    logout_user()
