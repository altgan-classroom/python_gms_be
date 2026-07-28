from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import Optional

from gmsshared.src.util.enums import RoleEnum


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    gym_name: str
    role_type: RoleEnum
    accepted_terms_and_conditions: bool


class LoginUserRequest(BaseModel):
    email: str
    password: str
    source: Optional[str] = None


class UpdateUserInfo(BaseModel):
    active: Optional[bool] = Field(
        default=True, description="Whether the user is currently active in the system or not"
    )
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    dark_mode: Optional[bool] = None
    photo_url: Optional[HttpUrl] = None


class ChangePasswordRequest(BaseModel):
    old_password: Optional[str] = None
    new_password: str


class ImpersonateRequest(BaseModel):
    impersonate_gym_id: int
    password: Optional[str]


class VerifyEmailRequest(BaseModel):
    token: str


class VerifyAndSetPassword(VerifyEmailRequest):
    password: str
    password_again: str
    is_profile_setup: Optional[bool] = None
    accepted_terms_and_conditions: Optional[bool] = None


class SendVerificationRequest(BaseModel):
    email: str


class ForgotPasswordRequest(BaseModel):
    email: str
    source: Optional[str] = None


class UploadRequest(BaseModel):
    name: str
    type: str


class RoleTypesQuery(BaseModel):
    staff: Optional[bool] = Field(default=False, description="Whether to request only staff roles")


class RefreshAccessTokenRequest(BaseModel):
    refresh_token: str


class VerificationLinkRequest(BaseModel):
    email: str
    type: int

class VendorAuthFieldRequest(BaseModel):
    vendor_id: int