"""Config settings for for development, testing and production environments."""
import os
from dotenv import load_dotenv
from logging.config import dictConfig

load_dotenv()

class Config:
    # Debug settings
    FLASK_DEBUG = bool(eval(os.getenv("FLASK_DEBUG", "False")))
    ENV = os.getenv("ENV", "test")

    # Flask stuff
    PRESERVE_CONTEXT_ON_EXCEPTION = bool(eval(os.getenv("PRESERVE_CONTEXT_ON_EXCEPTION", "False")))
    APP_URL = os.getenv("APP_URL")

    # Security stuff
    SECRET_KEY = os.getenv("SECRET_KEY")
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS"))
    JWT_TOKEN_EXPIRE_HOURS = float(os.getenv("JWT_TOKEN_EXPIRE_HOURS"))
    REFRESH_TOKEN_EXPIRE_DAYS = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    CONFIRM_TOKEN_SALT = os.getenv("CONFIRM_TOKEN_SALT")
    CONFIRM_TOKEN_EXPIRE_SECS = int(os.getenv("CONFIRM_TOKEN_EXPIRE_SECS"))
    PROFILE_SETUP_TOKEN_EXPIRE_SECS = int(os.getenv("PROFILE_SETUP_TOKEN_EXPIRE_SECS"))
    STOREFRONT_URL = os.getenv("STOREFRONT_URL")

    # DB stuff
    SQLALCHEMY_TRACK_MODIFICATIONS = bool(eval(os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False")))
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = bool(eval(os.getenv("SQLALCHEMY_ECHO", "False")))

    # Validation stuff
    FLASK_PYDANTIC_VALIDATION_ERROR_RAISE = bool(eval(os.getenv("FLASK_PYDANTIC_VALIDATION_ERROR_RAISE", "True")))

    # Email confirmation
    EMAIL_CONFIRMATION = bool(eval(os.getenv("EMAIL_CONFIRMATION", "True")))
    EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    # S3 stuff
    UPLOAD_S3_BUCKET = os.getenv("UPLOAD_S3_BUCKET")
    UPLOAD_S3_KEY = os.getenv("UPLOAD_S3_KEY")
    UPLOAD_S3_SECRET = os.getenv("UPLOAD_S3_SECRET")
    UPLOAD_URL_EXPIRE = os.getenv("UPLOAD_URL_EXPIRE")
    UPLOAD_SIZE_LIMIT = os.getenv("UPLOAD_SIZE_LIMIT")

    # Quicksight stuff
    QUICKSIGHT_USER_NAME = os.getenv("QUICKSIGHT_USER_NAME")

    # Broker stuff
    BROKER_URI = os.getenv("BROKER_URI")
    BACKEND_URI = os.getenv("BACKEND_URI")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Payrix stuff
    PAYRIX_APIKEY = os.getenv("PAYRIX_APIKEY")
    PAYRIX_ENDPOINT = os.getenv("PAYRIX_ENDPOINT")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
            },
            "root": {"level": "DEBUG" if FLASK_DEBUG else "ERROR", "handlers": ["console"]},
        }
    )

def get_config():
    return Config
