import datetime
import logging
import re
from http import HTTPStatus
from typing import Optional

from flask import Response, current_app
from kombu.exceptions import OperationalError

from auth_admin_service.admin.dtos.admin_requests import CreateLocationRequest, CreateUserRequest
from auth_admin_service.admin.services.admin_location_svc import create_location
from auth_admin_service.admin.services.admin_user_svc import (
    send_staff_account_verification_email,
    send_password_reset_email,
    create_user,
)
from auth_admin_service.auth.dtos.auth_requests import (
    VerifyEmailRequest,
    VerifyAndSetPassword,
    RefreshAccessTokenRequest,
    RegisterUserRequest,
    VerificationLinkRequest,
)
from auth_admin_service.auth.dtos.auth_responses import RefreshAccessTokenResponse
from auth_admin_service.auth.dtos.auth_responses import LoginUserResponse, ProfileSetupResponse
from gmsshared import db, celery, get_config
from gmsshared.src.models.gym import Gym
from gmsshared.src.models.user import User
from gmsshared.src.models.user_profile import UserProfile
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.util.enums import RoleEnum, ResponseStatusEnum
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.enums import RequestTokenType


def register_user(body: RegisterUserRequest, oauth: bool):
    if body.role_type.value == RoleEnum.OWNER.value:
        return register_owner(body, oauth)


def register_owner(body: RegisterUserRequest, oauth: bool) -> Response:
    if User.find_by_email(body.email):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message=f"{body.email} is already registered",
        )
    new_user = _create_owner(
        body.email, body.password, body.first_name, body.last_name, body.accepted_terms_and_conditions
    )
    new_user.save()
    _create_default_location(new_user, body.gym_name)
    if not oauth and get_config().EMAIL_CONFIRMATION is not False:
        try:
            send_owner_verification_email(new_user)
        except OperationalError as oe:
            logging.error(f"Error sending owner verification email: {oe}")
    db.session.commit()
    _create_onboarding_admin_account(new_user, body.gym_name)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Successfully registered",
    )


def _create_onboarding_admin_account(owner: User, gym_name: str):
    # Create an email alias for the new gym
    admin_alias = _create_admin_alias(gym_name)
    admin_user = CreateUserRequest(
        location_id=owner.locations[0].id,
        first_name="GO",
        last_name=f"{''.join(gym_name.split(' '))}",
        email=admin_alias,
        role_type_id=RoleEnum.MANAGER.value,
    )
    create_user(owner.locations[0].id, admin_user, skip_verification=True)
    user = User.find_by_email(admin_alias)
    send_onboarding_email(user, owner)


def _create_admin_alias(gym_name: str) -> str:
    special_characters = r"[^a-zA-Z0-9]+"
    alias = (re.sub(special_characters, "", gym_name)).lower()
    return f"onboarding+{alias}@gymowners.com"


def verify_email(query: VerifyEmailRequest) -> Response:
    try:
        email = User.validate_verification_token(query.token)
    except Exception:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_TOKEN,
            logger_name=__name__,
            message="Invalid or expired token.",
        )
    user = User.find_by_email(email)
    if user.verified is True:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message="Your account is is already verified. If you forgot your password, use 'Forgot password?' link on login page",
        )
    if user.role_type_id == RoleEnum.OWNER.value:
        user.active = True
        user.verified = True
        user.verified_on = utc_now()
        user.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="You have verified your account. You can login now.",
    )


def verify_email_and_set_password(body: VerifyAndSetPassword) -> Response:
    try:
        email = User.validate_verification_token(
            body.token, is_profile_setup=body.is_profile_setup if body.is_profile_setup else False
        )
    except Exception:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_TOKEN,
            logger_name=__name__,
            message="Invalid or expired token.",
        )
    user = User.find_by_email(email)
    if body.password != body.password_again:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR_SETTING_PASSWORD,
            logger_name=__name__,
            message="Passwords dont match.",
        )

    user.password = body.password

    if not user.verified:
        user.verified = True
        user.verified_on = utc_now()
        user.user_profile.accepted_privacy_policy_datetime = utc_now()
        user.user_profile.accepted_terms_conditions_datetime = utc_now()
    if not user.active:
        user.active = True
    user.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="You have verified your account. You can login now with your new password.",
    )


