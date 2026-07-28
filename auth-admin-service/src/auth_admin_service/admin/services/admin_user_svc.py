import logging
from datetime import datetime
from http import HTTPStatus
from typing import List

from flask import Response, current_app

from auth_admin_service.admin.dtos.admin_requests import (
    CreateUserRequest,
    UpdateUserRequest,
    UpdateStaffProfileRequest,
    UserType,
)
from auth_admin_service.admin.dtos.admin_responses import UserResponse, ProfileInfoResponse
from auth_admin_service.auth.dtos.auth_responses import UserInfoResponse
from gmsshared import db, get_config, celery
from gmsshared.src.models._ref_permission_type import _RefPermissionType
from gmsshared.src.models.user import User, user_location
from gmsshared.src.models.user_profile import UserProfile
from gmsshared.src.util.enums import ResponseStatusEnum, RoleEnum
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.datetime_util import utc_now


def get_user_list(location_id: int, query: UserType) -> Response:
    users_list: List[User]
    if query.roles:
        roles = f"({','.join([str(role) for role in query.roles])})"
        users_list = User.find_by_location_and_role(location_id, roles)
    else:
        if query.active_only is not None:
            users_list = User.find_by_location(location_id, active_only=query.active_only)
        else:
            users_list = User.find_by_location(location_id)
    if not users_list:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No users found",
        )
    users: List[dict]
    users = [UserResponse.model_validate(dict(user), from_attributes=True).model_dump() for user in users_list]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message=f"{len(users)} users found",
        data=users,
    )


# TODO: Clean this up. Make it better with error handling
def create_user(location_id: int, body: CreateUserRequest, skip_verification: bool = False) -> Response:
    message = "Created new user"
    user = User.find_by_email(body.email)
    if user:
        if user.active:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.CONFLICT,
                logger_name=__name__,
                message=f"Email {user.email} already exists",
            )
        else:
            user_profile = user.user_profile
            message = "Re-added User"
    else:
        user = User(email=body.email, password=body.password if body.password else "Test@1234")
        user_profile = UserProfile(body.first_name, body.last_name)
    _fill_user(user_profile, body)
    user.user_profile = user_profile
    user.role_type_id = body.role_type_id
    if skip_verification:
        user.active = True
        user.verified = True
        user.verified_on = utc_now()
    else:
        user.active = False
        user.verified = False
    user.deactivated_on = None
    user.save_and_commit()
    exist_user_location = User.find_by_location_and_user(user_id=user.id, location_id=location_id)
    if not exist_user_location:
        db.session.execute(user_location.insert(), params={"location_id": location_id, "user_id": user.id})
        db.session.commit()
    if not skip_verification and get_config().EMAIL_CONFIRMATION is not False:
        send_staff_account_verification_email(user)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message=message,
    )


def activate_kiosk_user(user_id: int) -> Response:
    user = User.find_by_id(user_id)
    user.active = True
    user.deactivated_on = None
    user.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Activated Kiosk User",
    )


def get_user_info(user_id: int, location_id: int) -> Response:
    user = User.find_by_location_and_user(user_id, location_id)
    if not user:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="User not found",
        )
    data = UserInfoResponse.model_validate(user, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="User found",
        data=data,
    )


def update_user_info(user_id: int, body: UpdateUserRequest) -> Response:
    user = User.find_by_location_and_user(user_id, body.location_id)
    if not user:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="User not found",
        )
    if body.permissions:
        user.permissions = [_RefPermissionType.find_by_id(permission_id) for permission_id in body.permissions]
    if body.password:
        user.password = body.password
    user.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="User info updated",
    )


def delete_user_info(location_id, user_id: int) -> Response:
    user = User.find_by_location_and_user(user_id, location_id)
    if not user or user.deactivated_on is not None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="User not found",
        )
    if user.role_type_id == RoleEnum.OWNER.value:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message=f"User: {user.email} is owner and cannot be deleted",
        )
    try:
        user.active = False
        user.deactivated_on = datetime.utcnow()
        user.save_and_commit()
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.DELETED,
            logger_name=__name__,
            message="User successfully deleted",
        )
    except Exception as e:
        logging.error(f"Error deleting user with ID {user_id}: {e}")
        return create_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            status=ResponseStatusEnum.INTERNAL_ERROR,
            logger_name=__name__,
            message="Error deleting user",
        )


def update_staff_profile_info(
    location_id: int, user_id: int, user_role: str, body: UpdateStaffProfileRequest
) -> Response:
    if not (user_role == RoleEnum.OWNER.name or user_role == RoleEnum.MANAGER.name):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UNAUTHORIZED,
            logger_name=__name__,
            message="Only Gym owners or managers can update the staff profile information",
        )
    user = User.find_by_location_and_user(user_id, location_id)
    if not user:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Profile not found",
        )

    user_profile: UserProfile = user.user_profile
    _user_location: User = User.find_by_location_and_user(user.id, location_id)

    if user_profile and _user_location:
        _fill_staff_profile_info(user_profile, body)
        user.active = body.active if body.active is not None else user.active
        user.user_profile = user_profile
        user.role_type_id = body.role_type_id
        user.email = body.email
        user.verified_on = body.verified_on
        user.verified = True if body.verified_on is not None else user.verified
        user.save_and_commit()
        user_profile.start_date = body.start_date if body.start_date is not None else user_profile.start_date
        user_profile.photo_url = body.photo_url
        user_profile.save_and_commit()

        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UPDATED,
            logger_name=__name__,
            message="Profile info updated",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.INTERNAL_ERROR,
        logger_name=__name__,
        message="Error updating profile",
    )


def get_profile_info(user_id: int, location_id: int) -> Response:
    profile_info: User = User.get_staff_profile_info_by_id(user_id, location_id)
    if not profile_info:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="User not found",
        )
    profile_response: ProfileInfoResponse = ProfileInfoResponse.model_validate(profile_info, from_attributes=True)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="User found",
        data=profile_response.model_dump(),
    )


def _fill_staff_profile_info(profile: UserProfile, body: UpdateStaffProfileRequest):
    for attr in body.model_dump().items():
        profile.__setattr__(attr[0], attr[1])
    profile.save_and_commit()


def _fill_user(user_profile: UserProfile, body: CreateUserRequest):
    # TODO: Clean this up and make it generic
    for attr in body.model_dump().items():
        user_profile.__setattr__(attr[0], attr[1])


def send_staff_account_verification_email(user: User):
    token = User.generate_verification_token(user.email)
    link = f"{get_config().APP_URL}/staff-verify?role={user.role_type_id}&token={token}"
    data = {
        "first_name": user.user_profile.first_name,
        "last_name": user.user_profile.last_name,
        "gym_name": user.locations[0].name,
        "confirmation_link": link,
    }
    celery.send_task("staff_account_verification_email", (user.email, data))


def send_password_reset_email(user: User):
    token = User.generate_verification_token(user.email)
    domain = (
        f"{get_config().STOREFRONT_URL}"
        if user.role_type_id == RoleEnum.MEMBER.value
        else f"{get_config().APP_URL}"
    )
    path = "members/forgot_password_reset" if user.role_type_id == RoleEnum.MEMBER.value else "forgot_password_reset"
    link = f"{domain}/{path}?role={user.role_type_id}&token={token}"
    data = {
        "first_name": user.user_profile.first_name,
        "last_name": user.user_profile.last_name,
        "gym_name": user.locations[0].name,
        "reset_password_link": link,
    }
    celery.send_task("staff_password_reset_email", (user.email, data))
