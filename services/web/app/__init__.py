from typing import Optional

from flask import Flask
from flask_login import LoginManager

from common.config import settings
from app.security import auth
from app.clients import source_manager


def create_app():
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=settings.web.max_content_length,
        UPLOAD_EXTENSIONS=settings.web.upload_extensions,
        SECRET_KEY=settings.web.secret_key,
    )

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(token: str) -> Optional[auth.UserSession]:
        """
        Load user from JWT token, set source manager credentials

        'load_user' argument is a user ID, which according to Flask-Login docs
        can be any unique string. In our case, it's a JWT token,
        which is able to store more information than just a user ID.
        """
        user_session = auth.UserSession.from_token(token)
        if user_session:
            source_manager_base_url = user_session.db_user.source_manager.url
            source_manager_api_key = user_session.source_manager_api_key
            source_manager.session.base_url = source_manager_base_url
            source_manager.session.state['api_key'] = source_manager_api_key
        return user_session

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.blueprints.sources import bp as sources_bp
    app.register_blueprint(sources_bp, url_prefix='/sources')

    from app.blueprints.search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

    return app
