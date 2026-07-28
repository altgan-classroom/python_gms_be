from datetime import datetime, date
from typing import Optional, Annotated, List

from pydantic import BaseModel, Field, EmailStr, BeforeValidator, field_validator

from gmsshared.src.util.enums import ImageFileTypeEnum
from gmsshared.src.util.validators import date_validator
from gmsshared.src.util.enums import InvoiceStatusTypeEnum


class LocationPath(BaseModel):
    location_id: int = Field(..., description="Location id")


class UserPath(LocationPath):
    user_id: int = Field(..., description="User id")


class AvatarUploadRequest(BaseModel):
    payload: bytes = Field(..., description="Avatar image content, 100Kb max size")
    filetype: ImageFileTypeEnum = Field(..., description="Avatar image filetype, types available: jpg, jpeg, png")


class MemberFilter(BaseModel):
    name: Optional[str] = None
    member_id: Optional[int] = None
    registered: Optional[int] = 0


class ProfilePath(LocationPath):
    location_id: int = Field(..., description="Location id")
    member_id: int = Field(..., description="Member id")


class InvoicePath(ProfilePath):
    invoice_id: int = Field(..., description="Invoice id")


class InvoiceQuery(BaseModel):
    membership_id: Optional[int] = Field(None, description="Membership id")
    next_invoice: Optional[bool] = Field(None, description="Next invoice?")

class MemberRequest(BaseModel):
    location_id: int = Field(..., description="Location id")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    middle_name: Optional[str] = Field(None, description="User middle name")
    preferred_name: Optional[str] = Field(None, description="User preferred name")
    email: EmailStr = Field(..., description="User e-mail")
    birth_date: Optional[date] = Field(None, description="Birth date")
    gender_type_id: Optional[int] = Field(None, description="ID of gender type")
    address_street: Optional[str] = Field(None, description="Adress street name")
    address_street_2: Optional[str] = Field(None, description="Address street 2")
    address_city: Optional[str] = Field(None, description="Adress city")
    address_state: Optional[str] = Field(None, description="Adress state")
    address_zip: Optional[str] = Field(None, description="Adress ZIP code")
    address_country: Optional[str] = Field(None, description="Adress country")
    phone_number: Optional[str] = Field(..., description="User phone number")
    objective_type_id: Optional[int] = Field(None, description="ID of objective type")
    emergency_first_name: Optional[str] = Field(None, description="Emergency contact first name")
    emergency_last_name: Optional[str] = Field(None, description="Emergency contact last name")
    emergency_phone_number: Optional[str] = Field(None, description="Emergency contact phone number")
    emergency_relationship_type_id: Optional[int] = Field(
        None, description="ID of relationship type for emergency contact"
    )
    guardian_first_name: Optional[str] = Field(None, description="Guardian first name")
    guardian_last_name: Optional[str] = Field(None, description="Guardian last name")
    guardian_phone_number: Optional[str] = Field(None, description="Guardian contact phone number")
    about: Optional[str] = Field(None, description="'About' information for user")


class CreateMemberRequest(MemberRequest):
    avatar: Optional[bytes] = Field(None, description="Profile image")
    start_date: Annotated[Optional[date | str], BeforeValidator(date_validator)] = Field(
        None, description="Date member starts at location"
    )
    send_setup_email: Optional[bool] = True


class UpdateMemberProfileRequest(MemberRequest):
    email: Optional[EmailStr] = None
    relationship_status_type_id: Optional[int] = None
    have_children: Optional[bool] = None
    shirt_size_type_id: Optional[int] = None
    shirt_fit_type_id: Optional[int] = None
    favourite_gym_clothing_website: Optional[str] = None
    favourite_website: Optional[str] = None
    favourite_restaurant: Optional[str] = None
    cp_phone_calls: Optional[bool] = None
    cp_email: Optional[bool] = None
    cp_sms: Optional[bool] = None
    cp_in_app_message: Optional[bool] = None
    avatar: Optional[bytes] = Field(None, description="Profile image")
    start_date: Annotated[Optional[datetime], BeforeValidator(date_validator)] = Field(
        None, description="Date member starts at location"
    )
    door_access_credential: Optional[str] = Field(None, description="Door access credential")

