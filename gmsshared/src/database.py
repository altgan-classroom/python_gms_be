"""Framework-neutral SQLAlchemy layer.

Replaces Flask-SQLAlchemy's `db` object with a plain-SQLAlchemy equivalent that
exposes the SAME surface the codebase already uses (`db.Model`, `db.Column`,
`db.session`, `db.relationship`, `db.Table`, `Model.query`, ...). This lets the
existing models and services run unchanged under BOTH Flask (during the
migration) and FastAPI, and lets Celery workers use a plain session scope
instead of a Flask app context.
"""
import contextvars
import re
import threading
from contextlib import contextmanager

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, declared_attr, scoped_session, sessionmaker

from gmsshared.src.config import get_config


def _camel_to_snake(name: str) -> str:
    """Flask-SQLAlchemy's default table-name algorithm (e.g. _RefRoleType -> _ref_role_type)."""
    name = re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))", r"_\1", name)
    return name.lower()


class _ModelBase:
    """Auto-derives __tablename__ from the class name, like Flask-SQLAlchemy.
    Models that set __tablename__ explicitly still override this."""

    @declared_attr.directive
    def __tablename__(cls):
        return _camel_to_snake(cls.__name__)

engine = create_engine(
    get_config().SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Sync FastAPI endpoints run on pool threads, so a thread-scoped session outlives the request
# and keeps a stale transaction. Key by request instead; non-request code falls back to thread.
request_scope: contextvars.ContextVar = contextvars.ContextVar("gms_db_request_scope", default=None)
session = scoped_session(SessionLocal, scopefunc=lambda: request_scope.get() or threading.get_ident())

# Declarative base + Flask-SQLAlchemy-style `Model.query` (used ~200x as cls.query)
# and auto __tablename__.
_Base = declarative_base(cls=_ModelBase)
_Base.query = session.query_property()


@contextmanager
def session_scope():
    """Session context for non-request code (Celery tasks, scripts)."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.remove()


class _Db:
    """Mimics the Flask-SQLAlchemy `db` namespace used across the codebase."""

    Model = _Base
    metadata = _Base.metadata
    session = session
    engine = engine
    session_scope = staticmethod(session_scope)

    @staticmethod
    def Table(name, *args, **kwargs):
        # Flask-SQLAlchemy's db.Table auto-binds the metadata; plain
        # sqlalchemy.Table needs it as the 2nd positional arg.
        return sqlalchemy.Table(name, _Base.metadata, *args, **kwargs)


db = _Db()

# Re-export every public name from sqlalchemy + sqlalchemy.orm onto db.*
# (db.Column, db.Integer, db.String, db.relationship, db.Table, db.backref, ...).
# Use dir() rather than __all__ — SQLAlchemy's __all__ omits names like Table/Column.
# Assign onto the INSTANCE (not the class) so plain functions like relationship/backref
# don't become bound methods that inject a phantom `self` argument.
for _mod in (sqlalchemy, sqlalchemy.orm):
    for _name in dir(_mod):
        if not _name.startswith("_") and not hasattr(db, _name):
            setattr(db, _name, getattr(_mod, _name))
