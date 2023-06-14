from common.config import settings
from common import schemas
from app.blueprints.api import bp
from app.security.auth import source_manager_auth_required


@bp.route('/rabbitmq_credentials', methods=['GET'])
@source_manager_auth_required
def rabbitmq_credentials():
    """
    Get RabbitMQ credentials for the source manager.

    Returns:
    - schemas.RabbitMQCredentials: RabbitMQ credentials
    """
    # TODO: create new RabbitMQ user for each source manager
    text = schemas.RabbitMQCredentials(
        host=str(settings.rabbitmq.host),
        port=settings.rabbitmq.port,
        virtual_host=settings.rabbitmq.virtual_host,
        username=settings.rabbitmq.source_manager_username,
        password=settings.rabbitmq.source_manager_password,
    ).json()
    status_code = 200
    headers = {'Content-Type': 'application/json'}
    return text, status_code, headers
