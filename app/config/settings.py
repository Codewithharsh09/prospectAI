import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://localhost/prospectai"
    )
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    REQUIRED_ENV_VARS: list[str] = []


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


class ProductionConfig(BaseConfig):
    DEBUG = False
    REQUIRED_ENV_VARS = ["SECRET_KEY", "DATABASE_URL"]


config: dict[str, type] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
