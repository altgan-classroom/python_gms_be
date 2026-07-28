"""FastAPI counterparts to the Flask web glue.

Lets a service run on FastAPI while reusing the existing models/services:
- `g`                     : contextvar-backed replacement for flask.g
- `fastapi_create_response`: same JSON envelope as misc.create_response, as a JSONResponse
- `check_access(roles=...)`: dependency replacing the @check_access decorator
- `install_session_middleware` / `install_exception_handlers`: app wiring
"""
import functools
import inspect
from datetime import datetime
from http import HTTPStatus

from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from gmsshared import db
from gmsshared.src.util import validators
from gmsshared.src.util.enums import ResponseStatusEnum, RoleEnum  # noqa: F401
from gmsshared.src.util.exceptions import ApiUnauthorized, ApiForbidden
from gmsshared.src.models.user import User
from gmsshared.src.web.context import g  # noqa: F401  (re-exported for endpoints/services)


# -------------------------------------------------------------------- response
def fastapi_create_response(status_code, status, message, data=None, logger_name=None):
    """Mirror of misc.create_response: {status, message, data} body + HTTP status_code."""
    if data is None:
        data = {}
    return JSONResponse(
        status_code=int(status_code),
        content={
            "status": status.value if hasattr(status, "value") else status,
            "message": message,
            "data": data,
        },
    )


# ----------------------------------------------------------------- check_access
def _check_access_token(request: Request) -> dict:
    token = request.headers.get("Authorization")
    if not token:
        raise ApiUnauthorized(description="Unauthorized", error="No token found")
    result, token_dict = User.decode_token(token)
    if result.failure or token_dict["type"] != "access_token":
        raise ApiUnauthorized(description=result.error, error="Invalid token")
    return result.value


def _check_user(user_id: int) -> User:
    user = User.find_by_id(user_id)
    if not user:
        raise ApiUnauthorized(f"User {user_id} not found")
    g.setdefault("user", user)
    return user


def _check_roles(user: User, roles) -> None:
    if isinstance(roles, (list, tuple)):
        pass
    elif roles is not None:
        roles = [roles]
    else:
        return
    if len(set(roles).intersection([user.role.name.upper()])) == 0:
        raise ApiForbidden(description="You do not have the proper role to access this resource")


def _check_location_access(user: User, request: Request) -> None:
    """Best-effort port of the Flask location check using FastAPI path/query params."""
    try:
        gym_id = request.query_params.get("gym_id")
        if gym_id is not None:
            if int(gym_id) not in [loc.gym.id for loc in user.locations]:
                raise ApiForbidden(f"You are not authorized to access Gym id: {gym_id}")

        location_id = request.path_params.get("location_id")
        if location_id is None:
            return
        location_id = int(location_id)
        if location_id not in [loc.id for loc in user.locations]:
            raise ApiForbidden(f"You are not authorized to access Location id: {location_id}")
        location = [loc for loc in user.locations if loc.id == location_id][0]
        g.setdefault("timezone", location.timezone.iana_tzdata)
        g.setdefault("today_date", validators.to_local(datetime.utcnow()))
    except ApiForbidden:
        raise
    except Exception:
        raise ApiForbidden("You are not authorized to access Gym or Location")


def to_utc(fields=None):
    """Signature-preserving port of decorators.to_utc for FastAPI endpoints.

    Converts the named datetime/str fields of the `query`/`body` param to UTC
    before the handler runs. __signature__ is preserved so FastAPI can still
    introspect the real parameters."""
    fields = fields or []

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for key in ("query", "body"):
                model = kwargs.get(key)
                if model is not None and hasattr(model, "model_fields"):
                    for field in fields:
                        if field not in model.model_fields:
                            continue
                        value = getattr(model, field)
                        if isinstance(value, datetime):
                            setattr(model, field, validators.to_utc(value))
                        elif isinstance(value, str):
                            setattr(model, field, validators.to_utc(value).strftime("%H:%M"))
            return fn(*args, **kwargs)

        wrapper.__signature__ = inspect.signature(fn)
        return wrapper

    return decorate


# HTTP Bearer scheme — declared purely so Swagger UI renders the Authorize (lock)
# button and adds the `Authorization: Bearer <token>` header to Try-it-out requests.
# auto_error=False keeps the existing _check_access_token flow authoritative (it reads
# the raw header and raises ApiUnauthorized), so behavior is unchanged.
_bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Paste the access_token returned by POST /api/v1.1/auth/login",
)


def check_access(roles=None):
    """FastAPI dependency replacing @check_access(roles=[...])."""

    def _dep(request: Request, _credentials=Depends(_bearer_scheme)):
        token_payload = _check_access_token(request)
        user = _check_user(int(token_payload["user_id"]))
        _check_roles(user, roles)
        _check_location_access(user, request)
        for name, val in token_payload.items():
            g.setdefault(name, val)
        return user

    return _dep


# ----------------------------------------------------------------------- wiring
def install_session_middleware(app) -> None:
    @app.middleware("http")
    async def _session_per_request(request: Request, call_next):
        g.reset()
        try:
            return await call_next(request)
        finally:
            db.session.remove()


def install_exception_handlers(app) -> None:
    @app.exception_handler(ApiUnauthorized)
    async def _unauth(_request, _exc):
        return fastapi_create_response(
            HTTPStatus.OK, ResponseStatusEnum.UNAUTHORIZED,
            "Access to this resource is unauthorized/forbidden",
        )

    @app.exception_handler(ApiForbidden)
    async def _forbid(_request, _exc):
        return fastapi_create_response(
            HTTPStatus.OK, ResponseStatusEnum.UNAUTHORIZED,
            "Access to this resource is unauthorized/forbidden",
        )

    @app.exception_handler(Exception)
    async def _server(_request, exc):
        return fastapi_create_response(
            HTTPStatus.INTERNAL_SERVER_ERROR, ResponseStatusEnum.INTERNAL_ERROR,
            f"API exception: {exc}",
        )
