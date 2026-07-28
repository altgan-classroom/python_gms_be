from datetime import datetime, date

from pydantic import BaseModel, BeforeValidator, AfterValidator, Field
from typing import Optional, List, Annotated
from auth_admin_service.admin.dtos.admin_responses import LocationResponse
from gmsshared.src.util.validators import date_format_validator, date_validator


class PermissionType(BaseModel):
    id: int
    name: str
    display_name: str

    class Config:
        from_attributes = True


class Role(BaseModel):
    id: int
    name: str
    permissions: List[PermissionType] = []

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    user_id: int = Field(..., alias='id')
    photo_url: Optional[str] = None
    dark_mode: Optional[bool] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Annotated[Optional[date | str], BeforeValidator(date_format_validator)] = None
    start_date: Annotated[
        Optional[date | str], BeforeValidator(date_validator), AfterValidator(date_format_validator)
    ] = Field(None, description="User start date")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserInfoResponse(BaseModel):
    active: Optional[bool]
    id:int
    email: str
    verified_on: Annotated[Optional[datetime | str], BeforeValidator(date_format_validator)] = None
    locations: List[LocationResponse] = []
    last_login: Annotated[Optional[datetime | str], BeforeValidator(date_format_validator)] = None
    role: Role
    user_profile: UserProfile

    class Config:
        from_attributes = True


class LoginUserResponse(BaseModel):
    access_token: str
    refresh_token: str


class ProfileSetupResponse(BaseModel):
    active: bool


class RefreshAccessTokenResponse(BaseModel):
    access_token: str
