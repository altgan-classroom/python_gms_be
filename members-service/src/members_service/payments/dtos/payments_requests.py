from datetime import date
from typing import Optional

from pydantic import Field, BaseModel

from members_service.members.dtos.members_requests import ProfilePath, LocationPath


class PaymentMethodPath(ProfilePath):
    pm_id: int = Field(..., description="Payment Method id")


class PaymentPath(LocationPath):
    location_id: int = Field(..., description="Location id")
    member_id: int = Field(..., description="Member id")
    payment_id: int = Field(..., description="Payment id")


class UpdatePaymentPath(LocationPath):
    location_id: int = Field(..., description="Location id")
    member_id: int = Field(..., description="Member id")
    payment_id: Optional[int] = None


class PayrixOnboardRequest(BaseModel):
    payrix_customer_id: str
    payrix_onboarding_status: int


class CreatePaymentMethodRequest(BaseModel):
    location_id: int
    member_id: int
    token: Optional[str] = None
    payrix_token_id: Optional[str] = None
    expiration: Optional[str] = None
    account_ach: Optional[str] = None
    routing_ach: Optional[str] = None
    last_4_digits_card: Optional[str] = None
    inactive: Optional[bool] = None
    method: Optional[int] = None
    default: Optional[bool] = None
    zipcode: Optional[str] = None


class UpdatePaymentMethodRequest(CreatePaymentMethodRequest):
    payment_method_id: int


class CreatePaymentRequest(BaseModel):
    location_id: int
    member_id: int
    payment_method_id: Optional[int] = None
    amount: float
    scheduled_date: date
    notes: Optional[str] = Field(None, alias="description", description="Description")
    taxable: Optional[bool] = None
    invoice_id: Optional[int] = None


class UpdatePaymentRequest(CreatePaymentRequest):
    payment_id: int
    amount: Optional[float] = None
    scheduled_date: Optional[date] = None


class UpdatePaymentQuery(BaseModel):
    update_type: Optional[int] = Field(None,description="Optional. Update -> None, Forgive->1, Reinforce->2, Cancel->3, Restore->4")


class CreateRefundRequest(BaseModel):
    location_id: int
    member_id: int
    payment_id: int = Field(..., description="Original payment_id to be submitted")
    total_amount: float


class CreateRetryRequest(BaseModel):
    location_id: int
    member_id: int
    payment_id: int = Field(..., description="Original payment_id to be submitted")


class PayrixTxnAlert(BaseModel):
    txnId: str
    txnAmount: float
    txnStatus: str
    model_config = {"extra": "allow"}


class PayrixTxnUpdateResponse(BaseModel):
    alert: PayrixTxnAlert
    model_config = {"extra": "allow"}


class PayrixTxnUpdateRequest(BaseModel):
    response: PayrixTxnUpdateResponse
    model_config = {"extra": "allow"}
