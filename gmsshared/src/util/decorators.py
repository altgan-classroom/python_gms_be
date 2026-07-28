"""Decorators that verify authorization, validate permissions etc."""
from dataclasses import fields
import json
from dataclasses import fields
from datetime import datetime, date
from functools import wraps
from typing import List
from http import HTTPStatus
from zoneinfo import ZoneInfo
import json
import pytz
from amqp.spec import method
from flask import request, g
from pydantic import BaseModel
from gmsshared import get_config
from enum import Enum
from gmsshared.src.config import Config
from gmsshared.src.models.user import User
from gmsshared.src.util.enums import RoleEnum
from gmsshared.src.util.exceptions import ApiUnauthorized, ApiForbidden, DoorAccessException
from gmsshared.src.util.validators import to_local
import gmsshared.src.util.validators as validators
from gmsshared.src.models.report import Report
from gmsshared.src.models.update_log import UpdateLog
from gmsshared.src.models.door_access_log import DoorAccessLog
from gmsshared.src.util.enums import HttpRequestTypeEnum
from gmsshared.src.util.validators import to_utc
from gmsshared.src.util.validators import to_utc as convert_to_utc
from flask import Response

from datetime import datetime, date
import json

def _update_log(actor_user_id, response, **kwargs):
    try:
        location_id = request.view_args.get('location_id', None)
        target_user_id = (
            request.view_args.get('user_id') or
            request.view_args.get('member_id') or
            getattr(kwargs.get('body', {}), 'member_id', None) or
            getattr(kwargs.get('body', {}), 'user_id', None)
        )
        request_body = kwargs.get('body', {})

        if hasattr(request_body, "model_dump"):
            model_data = request_body.model_dump()
            for key, value in model_data.items():
                if isinstance(value, (datetime, date)):
                    utc_time = convert_to_utc(value)
                    model_data[key] = utc_time.isoformat() if isinstance(utc_time, datetime) else utc_time
                if isinstance(value, Enum):
                    model_data[key] = model_data[key].value
            request_body = json.dumps(model_data)
        elif isinstance(request_body, dict):
            for key, value in request_body.items():
                if isinstance(value, (datetime, date)):
                    request_body[key] = convert_to_utc(value)
            request_body = json.dumps(request_body)
        else:
            raise ValueError("Unsupported type for request_body.")
        if isinstance(response, Response):
            try:
                raw_response = response.response[0].decode('utf-8') if response.response else None
                response_data = json.loads(raw_response)  # Convert to dictionary if JSON
            except (IndexError, AttributeError, json.JSONDecodeError):
                response_data = raw_response or "Invalid Response Format"
        else:
            response_data = str(response)

        serialized_response = json.dumps(response_data)
        log_update = UpdateLog(location_id=location_id, target_user_id=target_user_id, request_body=request_body,
                               actor_user_id=actor_user_id, method=request.method, request_url=request.url, response=serialized_response)
        log_update.save_and_commit()
    except Exception as e:
        pass

