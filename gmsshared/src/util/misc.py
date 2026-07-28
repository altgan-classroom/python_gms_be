import gzip
import logging
from http import HTTPStatus
from typing import Any

import sqlalchemy
from flask import jsonify, make_response, Response, current_app
from flask.wrappers import Response as FlaskResponse

from gmsshared.src.config import get_config
from typing import Any, List
import logging
import flask
import gzip
from datetime import datetime, date
from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails
from gmsshared.src.util.exceptions import FileFormatError, FileSizeError, ApiUnauthorized, ApiForbidden
from gmsshared.src.util.enums import ResponseStatusEnum

logger = logging.getLogger(__name__)


def create_response(status_code: int, status: ResponseStatusEnum, message: str, data: Any = {},
                    logger_name: str = None) -> Response:
    logger.name = logger_name if logger_name else logger.name
    if status == "fail":
        logger.warning(message)
    else:
        logger.info(message)
    response = make_response(jsonify(status=status.value, message=message, data=data))
    response.status_code = status_code
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def create_report_response(status_code: int, message: str, data: Any = {}, logger_name: str = None,
                           filename: str = None) -> Response:
    logger.name = logger_name if logger_name else logger.name
    logger.info(message)

    response = make_response(data)
    response.status_code = status_code
    response.content_type = 'text/csv'
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    if filename:
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def handle_exceptions(e: Exception) -> Response:
    exception_message = f"API exception: {e}"
    if hasattr(e, "code"):
        exception_message = f"{exception_message}, error code: {e.code}"
    if hasattr(e, "description"):
        exception_message = f"{exception_message}, error code: {e.description}"
    logger.error(exception_message)

    if isinstance(e, ApiUnauthorized) or isinstance(e, ApiForbidden):
        return handle_authorization_errors(e)
    if isinstance(e, ValidationError):
        return handle_model_validation_errors(e)
    if isinstance(e, FileFormatError) or isinstance(e, FileSizeError):
        return handle_payload_validation_errors(e)
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return create_response(status_code=status_code, status=ResponseStatusEnum.INTERNAL_ERROR, logger_name=__name__,
                           message=exception_message)


def handle_authorization_errors(e: ApiUnauthorized | ApiForbidden) -> Response:
    logger.error(f"Authorization errors: {e}")
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UNAUTHORIZED,
        logger_name=__name__,
        message=f"Access to this resource is unauthorized/forbidden",
    )


def handle_payload_validation_errors(e: ValidationError) -> Response:
    logger.error(f"Error on payload validation: {e}")
    return create_response(
        status_code=HTTPStatus.BAD_REQUEST,
        status=ResponseStatusEnum.ERROR,
        logger_name=__name__,
        message=f"Payload validation error: {e}",
    )


def handle_model_validation_errors(e: FileFormatError | FileSizeError) -> Response:
    params = None
    if e.body_params is not None:
        params = e.body_params
    if e.form_params is not None:
        params = e.form_params
    if e.query_params is not None:
        params = e.query_params
    params_message = (f", with parameters: {params}" if params else "")
    logger.error(f"Error on model validation: {e}{params_message}")
    error_message = f"Errors on paylod model found on payload keys:{params[0]['loc'][0]}, message contents:{params[0]['msg']}"
    return create_response(status_code=HTTPStatus.BAD_REQUEST, status=ResponseStatusEnum.INTERNAL_ERROR,
                           logger_name=__name__,
                           message=error_message)


class ValidationErrorModel(BaseModel):
    status: str
    message: str


def validation_error_callback(e: ValidationError) -> FlaskResponse:
    print(f"{e.error_count()} error(s) found on validation with details: {e}")

    def create_error_message(err: ErrorDetails):
        return {
            "type": err.get("type"),
            "location": err.get("loc"),
            "message": err.get("msg"),
            "input": err.get("input"),
        }

    errors_message = [create_error_message(err) for err in e.errors(include_input=True)]
    message: str = f"{e.error_count()} error(s) found on validation: {errors_message}"
    validation_error_object = ValidationErrorModel(status=ResponseStatusEnum.INVALID_REQUEST, message=message)
    response = make_response(validation_error_object.json())
    response.headers["Content-Type"] = "application/json"
    response.status_code = getattr(current_app, "validation_error_status", 422)
    return response


def compress(response) -> Response:
    accept_encoding = flask.request.headers.get('accept-encoding', '').lower()
    if (response.status_code < 200) or (response.status_code >= 300) or response.direct_passthrough \
            or ('gzip' not in accept_encoding) or ('Content-Encoding' in response.headers):
        return response
    content = gzip.compress(response.get_data(),
                            compresslevel=6)  # 0: no compression, 1: fastest, 9: slowest. Default: 9
    response.set_data(content)
    response.headers['content-length'] = len(content)
    response.headers['content-encoding'] = 'gzip'
    return response


def fill_model(src: Any, dest: Any, exclude: List[str], ignore_nulls: False) -> Any:
    from gmsshared import db
    exclude.extend(['_sa_instance_state', 'create_datetime', 'update_datetime'])
    attrs = {}
    if isinstance(src, BaseModel):
        attrs = src.model_dump().items()
    elif isinstance(src, db.Model):
        attrs = src.__dict__.items()

    for attr in attrs:
        if isinstance(attr[0], List):
            continue

        if attr[0] not in exclude and not (attr[1] is None and ignore_nulls):
            dest.__setattr__(attr[0], attr[1])
    return dest

#TODO: Stopgap fix! Merge this with fill_model and delete this.
def copy_model_to_model(src: Any, dest: Any, exclude: List[str]) -> Any:
    exclude.extend(['_sa_instance_state', 'query', 'query_class', 'registry', 'create_datetime', 'update_datetime'])

    for column in src.__table__.columns:
        if column.key not in exclude:
            dest.__setattr__(column.key, src.__getattribute__(column.key))
    return dest


def row2dict(row, include: List[str]):
    attribs_to_exclude = list({'id', 'create_datetime', 'update_datetime'} - set(include))
    if isinstance(row, sqlalchemy.RowMapping):
        return {
            key: (
                value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime)
                else value.strftime("%Y-%m-%d") if isinstance(value, date)
                else value
            )
            for key, value in row.items()
        }
    d = {}
    for column in row.__table__.columns:
        if column.name not in attribs_to_exclude:
            d[column.name] = str(getattr(row, column.name))
    return d
