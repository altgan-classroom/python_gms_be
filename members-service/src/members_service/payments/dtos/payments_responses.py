from datetime import date, datetime
from typing import List, Optional, Annotated, Any

from pydantic import BaseModel, Field, AfterValidator, field_validator

from gmsshared.src.util.validators import to_local


class PayrixTransactionStatusType(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PaymentMethodResponse(BaseModel):
    id: int
    location_id: int
    member_id: int = Field(validation_alias="user_id")
    token: Optional[str] = None
    payrix_token_id: Optional[str] = None
    expiration: Optional[str] = None
    last_4_digits_account: Optional[str] = None
    last_4_digits_routing: Optional[str] = None
    last_4_digits_card: Optional[str] = None
    method: Optional[int] = None
    inactive: Optional[bool] = None
    payrix_onboarding_status: Optional[int] = None
    payrix_onboarding_error: Optional[str] = None
    default: Optional[bool] = Field(default=None, validation_alias="default_method")
    zipcode: Optional[str] = None
    payrix_zipcode_onboarding_status: Optional[int] = None

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    location_id: int
    member_id: int = Field(validation_alias="user_id")
    total_amount: Optional[float] = None
    processed_date: Optional[datetime] = None
    payment_category_type_id: Optional[int] = None
    sessions_count: Optional[int] = None
    price_per_session: Optional[float] = None

    class Config:
        from_attributes = True


class PaymentRefundResponse(BaseModel):
    payment_id: Optional[int]
    total_amount: Optional[float] = None
    description: Optional[str] = None
    sessions_count: Optional[int] = None
    price_per_session: Optional[float] = None
    processed_date: Annotated[Optional[datetime], AfterValidator(to_local)] = Field(...)
    payment_status: Optional[str] = None
    payment_method_last_4_digits: Optional[Any] = None
    payment_type: Optional[Any] = None
    payrix_transaction_error: Optional[Any] = None

    @field_validator("payment_method_last_4_digits")
    def extract_payment_method_last_4_digits(cls, v, info):
        if v is None:
            return None
        if (v.last_4_digits_card is None) or (v.last_4_digits_card.strip() == ""):
            return v.last_4_digits_account
        else:
            return v.last_4_digits_card

    class Config:
        from_attributes = True


class PaymentHistResponse(BaseModel):
    id: int
    location_id: int
    member_id: int = Field(..., alias="user_id")
    total_amount: Optional[float] = None
    processed_date: Annotated[Optional[datetime], AfterValidator(to_local)] = Field(...)
    payment_method_last_4_digits: Optional[str] = None
    payment_type: Optional[str] = None
    payment_status: Optional[str] = None
    refunds: Optional[List[PaymentRefundResponse]] = None
    payrix_transaction_error: Optional[str] = None
    source: Optional[str] = None
    retry_availability: Optional[bool] = True
    description: Optional[str] = None
    scheduled_date: Annotated[Optional[date], AfterValidator(to_local)] = Field(...)
    payment_method_id: Optional[int] = None

    @field_validator("scheduled_date")
    def scheduled_date_or_processed_date(cls, v, info):
        if v is None:
            return None
        if info.data and info.data['processed_date']:
            return None
        else:
            return v

    class Config:
        from_attributes = True


class PaymentHistResponseList(BaseModel):
    data: List[PaymentHistResponse]


class PaymentStatusResponse(BaseModel):
    location_id: int
    member_id: int = Field(validation_alias="user_id")
    payment_id: int = Field(validation_alias="id")
    payment_method_id: Optional[int] = None
    total_amount: Optional[float] = None
    payrix_onboarding_status: Optional[int] = None
    payrix_onboarding_error: Optional[str] = None
    processed_date: Optional[datetime] = None
    payrix_transaction_status: Optional[int] = None
    payrix_transaction_error: Optional[str] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    description: Optional[str] = Field(None, alias="notes")
    scheduled_date: Annotated[Optional[date], AfterValidator(to_local)] = Field(...)

    class Config:
        from_attributes = True

    @field_validator('total_amount', mode='before')
    @classmethod
    def round_total_amount(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class PaymentResponseList(BaseModel):
    data: List[PaymentResponse]


class PaymentMethodResponseList(BaseModel):
    data: List[PaymentMethodResponse]