def verify_profile_setup_token(query: VerifyEmailRequest):
    try:
        email = User.validate_verification_token(query.token, is_profile_setup=True)
    except Exception:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_TOKEN,
            logger_name=__name__,
            message="Invalid or expired token.",
        )
    user = User.find_by_email(email)
    user.verified = True
    user.verified_on = utc_now()
    user.save_and_commit()
    data = ProfileSetupResponse(active=user.active).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="Profile setup link is verified",
        data=data,
    )


def forgot_password_and_reset(body: VerifyAndSetPassword) -> Response:
    try:
        email = User.validate_verification_token(body.token, body.is_profile_setup)
    except Exception:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_TOKEN,
            logger_name=__name__,
            message="Invalid or expired token.",
        )
    user = User.find_by_email(email)
    if not user.active or not user.verified:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR_SETTING_PASSWORD,
            logger_name=__name__,
            message="User is not active or verified. Please contact your gym administrator.",
        )
    if body.password != body.password_again:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR_SETTING_PASSWORD,
            logger_name=__name__,
            message="Passwords dont match.",
        )
    user.password = body.password
    user.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="You have successfully reset your password. You can login now with your new password.",
    )


def login_user(email: str, password: str, source) -> Response:
    user = User.find_by_email(email)

    if not user or not user.active or not user.check_password(password):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_CREDENTIALS,
            logger_name=__name__,
            message="Invalid email or password",
        )

    if source is not None and source.lower() == "web" and user.role_type_id == RoleEnum.MEMBER.value:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FORBIDDEN,
            logger_name=__name__,
            message="Please use the mobile app to login",
        )

    if source is not None and source.lower() == "mobile" and user.role_type_id != RoleEnum.MEMBER.value:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FORBIDDEN,
            logger_name=__name__,
            message="Please use the web app to login",
        )

    if user.deactivated_on is not None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FORBIDDEN,
            logger_name=__name__,
            message="Invalid email or password",
        )

    if user.verified is False:
        return send_verification_email(user.email)

    access_token = User.generate_access_token(user)
    refresh_token = User.generate_refresh_token(user)
    user.last_login = utc_now()
    user.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message=f"{email} logged in",
        data=LoginUserResponse(access_token=access_token, refresh_token=refresh_token).model_dump(),
    )


def refresh_access_token_info(body: RefreshAccessTokenRequest):
    result, token_dict = User.decode_token(body.refresh_token)
    if result.failure or token_dict["type"] != "refresh_token":
        return create_response(
            status_code=HTTPStatus.UNAUTHORIZED,
            status=ResponseStatusEnum.UNAUTHORIZED,
            logger_name=__name__,
            message="Refresh token is invalid or expired",
        )
    user = User.find_by_id(token_dict["user_id"])
    if user is None:
        return create_response(
            status_code=HTTPStatus.UNAUTHORIZED,
            status=ResponseStatusEnum.UNAUTHORIZED,
            logger_name=__name__,
            message="Refresh token is invalid",
        )
    access_token = User.generate_access_token(user)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        data=RefreshAccessTokenResponse(access_token=access_token).model_dump(),
        message="",
    )


def forgot_password_request(email: str, source: str = None):
    user = User.find_by_email(email)
    if not user:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Email not found.",
        )

    if not user.verified:
        if user.role_type_id == RoleEnum.OWNER.value:
            send_owner_verification_email(user)
        elif user.role_type_id == RoleEnum.STAFF.value:
            send_staff_account_verification_email(user)
        else:
            send_member_verification_email(user, source)

        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message="You are not verified. We've sent you another verification email. Check it out!.",
        )

    send_password_reset_email(user)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="We've sent you a password reset email. Check it out!.",
    )


def _create_default_location(new_user: User, gym_name: str):
    new_gym = Gym(gym_name)
    new_gym.save_and_commit()
    new_location_request = CreateLocationRequest(gym_id=new_gym.id, location_name=new_gym.name, primary=True)
    create_location(new_user.id, new_location_request)


