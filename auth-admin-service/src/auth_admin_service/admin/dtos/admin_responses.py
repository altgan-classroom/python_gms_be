from datetime import datetime, date
from typing import Optional, List, Annotated, Self

from pydantic import BaseModel, EmailStr, Field, AfterValidator, BeforeValidator, model_validator

from gmsshared.src.util.enums import ResponseStatusEnum
from gmsshared.src.util.validators import date_format_validator, date_validator
from gmsshared.src.util.datetime_util import convert_utc_to_location_timestring, get_location_tzdata_and_timezone


# Duplicate here to avoid circular references
class GymTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class Gym(BaseModel):
    gym_id: int = Field(alias="id")
    name: str
    logo_url: Optional[str]

    class Config:
        from_attributes = True


class TimeInformation(BaseModel):
    location_current_time: datetime | str | None = Field(None, description="The current location date & time")
    server_current_time: datetime | str | None = Field(None, description="The current server date & time (UTC)")
    location_timezone: str | None = Field(None, description="IANA timezone of the location")
    location_time_offset: str | None = Field(None, description="Time offset")


class LocationResponse(BaseModel):
    location_id: int = Field(alias="id")
    name: str
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    area_sft: Optional[int] = None
    gym_types: Optional[List[GymTypeResponse]] = None
    other_gym_type: Optional[str] = None
    primary: Optional[bool] = None
    gym: Gym
    location_type_id: Optional[int] = None
    cs_phone: Optional[str] = None
    cs_email: Optional[str] = None
    payrix_merchant_id: Optional[str] = None
    payrix_onboarding_status: Optional[int] = None
    sales_tax: Optional[float] = None
    timezone_type_id: Optional[int] = None
    location_time_info: TimeInformation = Field(None, description="Location and server time information")
    waitlist: Optional[bool] = None
    kiosk_enabled: Optional[bool] = False
    kiosk_user_id: Optional[int] = None
    checkin_type: Optional[int] = Field(default=None, description="Checkin type")
    accent_color: Optional[str] = "#000000"
    logo_url: Optional[str] = None
    no_show_credit: Optional[bool] = None
    payments: Optional[bool] = None
    registration_start_time_type_id: Optional[int] = None
    registration_start_time_value: Optional[int] = None
    registration_end_time_type_id: Optional[int] = None
    registration_end_time_value: Optional[int] = None
    late_cancellation_time_type_id: Optional[int] = None
    late_cancellation_time_value: Optional[int] = None
    is_dea: Optional[bool] = False
    late_cancellation: Optional[bool] = None
    class_access_group: Optional[bool] = False
    kiosk_username: Optional[str] = None
    block_registrations_on_balance_due: Optional[bool] = None
    door_access: Optional[bool] = None
    door_access_auth_status: Optional[int] = None
    door_access_auth_error: Optional[str] = None
    door_access_vendor_id: Optional[int] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def add_time_info(self) -> Self:
        now = datetime.now()
        server_time_string = date_format_validator(now)
        location_time_string = convert_utc_to_location_timestring(self.location_id, server_time_string)
        location_timezone, location_time_offset = get_location_tzdata_and_timezone(self.location_id)
        self.location_time_info = TimeInformation(
            location_current_time=location_time_string,
            server_current_time=server_time_string,
            location_timezone=location_timezone,
            location_time_offset=location_time_offset,
        )
        return self


class LocationList(BaseModel):
    data: List[LocationResponse]


class UserResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    staff_member_role: str = Field(..., description="User role name")
    verified_on: Annotated[Optional[datetime | str], AfterValidator(date_format_validator)] = Field(
        None, description="Date user was verified"
    )
    email: Optional[str] = Field(None, description="User email address")
    phone_number: Optional[str] = Field(None, description="User phone number")
    active: bool = Field(..., description="Either if the user is active or not")
    create_datetime: Annotated[datetime | str, AfterValidator(date_format_validator)] = Field(
        ..., description="Date user was created"
    )
    start_date: Annotated[
        Optional[date | str], BeforeValidator(date_validator), AfterValidator(date_format_validator)
    ] = Field(None, description="User start date")
    photo_url: Optional[str] = None


