from datetime import datetime, date
import json
from pydantic import BaseModel, Field, AfterValidator, BeforeValidator, field_validator
from typing import Optional, List, Annotated

from gmsshared.src.util.enums import ContactTypeEnum
from gmsshared.src.util.responses import BaseResponse
from gmsshared.src.util.validators import (
    date_format_validator,
    to_local_activity_history,
    validate_contact_type,
    validate_contact_about,
    date_validator,
    payment_date_format_validator,
    to_local,
    validate_plan_type,
)


class MemberResponse(BaseModel):
    contact_type: Annotated[ContactTypeEnum, BeforeValidator(validate_contact_type)] = Field(
        ContactTypeEnum.LEAD, description="role type of contact"
    )
    location_id: int
    member_id: int
    member_name: str
    email: str
    phone_number: Optional[str] = None
    first_name: str
    last_name: str
    membership_status: str
    create_datetime: Annotated[datetime | str, AfterValidator(date_format_validator)] = Field(
        ..., description="Date user was created"
    )


class MemberListResponse(BaseResponse):
    data: Optional[List[MemberResponse] | None]


class MemberClassResponse(BaseModel):
    id: int
    location_id: int
    class_id: int
    user_id: int
    membership_id: int
    class_time: Annotated[datetime | str, AfterValidator(to_local)] = Field(..., description="Class Time")
    member_registered_time: Annotated[datetime | str, AfterValidator(to_local)] = Field(
        ..., description="Member Registered Time"
    )
    member_waitlist: Optional[int] = 0
    member_cancelled_time: Annotated[Optional[datetime], AfterValidator(to_local)] = Field(
        None, description="Member Cancelled Time"
    )
    member_checkin_time: Annotated[Optional[datetime | str], AfterValidator(to_local)] = Field(
        None, description="Member Checkin Time"
    )
    create_datetime: Annotated[datetime | str, AfterValidator(to_local)] = Field(..., description="Member Created Time")
    update_datetime: Annotated[datetime | str, AfterValidator(to_local)] = Field(..., description="Member Updated Time")
    cancel_rebook_email_time: Annotated[Optional[datetime | str], AfterValidator(to_local)] = Field(
        None, description="Cancel Rebook Time"
    )
    cancel_reason: Optional[str] = None
    coach_name: Optional[str] = None


class RegisteredMemberResponse(BaseModel):
    member_classes: Optional[List[MemberClassResponse]]
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    photo_url: Optional[str] = None


class RegisteredMemberListResponse(BaseModel):
    memberships: List[RegisteredMemberResponse]


class MemberProfileResponse(BaseModel):
    member_id: int
    location_id: int
    membership_status: str
    payment_status: str | None
    last_check_in: Annotated[Optional[datetime | str], AfterValidator(date_format_validator)] = Field(
        None, description="Last time member checked in"
    )
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None
    email: str
    photo_url: Optional[str] = None
    dark_mode: Optional[bool] = None
    birth_date: Annotated[
        Optional[date | str], BeforeValidator(date_validator), AfterValidator(date_format_validator)
    ] = Field(None, description="Last time member checked in")
    address_street: Optional[str] = None
    address_street_2: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None
    objective_type_id: Optional[int] = None
    gender_type_id: Optional[int] = None
    phone_number: Optional[str] = None
    emergency_first_name: Optional[str] = None
    emergency_last_name: Optional[str] = None
    emergency_phone_number: Optional[str] = None
    emergency_relationship: Optional[str] = None
    guardian_first_name: Optional[str] = None
    guardian_last_name: Optional[str] = None
    guardian_phone_number: Optional[str] = None
    membership_plans: Optional[List[int]] = Field(None, alias="plans")
    outstanding_balance: Optional[float] = None
    create_datetime: Annotated[datetime | str | None, AfterValidator(date_format_validator)] = Field(
        ..., description="Date user was enrolled in first membership"
    )
    about: Annotated[Optional[str], BeforeValidator(validate_contact_about)] = Field(
        None, description="'About' information for user"
    )
    contact_type: str | None = Field(default=None, description="One of Client, Lead, Frozen or Exited")
    have_children: Optional[bool] = None
    door_access_credential: Optional[str] = None
    door_access_credential_status: Optional[int] = None


