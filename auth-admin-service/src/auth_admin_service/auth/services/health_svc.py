from http import HTTPStatus

from flask import Response
from sqlalchemy import text

from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.enums import ResponseStatusEnum
from gmsshared import db


def get_auth_health_info() -> Response:
    db.session.execute(text("select 1"))
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="Auth health is good",
    )
