from http import HTTPStatus
from flask import Response
from gmsshared.src.web.fastapi_glue import g
import boto3

from auth_admin_service.auth.dtos.auth_requests import (
    UpdateUserInfo,
    ChangePasswordRequest,
    UploadRequest,
    ImpersonateRequest,
)
from auth_admin_service.auth.dtos.auth_responses import UserInfoResponse, LoginUserResponse

from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.models.user import User
from gmsshared.src.models.gym import Gym
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.enums import RoleEnum, ResponseStatusEnum


def get_user_info(user_id: int) -> Response:
    user = User.find_by_id(user_id)
    data = UserInfoResponse.model_validate(user, from_attributes=True).model_dump()
    if "impersonator" in g and g.impersonator is not None:
        impersonator = UserInfoResponse.model_validate(g.impersonator, from_attributes=True).model_dump()
        data["permissions"] = impersonator["permissions"]
        data["impersonated"] = True
    user.last_login = utc_now()
    user.save()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="User found",
        data=data,
    )


def update_user_info(user_id: int, body: UpdateUserInfo) -> Response:
    user = User.find_by_id(user_id)
    user.active = body.active
    user.first_name = body.first_name
    user.middle_name = body.middle_name
    user.last_name = body.last_name
    user.photo_url = body.photo_url
    user.dark_mode = body.dark_mode
    user.save()

    data = UserInfoResponse.model_validate(user, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="User info updated",
        data=data,
    )


def change_password_info(user_id: int, body: ChangePasswordRequest):
    user = User.find_by_id(user_id)
    if body.old_password:
        if not user.check_password(body.old_password):
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.ERROR_SETTING_PASSWORD,
                logger_name=__name__,
                message="Invalid old password",
            )
    user.password = body.new_password
    user.save()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Password updated",
    )


def get_presigned_url(user_id: int, query: UploadRequest):
    user = User.find_by_id(user_id)
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=get_config().UPLOAD_S3_KEY,
        aws_secret_access_key=get_config().UPLOAD_S3_SECRET,
        region_name="us-east-1",
    )
    if query.type == "logo":
        key = f"{query.type}/{user.gym[0].id}_gym_{query.name}"
    else:
        key = f"{query.type}/{user_id}_user_{query.name}"
    response = s3_client.generate_presigned_post(
        Bucket=get_config().UPLOAD_S3_BUCKET,
        Key=key,
        ExpiresIn=int(get_config().UPLOAD_URL_EXPIRE),
        Fields={"acl": "public_read"},
        Conditions=[["content-length-range", 0, get_config().UPLOAD_SIZE_LIMIT]],
    )
    response["final_url"] = f"https://{get_config().UPLOAD_S3_BUCKET}/{key}"
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        data=response,
        message="Created presigned url",
    )


def get_impersonation_info(impersonator_id: int, body: ImpersonateRequest):
    impersonator, can_impersonate = _can_impersonate(impersonator_id)
    if not can_impersonate:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UNAUTHORIZED,
            logger_name=__name__,
            message=f"{impersonator.email} is not authorized to impersonate",
        )
    gym = Gym.find_by_id(body.impersonate_gym_id)
    if not gym:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Gym not found",
        )
    user = User.find_owner_by_gym(body.impersonate_gym_id)
    access_token = User.generate_access_token(user.id, impersonator_id)
    refresh_token = User.generate_refresh_token(user.id)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message=f"Impersonation token found for {gym.name}",
        data=LoginUserResponse(access_token=access_token, refresh_token=refresh_token).model_dump(),
    )


def _can_impersonate(impersonator_id: int):
    impersonator = User.find_by_id(impersonator_id)
    if impersonator.role_id not in [RoleEnum.COACH.value, RoleEnum.SUPPORT.value, RoleEnum.VA.value]:
        return impersonator, False
    return impersonator, True
