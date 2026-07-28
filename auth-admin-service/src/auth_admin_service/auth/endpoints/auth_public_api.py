from fastapi import APIRouter, Depends

from auth_admin_service.admin.services.admin_location_svc import get_vendor_auth_data
from gmsshared.src.config import Config
from auth_admin_service.auth.dtos.auth_requests import (
    RegisterUserRequest,
    LoginUserRequest,
    VerifyEmailRequest,
    SendVerificationRequest,
    VerifyAndSetPassword,
    ForgotPasswordRequest,
    RefreshAccessTokenRequest,
    VerificationLinkRequest,
)
from auth_admin_service.auth.services.auth_public_svc import (
    register_user,
    login_user,
    verify_email,
    verify_email_and_set_password,
    send_verification_email,
    forgot_password_request,
    forgot_password_and_reset,
    refresh_access_token_info,
    verify_profile_setup_token,
    generate_verification_link,
)

auth_public_api = APIRouter(prefix="/auth", tags=["Auth Public"])


@auth_public_api.post("/register")
def register(body: RegisterUserRequest):
    return register_user(body, oauth=False)


@auth_public_api.post("/login")
def login(body: LoginUserRequest):
    return login_user(body.email, body.password, body.source)


@auth_public_api.get("/verify")
def verify(query: VerifyEmailRequest = Depends()):
    return verify_email(query)


@auth_public_api.get("/setup-profile")
def verify_profile_setup(query: VerifyEmailRequest = Depends()):
    return verify_profile_setup_token(query)


@auth_public_api.post("/verify_and_set_password")
def verify_and_set_password(body: VerifyAndSetPassword):
    return verify_email_and_set_password(body)


@auth_public_api.post("/send_verification_token")
def send_verification(body: SendVerificationRequest):
    return send_verification_email(body.email)


@auth_public_api.get("/forgot_password")
def forgot_password(query: ForgotPasswordRequest = Depends()):
    return forgot_password_request(query.email, query.source)


@auth_public_api.post("/forgot_password_reset")
def forgot_password_reset(body: VerifyAndSetPassword):
    return forgot_password_and_reset(body)


@auth_public_api.post("/refresh")
def refresh_access_token(body: RefreshAccessTokenRequest):
    return refresh_access_token_info(body)


if Config.ENV in ["stage", "test"]:

    @auth_public_api.get("/verification-link")
    def get_link(query: VerificationLinkRequest = Depends()):
        return generate_verification_link(query)


@auth_public_api.get("/door_access/vendors/{vendor_id}/auth_fields")
def get_vendor_auth_field(vendor_id: str):
    return get_vendor_auth_data(vendor_id)
