from datetime import date, datetime
from typing import Optional, List, Annotated

from pydantic import BaseModel, Field, EmailStr, HttpUrl, BeforeValidator
from gmsshared.src.util.enums import CheckinTypeEnum
from gmsshared.src.util.validators import date_validator
from gmsshared.src.util.enums import RegistrationTimesType


class Path(BaseModel):
    pass


class LocationPath(Path):
    location_id: int = Field(..., description="Location id")


class UserPath(LocationPath):
    """location_id + user_id"""

    user_id: int = Field(..., description="User id")

class DoorPath(LocationPath):
    door_id: int = Field(..., description="Door id")

class UserType(BaseModel):
    roles: Optional[List[int]] = Field(None, description="IDs of roles used to filter results")
    active_only: Optional[bool] = Field(None, description="Whether to return only non-deactivated users")


class GetGymLocationsRequest(BaseModel):
    gym_id: int = Field(..., alias="gym_id")


class CreateLocationRequest(BaseModel):
    gym_id: int
    location_name: str
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    area_sft: Optional[int] = None
    location_type_id: Optional[int] = None
    gym_types: Optional[List[int]] = None
    other_gym_type: Optional[str] = None
    primary: Optional[bool] = None
    cs_phone: Optional[str] = None
    cs_email: Optional[str] = None
    sales_tax: Optional[float] = None
    kiosk_enabled: Optional[bool] = False
    checkin_type: Optional[CheckinTypeEnum] = Field(default=None, description="Checkin type")
    accent_color: Optional[str] = "#000000"
    kiosk_username: Optional[str] = None
    kiosk_password: Optional[str] = None
    logo_url: Optional[str] = None
    registration_start_time_type_id: Optional[RegistrationTimesType] = None
    registration_start_time_value: Optional[int] = None
    registration_end_time_type_id: Optional[RegistrationTimesType] = None
    registration_end_time_value: Optional[int] = None
    late_cancellation_time_type_id: Optional[RegistrationTimesType] = None
    late_cancellation_time_value: Optional[int] = None

class DoorAcessAuthFields(BaseModel):
    field_id: int = Field(None, description="Door access auth field id")
    field_value: str = Field(None, description="Door access auth field value")

class UpdateLocationRequest(CreateLocationRequest):
    gym_id: Optional[int] = None
    location_id: int
    timezone_type_id: Optional[int] = None
    waitlist: Optional[bool] = None
    no_show_credit: Optional[bool] = None
    is_dea: Optional[bool] = None
    late_cancellation: Optional[bool] = None
    block_registrations_on_balance_due: Optional[bool] = None
    class_access_group: Optional[bool] = None

class PayrixOnboardRequest(BaseModel):
    payrix_merchant_id: str
    payrix_onboarding_status: int


class CreateUserRequest(BaseModel):
    location_id: int = Field(..., description="Primary Location ID for this user")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    email: str = Field(..., description="User email")
    phone_number: Optional[str] = Field(None, description="User phone number")
    birth_date: Optional[date] = Field(None, description="User birth date")
    role_type_id: int = Field(..., description="ID of role type for this user")
    start_date: Annotated[Optional[date | str], BeforeValidator(date_validator)] = Field(
        None, description="User start date"
    )
    password: Optional[str] = Field("Test@1234", description="Default Password")
    about: Optional[str] = Field(None, description="'About' information for user")


class UpdateUserRequest(CreateUserRequest):
    permissions: Optional[List[int]] = None
    password: Optional[str] = None


class UpdateGymRequest(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None


class UpdateStaffProfileRequest(BaseModel):
    active: Optional[bool] = Field(None, description="Whether the user is active or not")
    location_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    start_date: Annotated[Optional[date | str], BeforeValidator(date_validator)] = None
    verified_on: Optional[datetime] = None
    role_type_id: Optional[int] = None
    photo_url: Optional[str] = None


class UpdateGymMainSettingsRequest(BaseModel):
    gym_id: int
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    timezone_type_id: Optional[int] = None
    location_type_id: Optional[int] = None


class UpdateGymClassSettingsRequest(BaseModel):
    gym_id: int
    session_or_class: Optional[int] = None
    registration_start_time_type_id: Optional[int] = None
    registration_start_value: Optional[int] = None
    registration_end_time_type_id: Optional[int] = None
    registration_end_value: Optional[int] = None
    late_cancellation_enforcement: Optional[bool] = None
    late_cancellation_time_type_id: Optional[int] = None
    cancellation_penalty: Optional[int] = None
    no_show_penalties: Optional[bool] = None
    no_show_time_penalty: Optional[int] = None
    waitlist_availability: Optional[bool] = None
    block_registrations_on_balance_due: Optional[bool] = None


class CreateRoomRequest(BaseModel):
    location_id: int
    name: str
    sft: Optional[int] = None
    capacity: Optional[int] = None
    notes: Optional[str] = None


class UpdateRoomRequest(CreateRoomRequest):
    location_id: int
    room_id: int
    name: Optional[str] = None


class RoomPath(LocationPath):
    room_id: int = Field(..., description="Room id")


class ReportPath(LocationPath):
    report_id: int = Field(..., description="Report id")

class CreateDoorRequest(BaseModel):
    location_id: int
    name: str
    door_location: Optional[str] = None

class UpdateDoorRequest(CreateDoorRequest):
    id: int = Field(..., alias='door_id')
    active: bool

class UpdateDoorAccessSettingsRequest(BaseModel):
    door_access: Optional[bool] = None
    door_access_auth_fields: Optional[List[DoorAcessAuthFields]] = None
    door_access_vendor_id: Optional[int] = None
    door_access_unlock_doors: Optional[bool] = None