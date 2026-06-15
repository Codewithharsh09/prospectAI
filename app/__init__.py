import logging
import os

from flask import Flask

from app.api import register_blueprints
from app.config.settings import config
from app.core.errors import register_error_handlers
from app.extensions import db
from app.middleware.request_middleware import register_middleware
from app.utils.logger import setup_logging

logger = logging.getLogger(__name__)


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    setup_logging(app)

    _validate_env(app)

    db.init_app(app)

    register_middleware(app)
    register_error_handlers(app)
    register_blueprints(app)

    logger.info("Application started", extra={"config": config_name})

    return app


def _validate_env(app: Flask) -> None:
    required = app.config.get("REQUIRED_ENV_VARS", [])
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
