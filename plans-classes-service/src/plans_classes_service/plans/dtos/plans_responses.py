from pydantic import BaseModel, Field
from typing import Optional, List


class PlanType(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ClassAccessGroup(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GymResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class LocationResponse(BaseModel):
    id: int
    name: str
    primary: bool
    gym: GymResponse

    class Config:
        from_attributes = True


class Plan(BaseModel):
    location_id: int
    plan_id: int = Field(alias="id")
    name: str
    description: Optional[str]
    plan_types: List[PlanType]
    duration: Optional[float]
    duration_type_id: Optional[int]
    billing_type_id: int
    signup_fee: Optional[float]
    recurring_amount: Optional[float]
    recurring_interval: Optional[float]
    recurring_duration_type_id: Optional[int]
    classes_per_week: Optional[int]
    unlimited: Optional[bool]
    auto_renewal: Optional[bool]
    paid_in_full_price: Optional[float]
    class_or_session_pack_price: Optional[float]
    class_access_groups: Optional[List[ClassAccessGroup]]
    pass_limit: Optional[int]
    pass_expiration: Optional[int]
    pass_expiration_duration_type_id: Optional[int]
    plan_status_type_id: Optional[int]
    trial: Optional[bool]
    challenge: Optional[bool]
    grandfathered: Optional[bool]
    check_in_required: Optional[bool]
    booking_required: Optional[bool]
    min_age: Optional[int]
    max_age: Optional[int]
    access_for_24_hrs: Optional[bool]
    revenue_rate: Optional[float]
    location_permissions: Optional[List[LocationResponse]] = Field(alias="plan_locations")
    membership_type_id: Optional[int]
    sessions_count: Optional[int]
    sessions_limit_times: Optional[int]
    sessions_limit_every: Optional[int]
    sessions_limit_duration_type_id: Optional[int]
    first_of_month: Optional[bool]
    taxable: Optional[bool]
    apply_weekly_registration_limits: Optional[bool] = Field(default=False)
    weekly_limit_times: Optional[int]

    class Config:
        from_attributes = True


class PlanResponse(Plan):
    plan_types: List[int]


class PlanList(BaseModel):
    location_id: int
    plan_id: int
    plan_name: str
    plan_type: str
    plan_duration: str
    billing_type: str
    price: str
    plan_status: str
    member_count: Optional[int]
