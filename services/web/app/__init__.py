from typing import Optional

from flask import Flask
from flask_login import LoginManager
from redis_om import Migrator, NotFoundError

from common.config import settings
from app.security import auth
from app.models import User
from app.clients.source_manager import session as sm_session


def create_app():
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=settings.web.max_content_length,
        UPLOAD_EXTENSIONS=settings.web.upload_extensions,
        SECRET_KEY=settings.security.secret_key,
    )

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(token: str) -> Optional[auth.UserSession]:
        """
        Load user from JWT token.

        'load_user' argument is a user ID, which according to Flask-Login docs
        can be any unique string. In our case, it's a JWT token,
        which is able to store more information than just a user ID.
        """
        token_data = auth.decode_access_token(token)
        if token_data is None:
            return None
        try:
            db_user = User.find(User.username == token_data.username).first()
        except NotFoundError:
            return None

        sm_session.base_url = db_user.source_manager.url
        sm_session.secret = token_data.sm_secret

        return auth.UserSession(
            db=db_user,
            sm_secret=token_data.sm_secret,
        )

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.security import bp as security_bp
    app.register_blueprint(security_bp, url_prefix='/security')

    from app.blueprints.sources import bp as posts_bp
    app.register_blueprint(posts_bp, url_prefix='/sources')

    Migrator().run()

    return app
