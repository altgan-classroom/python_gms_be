import http
from typing import List, Type, Any

from flask import Response, make_response
from pydantic import BaseModel

from gmsshared.src.util.enums import ResponseStatusEnum
from gmsshared.src.util.misc import logger


class BaseResponse(BaseModel):
    status: ResponseStatusEnum
    status_code: int
    message: str
    data: dict | str | bytes | None


class BadRequestResponse(BaseResponse):
    status_code: int = http.HTTPStatus.BAD_REQUEST
    status: ResponseStatusEnum = ResponseStatusEnum.ERROR
    message: str = "Payload validation error: <error>"
    data: None


class ServerErrorResponse(BaseResponse):
    status_code: int = http.HTTPStatus.INTERNAL_SERVER_ERROR
    status: ResponseStatusEnum = ResponseStatusEnum.INTERNAL_ERROR
    message: str = "Undefined error on server; contact server administrator"
    data: None


class UnprocessableEntity(BaseResponse):
    status_code: int = http.HTTPStatus.UNPROCESSABLE_ENTITY
    status: ResponseStatusEnum = ResponseStatusEnum.ERROR


default_responses: dict = {200: BaseResponse, 500: ServerErrorResponse, 400: BadRequestResponse, 422: UnprocessableEntity}


class CodeResponse:
    code: int
    response: Type[BaseModel] = None

    def __init__(self, code: int, response: Type[BaseModel] = None):
        self.code = code
        self.response = response


def custom_responses(code_responses: List[CodeResponse]) -> dict:
    responses = default_responses.copy()
    for response in code_responses:
        responses[response.code] = response.response
    return responses

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

def create_pdf_response(status_code: int, message: str, data: Any = {}, logger_name: str = None,
                           filename: str = None) -> Response:
    logger.name = logger_name if logger_name else logger.name
    logger.info(message)

    response = make_response(data)
    response.status_code = status_code
    response.content_type = 'application/pdf'
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    if filename:
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

