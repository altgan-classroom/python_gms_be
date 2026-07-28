"""Shared extensions for the GMS services."""
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from celery import Celery

from gmsshared.src.config import get_config
from gmsshared.src.database import db, engine, SessionLocal  # noqa: F401


cors = CORS()
bcrypt = Bcrypt()

celery = Celery(__name__,
                broker=get_config().BROKER_URI,
                backend=get_config().BACKEND_URI
                )