class ProfileResponse(BaseModel):
    member_id: int
    location_id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None
    email: str
    birth_date: Annotated[
        Optional[date | str], BeforeValidator(date_validator), AfterValidator(date_format_validator)
    ] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_street_2: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None
    objective_type_id: Optional[int] = None
    gender_type_id: Optional[int] = None
    phone_number: Optional[str]
    emergency_first_name: Optional[str] = None
    emergency_last_name: Optional[str] = None
    emergency_phone_number: Optional[str] = None
    emergency_relationship_type_id: Optional[int] = None
    guardian_first_name: Optional[str] = None
    guardian_last_name: Optional[str] = None
    guardian_phone_number: Optional[str] = None
    relationship_status_type_id: Optional[int] = None
    have_children: Optional[bool] = Field(None)
    shirt_size_type_id: Optional[int] = None
    shirt_fit_type_id: Optional[int] = None
    favourite_gym_clothing_website: Optional[str] = None
    favourite_website: Optional[str] = None
    favourite_restaurant: Optional[str] = None
    cp_phone_calls: Optional[bool] = None
    cp_email: Optional[bool] = None
    cp_sms: Optional[bool] = None
    cp_in_app_message: Optional[bool] = None
    payrix_customer_id: Optional[str] = None
    payrix_onboarding_status: Optional[int] = None
    outstanding_balance: Optional[float] = None
    create_datetime: Annotated[datetime | str, AfterValidator(date_format_validator)] = Field(
        ..., description="Date user was created"
    )
    door_access_auth_info: Optional[dict] = None
    door_access_auth_status: Optional[int] = None
    door_access_credential: Optional[str] = None
    door_access_credential_status: Optional[int] = None


class LocationInfoResponse(BaseModel):
    email: str
    phone: str

class FreezeResponse(BaseModel):
    freeze_id: Optional[int] = None
    freeze_from: str
    freeze_to: str
    freeze_reason_type_id: Optional[int] = None


class Membership(BaseModel):
    member_id: int
    location_id: int
    plan_id: int
    membership_id: int
    plan_name: str | None
    start_date: Annotated[date | str | None, AfterValidator(payment_date_format_validator)] = Field(
        ..., description="Start Date"
    )
    end_date: Annotated[date | str | None, AfterValidator(payment_date_format_validator)] = Field(
        ..., description="End Date"
    )
    member_status: str | None
    membership_status: str | None
    sessions_count: int | None
    cancel_date: Annotated[date | None, AfterValidator(to_local)] = Field(None, description="Cancel Date")
    freeze_to: Annotated[date | None, AfterValidator(to_local)] = Field(None, description="Freeze Date")
    auto_renewal: Optional[bool] = Field(None, description="Auto Renewal")
    plan_types: Annotated[Optional[List[int] | str | None], AfterValidator(validate_plan_type)] = Field(
        None, description="Plan type list"
    )
    class_access_groups: Optional[List[dict|None]] = []
    discount_percent_per_payment: Optional[float] = Field(None, description="Initial Discount Percent Per Payment")
    discount_amount_per_payment: Optional[float] = Field(None, description="Initial Discount Amount Per Payment")
    apply_discount_to_all_payments: Optional[bool] = Field(None, description="Apply Discount to all payments?")
    split_payments: Optional[str] = Field(None, description="Split Payments")
    next_billing_date: Annotated[date | str | None, AfterValidator(payment_date_format_validator)] = Field(
        None, description="Next Billing Date")
    next_billing_amount: Optional[float] = Field(None, description="Next Billing Amount")
    apply_next_billing_date_to_all_invoices: Optional[bool] = False
    billing_interval: str | None
    next_billing_date_range: Optional[List[date | str]] = Field(None, description="Next Billing Date Range")
    current_freeze: Optional[List[FreezeResponse]] = []
    past_freezes: Optional[List[FreezeResponse]] = []
    upcoming_freezes: Optional[List[FreezeResponse]] = []
    next_action_type_id: Optional[int] = None
    next_action_date: Annotated[date | None, AfterValidator(to_local)] = None
    session_limits: Optional[str] = None
    session_limits_reset_on: Optional[date | str | None] = None
    sessions_remaining: Optional[int] = None

    class Config:
        from_attributes = True

    @field_validator('past_freezes', 'current_freeze', 'upcoming_freezes', 'class_access_groups', mode='before')
    def parse_json_string(cls, v):
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v or []

