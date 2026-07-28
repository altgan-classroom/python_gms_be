from pydantic import BaseModel, Field
from typing import Optional, List


class LocationPath(BaseModel):
    location_id: int = Field(..., description="Location id")


class PlanPath(LocationPath):
    plan_id: int = Field(..., description="Plan id")

class ClassAccessGroupPath(LocationPath):
    class_access_group_id: int = Field(..., description="Class access id")

class CreatePlanRequest(BaseModel):
    location_id: int = Field(title="Location", description=" ")
    name: str = Field(title="Plan Name", description=" ")
    description: Optional[str] = Field(title="Plan Description", description=" ")
    plan_types: Optional[List[int]] = Field(None, title="Plan Type", description="Refer to GET /plan_types for ids")
    class_accesses: Optional[List[int]] = None
    duration: Optional[float] = Field(default=None, title="Duration", description=" ")
    duration_type_id: Optional[int] = Field(
        default=None,
        title="Duration Type",
        description="Refer to GET /duration_types for ids",
    )
    billing_type_id: int = Field(None, title="Billing Type", description="Refer to GET /billing_types for ids")
    signup_fee: Optional[float] = Field(
        None,
        description="Optional. Only applicable if <i>Billing Type</i> is '<b>Recurring (billing_type_id = 1) or Class or session packs (billing_type_id = 3)</b>'",
    )
    recurring_amount: Optional[float] = Field(
        None,
        description="Required only if <i>Billing Type</i> is '<b>Recurring (billing_type_id = 1)</b>'",
    )
    recurring_interval: Optional[float] = Field(
        None,
        description="Required only if <i>Billing Type</i> is '<b>Recurring (billing_type_id = 1)</b>'",
    )
    recurring_duration_type_id: Optional[int] = Field(
        None,
        title="Recurring interval type",
        description="Required only if <i>Billing Type</i> is '<b>Recurring (billing_type_id = 1)</b>'. Refer to GET /duration_types for ids",
    )
    classes_per_week: int = Field(0, title="Classes per week", description=" ")
    unlimited: Optional[bool] = Field(
        False,
        title="Unlimited",
        description="Required only if <i>Billing Type</i> is '<b>Recurring (billing_type_id = 1)</b>'",
    )
    auto_renewal: bool = Field(False, title="Auto-renewal", description=" ")
    paid_in_full_price: Optional[float] = Field(
        None,
        title="Paid in Full price",
        description="Required only if <i>Billing Type</i> is '<b>Paid in Full (billing_type_id = 2)</b>'. Refer to GET /billing_types for ids",
    )
    class_or_session_pack_price: Optional[float] = Field(
        None,
        description="Optional. Only applicable if <i>Billing Type</i> is '<b>Class or session packs (billing_type_id = 3)</b>'",
    )
    limit_total_classes: Optional[bool] = Field(
        False,
        description="Required only if <i>Billing Type</i> is '<b>Class or session packs (billing_type_id = 3)</b>'",
    )
    pass_limit: Optional[int] = Field(
        None,
        description="Required only if <i>Billing Type</i> is '<b>Class or session packs (billing_type_id = 3) and limit_total_classes is True</b>'",
    )
    pass_expiration: Optional[int] = Field(
        None,
        description="Required only if <i>Billing Type</i> is '<b>Class or session packs (billing_type_id = 3) and limit_total_classes is True</b>'",
    )
    pass_expiration_duration_type_id: Optional[int] = Field(
        None,
        description="Required only if <i>Billing Type</i> is '<b>Class or session packs (billing_type_id = 3) and limit_total_classes is True</b>'. Refer to GET /duration_types for ids",
    )
    plan_status_type_id: int = Field(None, title="Plan Status", description="Refer to GET /plan_status_types for ids")
    trial: Optional[bool] = Field(
        None,
        title="Trial",
        description="Use this with <b>challenge</b> to determine whether to hide or show the section. If either trial or challenge is True then enable the section",
    )
    challenge: Optional[bool] = Field(
        None,
        title="Challenge",
        description="Use this with <b>trial</b> to determine whether to hide or show the section. If either trial or challenge is True then enable the section",
    )
    grandfathered: Optional[bool] = Field(None, title="Grandfathered", description="")
    check_in_required: Optional[bool] = Field(None, title="Check-in Required")
    booking_required: Optional[bool] = Field(None, title="Booking Required")
    min_age: Optional[int] = Field(
        None,
        title="Minimum Age",
        description="Use this with <b>Maximun Age</b> to determine whether to hide or show the section. If either min_age or max_age is not 0 then enable the section",
    )
    max_age: Optional[int] = Field(
        None,
        title="Maximum Age",
        description="Use this with <b>Minimum Age</b> to determine whether to hide or show the section. If either min_age or max_age is not 0 then enable the section",
    )
    access_for_24_hrs: Optional[bool] = Field(None, title="Access for 24 hours")
    revenue_rate: Optional[float] = Field(None, title="Revenue rate")
    location_permissions: Optional[List[int]] = Field(
        None,
        title="Location Permissions",
        description="List of location ids for this business that this plan gives access to",
    )
    membership_type_id: Optional[int] = Field(None, title="Membership Type")
    sessions_count: Optional[int] = Field(None, description="Initial Session Packs")
    sessions_limit_times: Optional[int] = Field(None, description="Group sessions limits X times")
    sessions_limit_every: Optional[int] = Field(None, description="Group sessions limits every Y")
    sessions_limit_duration_type_id: Optional[int] = Field(
        None,
        description="The Z in 'Group sessions limits X times every Y (Z)'. Refer to GET /duration_types for ids",
    )
    first_of_month: Optional[bool] = Field(None, title="1st of month recurring")
    taxable: Optional[bool] = Field(None, title="Taxable")
    apply_weekly_registration_limits: Optional[bool] = Field(
        False,
        title="apply_weekly_registration_limits",
        description="Indicates whether weekly session limits (MON-SUN) should be applied",
    )
    weekly_limit_times: Optional[int] = Field(None, description="weekly(MON-SUN) sessions limits X times")
    class_access_groups: Optional[List[int]] = Field([], title="Class Access Groups")


class UpdatePlanRequest(CreatePlanRequest):
    plan_id: int = Field(title="Plan id", description=" ")