class MembershipPath(ProfilePath):
    membership_id: int = Field(..., description="Membership id")

class MembershipFreezePath(MembershipPath):
    freeze_id: int = Field(..., description="Freeze id")


class SplitPayment(BaseModel):
    payment_date: date
    payment_amount: float


class CreateMembershipRequest(BaseModel):
    location_id: int
    member_id: int
    plan_id: int
    signup_fee: Optional[float] = None
    signup_fee_due_date: Optional[date] = None
    plan_start_date: date
    plan_end_date: Optional[date] = None
    first_payment_date: Optional[date] = None
    auto_renewal: Optional[bool] = None
    discount_percent_per_payment: Optional[float] = None
    discount_amount_per_payment: Optional[float] = None
    apply_discount_to_all_payments: Optional[bool] = None
    salesperson_id: Optional[int] = None
    sessions_count: Optional[int] = None
    split_payment: bool = Field(False, description="Flag to denote a split payment or not")
    split_payments: Optional[List[SplitPayment]] = []
    cancel_description: Optional[str] = None


class CreateMembershipQuery(BaseModel):
    process: Optional[bool] = Field(None, description="action=process will create membership and process payment")
    payment_method_id: Optional[int] = Field(None, description="Payment method id")


class CreateMembershipSessionRequest(BaseModel):
    location_id: int
    member_id: int
    membership_id: int
    payment_method_id: int
    sessions_count: Optional[int] = None
    price_per_session: Optional[float] = None
    taxable: Optional[bool] = None

class RemoveMembershipSessionRequest(BaseModel):
    location_id: int
    member_id: int
    membership_id: int
    sessions_count: Optional[int] = None
    reason: Optional[str] = None


class UpdateMembershipRequest(BaseModel):
    location_id: int
    member_id: int
    membership_id: int
    membership_status_type_id: int
    auto_renewal: Optional[bool] = None
    non_renewal: Optional[bool] = None
    freeze_from: Optional[date] = None
    freeze_to: Optional[date] = None
    freeze_reason_type_id: Optional[int] = None
    unfreeze_date: Optional[date] = None
    cancel_date: Optional[date] = None
    cancel_reason_type_id: Optional[int] = None
    cancel_description: Optional[str] = None
    next_billing_date: Optional[date] = None
    apply_next_billing_date_to_all_invoices: Optional[bool] = None
    apply_discount_to_all_payments: Optional[bool] = None
    discount_percent_per_payment: Optional[float] = None
    discount_amount_per_payment: Optional[float] = None
    plan_start_date: Optional[date] = None


class UpdateMembershipFreezeRequest(BaseModel):
    location_id: int
    membership_id: int
    member_id: int
    freeze_id: int
    freeze_from: Optional[date] = None
    freeze_to: Optional[date] = None
    cancel_date: Optional[date] = None
    freeze_reason_type_id: Optional[int] = None

class PayrixOnboardMemberRequest(BaseModel):
    pass


class CreateInvoice(BaseModel):
    location_id: int
    member_id: int
    amount: Optional[float] = None
    total_amount: Optional[float] = Field(None, description="Total Amount with tax")
    notes: Optional[str] = None
    payment_category_type_id: Optional[int] = Field(None, description="Payment category type. Valid values are 1, 2, 3, 4")
    scheduled_date: Annotated[Optional[date | str], BeforeValidator(date_validator)] = Field(
        None, description="Invoice due date"
    )
    payment_method_id: Optional[int] = Field(None, description="Payment method id")
    auto_payment_on_due: Optional[bool] = False

class UpdateInvoiceRequest(BaseModel):
    location_id: int
    member_id: int
    invoice_id: int
    invoice_status_type_id: int = Field(..., description="Only valid value is 4 (Void) at this time")
    notes: Optional[str] = None

    @field_validator("invoice_status_type_id")
    def ensure_only_void(cls, v, info):
        if v != InvoiceStatusTypeEnum.VOID.value:
            raise Exception(f"Only valid value is 4 (Void) at this time")
        return v


class DoorAccessMemberLoginRequest(BaseModel):
    location_id: int
    member_id: int
    device_brand: Optional[str] = None
    device_model: Optional[str] = None
    os_name: Optional[str] = None
    expire: Optional[bool] = False