def _create_owner(
    email: str, password: str, first_name: str, last_name: str, accepted_terms_and_conditions: bool
) -> Optional[User]:
    new_user = User(email, password)
    new_profile = UserProfile(
        first_name=first_name,
        last_name=last_name,
        accepted_terms_conditions_privacy_policy_datetime=datetime.datetime.utcnow(),
    )
    new_user.user_profile = new_profile
    new_user.role_type_id = RoleEnum.OWNER.value
    new_user.active = True
    return new_user


def send_verification_email(email: str):
    user = User.find_by_email(email)
    if not user:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Email not found.",
        )
    if user.verified:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message="Already verified. Pls use your username and password to login",
        )
    if user.role_type_id == RoleEnum.OWNER.value:
        send_owner_verification_email(user)
    elif user.role_type_id == RoleEnum.MEMBER.value:
        send_member_verification_email(user)
    else:
        send_staff_account_verification_email(user)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="We've sent you another verification email. Check it out!.",
    )


def send_owner_verification_email(user: User):
    token = User.generate_verification_token(user.email)
    link = f"{get_config().APP_URL}/verify?role={user.role_type_id}&token={token}"
    data = {"first_name": user.user_profile.first_name, "confirmation_link": link}
    celery.send_task("owner_verification_email", (user.email, data))


def send_member_verification_email(user: User, source: str = None):
    token = User.generate_verification_token(user.email)
    # If unverified member tries to reset password from storefront, send the setup-profile to verify and set password on web
    if source and source.lower() == "storefront":
        link = f"{get_config().STOREFRONT_URL}/setup-profile?token={token}"
    else:
        link = f"{get_config().STOREFRONT_URL}/verify?role={user.role_type_id}&token={token}"
    data = {
        "member_first_name": user.user_profile.first_name,
        "confirmation_link": link,
        "location_name": user.locations[0].name,
    }
    celery.send_task("contact_app_verification_code_email", (user.email, data))
    return create_response(
        status_code=HTTPStatus.OK, status=ResponseStatusEnum.SENT_MAIL, logger_name=__name__, message="SENT_MAIL"
    )


def send_member_forgotten_password_email(user: User):
    token = User.generate_verification_token(user.email)
    link = f"{get_config().APP_URL}/verify?role={user.role_type_id}&token={token}"
    data = {
        "member_first_name": user.user_profile.first_name,
        "member_last_name": user.user_profile.last_name,
        "verification_code": link,
        "location_name": user.locations[0].name,
    }
    celery.send_task("contact_app_forgotten_password_code_email", (user.email, data))
    logging.info(f"Verification code for resetting forgotten password sent to {user.email}")


def send_onboarding_email(user: User, owner: User):
    data = {
        "location_name": user.locations[0].name,
        "owner_email": owner.email,
        "admin_email": user.email,
        "created_datetime": utc_now(),
    }
    celery.send_task("owner_onboard_admin_email", (user.email, data))


def generate_verification_link(query: VerificationLinkRequest):
    user = User.find_by_email(query.email)
    if not user:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Email not found.",
        )
    link = ""
    token = User.generate_verification_token(user.email)
    if query.type == RequestTokenType.SIGNUP.value:
        if user.role_type_id == RoleEnum.OWNER.value or user.role_type_id == RoleEnum.MEMBER.value:
            link = f"{get_config().APP_URL}/verify?role={user.role_type_id}&token={token}"
        else:
            link = f"{get_config().APP_URL}/staff-verify?role={user.role_type_id}&token={token}"
    elif query.type == RequestTokenType.FORGOT_PASSWORD.value:
        path = (
            "members/forgot_password_reset" if user.role_type_id == RoleEnum.MEMBER.value else "forgot_password_reset"
        )
        link = f"{get_config().APP_URL}/{path}?role={user.role_type_id}&token={token}"
    elif query.type == RequestTokenType.PROFILE_SETUP.value:
        link = f"{get_config().STOREFRONT_URL}/setup-profile?token={token}"
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        message="Verification link generated successfully.",
        data={"link": link},
    )