def check_access(roles=None, return_role=False, return_user_id=False):
    def decorate(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            token_payload = _check_access_token()
            user = _check_user(int(token_payload['user_id']))
            _check_roles(user, roles)
            _check_location_access(user)
            for name, val in token_payload.items():
                setattr(decorated, name, val)
                if return_role:
                    kwargs["user_role"] = user.role.name.upper()
                if return_user_id:
                    kwargs["user_id"] = user.id
            response = fn(*args, **kwargs)
            if request.method != "GET":
                _update_log(token_payload['user_id'], response, **kwargs)
            return response
        return decorated
    return decorate

def _check_location_access(user: User) -> None:
    try:
        if ('gym_id' in request.args):
            gym_id = request.args['gym_id']
            if int(gym_id) not in [location.gym.id for location in user.locations]:
                raise ApiForbidden(f"You are not authorized to access Gym id: {gym_id}")

        if ('location_id' not in request.view_args):
            return

        location_id = int(request.view_args['location_id'])
        location = [loc for loc in user.locations if loc.id == location_id][0]
        g.setdefault('timezone', location.timezone.iana_tzdata)
        g.setdefault('today_date', to_local(datetime.utcnow()))
        if location_id not in [location.id for location in user.locations]:
            raise ApiForbidden(f"You are not authorized to access Location id: {location_id}")
    except Exception as e:
        raise ApiForbidden(f"You are not authorized to access Gym or Location")

def _check_user(user_id: int) -> User:
    user = User.find_by_id(user_id)
    if not user:
        raise ApiUnauthorized(f"User {user_id} not found")
    g.setdefault('user', user)
    return user


def _check_roles(user: User, roles: List[RoleEnum]) -> None:
    if isinstance(roles, (list, tuple)):  # make a list of roles
        roles = roles
    elif roles is not None:
        roles = [roles]
    else:
        return

    if len(set(roles).intersection([user.role.name.upper()])) == 0:  # check if they have the role
        raise ApiForbidden(description="You do not have the proper role to access this resource")


def _check_access_token() -> dict[str, str]:
    token = request.headers.get("Authorization")
    if not token:
        raise ApiUnauthorized(description="Unauthorized", error="No token found")
    result, token_dict = User.decode_token(token)
    if result.failure or token_dict['type'] != 'access_token':
        raise ApiUnauthorized(description=result.error, error="Invalid token", error_description=result.error, )
    return result.value

def to_utc(fields=None):
    def decorate(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            model = None
            if ('query' in kwargs.keys() and isinstance(kwargs['query'], BaseModel)):
                model = kwargs['query']

            if ('body' in kwargs.keys() and isinstance(kwargs['body'], BaseModel)):
                model = kwargs['body']

            if model:
                _process_model(model, fields, **kwargs)

            return fn(*args, **kwargs)
        return decorated
    return decorate

def _process_model(model, fields, **kwargs):
    for field in fields:
        if field not in model.model_fields:
            continue

        value = model.__getattribute__(field)
        if isinstance(value, datetime):
            model.__setattr__(field, validators.to_utc(value))

        if isinstance(value, str):
            model.__setattr__(field, validators.to_utc(value).strftime("%H:%M"))


def check_report_access():
    def decorate(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            report_id = request.view_args.get('report_id')
            user = g.get("user")
            _check_report_access(user, int(report_id))
            response = fn(*args, **kwargs)
            return response
        return decorated
    return decorate


def _check_report_access(user: User, report_id: int) -> None:
    report = Report.find_by_id(environment=get_config().ENV, id=report_id)
    if not report:
        raise ApiForbidden(f"Report {report_id} not found")

    allowed_roles = [role.name.upper() for role in report.roles]
    user_role = user.role.name.upper()

    if user_role not in allowed_roles:
        raise ApiForbidden(f"You are not authorized to access Report {report_id}")


def door_access_logger(resource_type_id):
    def decorate(fn):
        @wraps(fn)
        def log(*args, **kwargs):
            location_id = kwargs.get("location_id")
            if not location_id:
                location_id = kwargs.get("location").id if kwargs.get("location") else None
            try:
                # door_access tasks return a dict of api_response, result(to pass it on to next tasks), user_id, resource_id
                res = fn(*args, **kwargs)
                response = res.get("response", None)
                result = res.get("result", None)
                user_id = res.get("user_id", None)
                resource_id = res.get("resource_id", None)
                json_response = None
                try:
                    json_response = response.json()
                except Exception as e:
                    pass
                if response is None: return result
                if response.request.method == "GET": return result
                DoorAccessLog.insert(
                    location_id,
                    user_id,
                    resource_type_id,
                    resource_id,
                    HttpRequestTypeEnum[response.request.method].value,
                    response.request.url,
                    response.request.body,
                    json_response,
                    response.status_code,
                    None,
                    response.elapsed.total_seconds(),
                )
                return result
            except DoorAccessException as error:
                DoorAccessLog.insert(
                    location_id,
                    error.user_id,
                    resource_type_id,
                    error.resource_id,
                    HttpRequestTypeEnum.PATCH.value,
                    error.url,
                    error.data,
                    None,
                    HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    error.message,
                    None,
                )
                return False
        return log
    return decorate