class UserList(BaseModel):
    data: List[UserResponse]


class ProfileInfoResponse(BaseModel):
    active: Optional[bool]
    user_id: int = Field(..., description="User ID")
    location_id: int = Field(..., description="Location id")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    email: EmailStr = Field(..., description="User email address")
    photo_url: Optional[str] = Field(None, description="User photo url")
    phone_number: Optional[str] = Field(None, description="User phone number")
    birth_date: Annotated[Optional[str], BeforeValidator(date_format_validator)] = Field(
        None, description="User birth date"
    )
    verified_on: Annotated[Optional[str], BeforeValidator(date_format_validator)] = Field(
        None, description="Date user was verified"
    )
    start_date: Annotated[
        Optional[date | str], BeforeValidator(date_validator), AfterValidator(date_format_validator)
    ] = Field(None, description="User start date")

    class Config:
        from_attributes = True


class GymMainSettingsResponse(BaseModel):
    gym_id: int = Field(alias="id")
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    timezone_type_id: Optional[int] = None
    location_type_id: Optional[int] = None

    class Config:
        from_attributes = True


class GymClassSettingsResponse(BaseModel):
    gym_id: int = Field(alias="id")
    session_or_class: Optional[int] = None
    registration_start_type_id: Optional[int] = None
    registration_start_value: Optional[int] = None
    registration_end_type_id: Optional[int] = None
    registration_end_value: Optional[int] = None
    late_cancellation_enforcement: Optional[bool] = None
    late_cancellation_time_type_id: Optional[int] = None
    cancellation_penalty: Optional[int] = None
    no_show_penalties: Optional[bool] = None
    no_show_time_penalty: Optional[int] = None
    waitlist_availability: Optional[bool] = None
    block_registrations_on_balance_due: Optional[bool] = None

    class Config:
        from_attributes = True


class RoomResponse(BaseModel):
    room_id: int = Field(alias="id")
    location_id: int
    name: str
    sft: Optional[int] = None
    capacity: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RoomList(BaseModel):
    data: List[RoomResponse]


class ReportResponse(BaseModel):
    report_id: int = Field(alias="id")
    name: str
    description: str
    dashboard_id: str
    sheet_id: str
    visual_id: str
    active: bool

    class Config:
        from_attributes = True


class BaseResponse(BaseModel):
    status: ResponseStatusEnum
    status_code: int
    message: str
    data: dict | str | bytes | None


class LocationInfoResponse(BaseModel):
    email: str
    phone: str
    door_access_place_id: Optional[int] = None

class DoorAccessAuthResponse(BaseModel):
    door_access: Optional[bool] = None
    door_access_auth_fields: Optional[List[dict]] = None
    door_access_auth_status: Optional[int] = None
    door_access_auth_error: Optional[str] = None
    door_access_vendor_id: Optional[int] = None
    door_access_unlock_doors: Optional[bool] = False


class DoorAccessAuthFieldValidation(BaseModel):
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    required: Optional[bool] = None


class DoorAccessAuthField(BaseModel):
    field_id: int = Field(alias="id")
    field_name: Optional[str] = None
    field_type: Optional[str] = None
    display_name: Optional[str] = None
    field_validation_rules_json: Optional[DoorAccessAuthFieldValidation] = None
    field_help_text: Optional[str] = None
    field_value: Optional[str] = None

class DoorAccessLocationAuthField(BaseModel):
    field_id: Optional[int] = None
    field_value: Optional[str] = None


class DoorAccessAuthFieldResponse(BaseModel):
    data: List[DoorAccessAuthField]

class DoorAccessDoorResponse(BaseModel):
    door_id: int = Field(alias="id")
    name: Optional[str] = None
    door_location: Optional[str] = None
    active: Optional[bool] = None

class DoorAccessDoorResponseList(BaseModel):
    doors: List[DoorAccessDoorResponse]