class MembershipList(BaseModel):
    data: List[Membership]


class InvoiceItem(BaseModel):
    id: Optional[int] = None
    amount: float
    discount: float
    tax: float
    total_amount: float
    description: Optional[str] = None
    due_date: Annotated[date | str | None, AfterValidator(payment_date_format_validator)] = Field(None, description="Due Date")

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    location_id: int
    member_id: int = Field(..., alias="user_id")
    invoice_id: Optional[int] = Field(None, alias="id")
    invoice_type_id: Optional[int]
    invoice_status_type_id: Optional[int]
    total_amount: Optional[float]
    tax: Optional[float]
    amount: Optional[float]
    discount: Optional[float]
    product_category_type_id: Optional[int]
    product_id: Optional[int] = None
    notes: Optional[str]
    due_date: Annotated[date | str | None, AfterValidator(payment_date_format_validator)] = Field(None, description="Due Date")
    invoice_items: List[InvoiceItem]
    payments: Optional[List] = None
    created_date: Annotated[datetime | str | None, AfterValidator(payment_date_format_validator)] = Field(None, description="Created Date",
                                                                                                         alias="create_datetime")
    description: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceList(BaseModel):
    data: List[InvoiceResponse]

class TempPaymentResponse(BaseModel):
    signup_fee: Optional[float] = 0
    plan_payment: Optional[float] = 0
    discount: Optional[float] = 0
    tax: Optional[float] = 0
    total_amount: Optional[float] = 0
    due_date: Annotated[date | str | None, AfterValidator(payment_date_format_validator)] = Field(None, description="Due Date")

class TempMembershipResponse(BaseModel):
    member_id: int = Field(validation_alias="user_id")
    location_id: int
    plan_id: int
    membership_id: Optional[int] = None
    payments: Optional[List[TempPaymentResponse]] = None
    total_amount: Optional[float] = None


class MembershipSessionResponse(BaseModel):
    location_id: int
    member_id: int = Field(validation_alias="user_id")
    membership_id: int
    sessions_bought: Optional[int]
    sessions_remaining: Optional[int]

    class Config:
        from_attributes = True

class ReconciliationItem(BaseModel):
    type: str = Field(None, description="Type of txn. One of Invoice | Credit Memo | Credit Card Payment etc")
    processed_date: datetime | str | None = Field(None, description="Processed Date")
    total_amount: float = None
    credit: bool = Field(None, description="Credit or Debit")

class ActivityHistory(BaseModel):
    id: Optional[int] = Field(None, description="ID of invoice or payment depending on instrument type")
    activity_date: Annotated[datetime | str | None, AfterValidator(to_local_activity_history)] = Field(None, description="Activity Date")
    instrument_type: Optional[str] = Field(None, description="Use this to determine what the ID is for")
    type: str | None
    description: str | None
    status: str | None
    charges: float | None
    payment: float | None
    payment_method: Optional[str] = None
    can_cancel: bool | str | None = Field("false", description="Whether or not the Payment can be cancelled")
    total: float | None = Field(None, description="Use this with the instrument type to calc the Total Charges and Total Payments")
    balance: float | None = Field(0.0, description="Running balance since the beginning for this member")
    order_by: int | None = Field(None, description="Order by this column")
    msg: str | None = Field(None, description="Failure messages or notes in payments")
    amount: float | None = Field(None, description="Amount before discount and tax")
    discount: float | None = Field(None, description="Discount")
    tax: float | None = Field(None, description="Tax")

class ReconciliationResponse(BaseModel):
    data: List[ReconciliationItem]


class SessionActivity(BaseModel):
    activity_date: Annotated[datetime | str | None, AfterValidator(to_local_activity_history)] = Field(None, description="Activity Date")
    activity_name: Optional[str] = Field(None, description="Name of the activity")
    activity_type_id: Optional[int] = Field(None, description="Use this to determine what the activity is for")
    balance: Optional[int] = 0
    updated_by: Optional[str] = None
    amount: Optional[float] = None
    activity_description: Optional[str] = Field(None, description="Description of the activity")


class SessionActivityResponse(BaseModel):
    data: List[SessionActivity]