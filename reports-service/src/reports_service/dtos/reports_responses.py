from datetime import datetime
from typing import List, Annotated, Self, Optional

from pydantic import (
    BaseModel,
    AfterValidator,
    model_validator,
    Field,
    BeforeValidator,
    EmailStr,
    field_validator,
)

from gmsshared.src.util.enums import AttendanceStatusEnum
from gmsshared.src.util.responses import BaseResponse
from gmsshared.src.util.validators import (
    report_field_validator,
    attendance_report_period_validator,
    attendance_report_month_validator,
    to_local,
)


class RecordsList(BaseModel):
    reports: List[dict]
    from_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="Start of date range for reports"
    )
    to_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="End of date range for reports"
    )


class ReportsResponse(BaseResponse):
    data: RecordsList | None


class NewContact(BaseModel):
    contact_type: int
    name: str
    date_added: Annotated[str | None, AfterValidator(report_field_validator)]
    start_date: Annotated[str | None, AfterValidator(report_field_validator)]
    plan_id: Annotated[str | None, AfterValidator(report_field_validator)]


class NewContactList(BaseModel):
    contacts: List[NewContact]


class NewSales(BaseModel):
    plan_name: str
    billing_type: str | None
    number_of_new_sales: int
    fecc: float
    new_contract_value_added: float


class NewSalesList(BaseModel):
    sales: List[NewSales]

    @model_validator(mode="after")
    def add_total_report(self) -> Self:
        total = {
            "plan_name": "Total",
            "billing_type": None,
            "number_of_new_sales": 0,
            "fecc": 0,
            "new_contract_value_added": 0,
        }

        for sale in self.sales:
            total["number_of_new_sales"] = total["number_of_new_sales"] + sale.number_of_new_sales
            total["fecc"] = total["fecc"] + sale.fecc
            total["new_contract_value_added"] = total["new_contract_value_added"] + sale.new_contract_value_added

        self.sales.append(NewSales.model_validate(total, from_attributes=True))

        return self


class Attendance(BaseModel):
    member_id: int
    year: Annotated[int, BeforeValidator(attendance_report_period_validator)] = Field(..., alias="session_year")

    month: Annotated[int, BeforeValidator(attendance_report_month_validator)] = Field(..., alias="session_month")
    attended: int | None = Field(..., alias="attended_sessions")
    cancelled: int | None = Field(..., alias="cancelled_sessions")
    no_shows: int | None = Field(..., alias="no_show_sessions")

    @model_validator(mode="after")
    def validate_att(self) -> Self:
        if self.attended is None:
            self.attended = 0
        if self.cancelled is None:
            self.cancelled = 0
        if self.no_shows is None:
            self.no_shows = 0
        return self


class AttendanceList(BaseModel):
    monthly_attendance: List[Attendance]


class ContactAttendance(BaseModel):
    session_date: Annotated[datetime | str | None, AfterValidator(to_local)]
    session_name: str
    attendance_status: AttendanceStatusEnum


class MemberSessionAttendance(BaseModel):
    member_id: int = Field(..., description="ID of member")
    last_visit_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="Date of the last visit"
    )
    last_visit_session_name: str | None = Field(..., description="Name of the last visit session")
    next_scheduled_session_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="Date of next scheduled session"
    )
    next_scheduled_session_name: str | None = Field(..., description="Name of next scheduled session")
    total_sessions_attended: int | None = Field(..., description="Total sessions attended (lifetime)")


class LocationMembershipCount(BaseModel):
    full_members: int
    challengers: int
    limited_time_pass: int


class AtRiskAttendance(BaseModel):
    name: str = Field(..., description="Member's full name")
    phone: str | None = Field(None, description="Member's phone number")
    email: EmailStr = Field(..., description="Member's email address")
    plan_names: str = Field(..., description="Plans linked to the member")
    last_attended_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        None, description="Last time the member attended a session"
    )
    last_scheduled_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        None, description="Last booking date for the member"
    )


class MemberPaymentHistoryReport(BaseModel):
    total_revenue_received: float | None = Field(..., description="Net revenue received")
    total_revenue_plans: float | None = Field(..., description="Total revenue plans")
    total_fees_revenue: float | None = Field(..., description="Total fees revenue")
    other_revenue: float | None = Field(None, description="Other revenue")

class MTDReport(BaseModel):
    signup_fees: float | None = Field(None, description="Signup fees")
    membership_fees: float | None = Field(None, description="Membership fees")
    late_fees: float | None = Field(None, description="Late fees")
    cancellation_fees: float | None = Field(None, description="Cancellation fees")
    no_show_fees: float | None = Field(None, description="No show fees")
    others: float | None = Field(None, description="Other revenue")
    discounts: float | None = Field(None, description="Discounts")
    sub_total: float | None = Field(None, description="Sub total")
    total_taxes: float | None = Field(None, description="Total taxes")
    total_invoice_value: float | None = Field(None, description="Total invoice value")
    credit_card_payments: float | None = Field(None, description="Credit card payments")
    debit_card_payments: float | None = Field(None, description="Debit card payments")
    ach_payments: float | None = Field(None, description="Ach payments")
    cash_payments: float | None = Field(None, description="Cash payments")
    credit_memos: float | None  = Field(None, description="Credit Memos")
    refunds: float | None = Field(None, description="Refunds")
    total_payments: float | None = Field(None, description="Total payments")

class ForecastedRevenueReport(BaseModel):
    revenue: float | None = Field(..., description="Total forecasted revenue")


class BalanceAndFutureContractValueReport(BaseModel):
    contact: str = Field(..., description="Contact fullname")
    plan: str = Field(..., description="Membership plan name")
    future_contract_value: float = Field(..., description="Future contract value")
    balance: float = Field(..., description="Total balance (due to date)")
    member_id: int = Field(..., description="ID of member for this balance")


class RecurringMemberChurnReport(BaseModel):
    plan_name: str = Field(..., description="Name of plan")
    plan_total: int = Field(..., description="Total of plans")
    plan_total_exited: int = Field(..., description="Total of exited plans")
    churn_percentage: float = Field(..., description="Percentage of members who churned out")
    billing_type: str = Field(..., description="Membership billing type")
    plan_type: str = Field(..., description="Membership plan type")


class RecurringMemberChurnList(BaseModel):
    churns: List[RecurringMemberChurnReport]

    @model_validator(mode="after")
    def add_total_report(self) -> Self:
        total: dict = {
            "plan_name": "Total",
            "plan_total": 0,
            "plan_total_exited": 0,
            "churn_percentage": 0,
            "billing_type": "All",
            "plan_type": "All",
        }

        for churn in self.churns:
            total["plan_total"] = total["plan_total"] + churn.plan_total
            total["plan_total_exited"] = total["plan_total_exited"] + churn.plan_total_exited

        total["churn_percentage"] = float("{:.2f}".format(total["plan_total_exited"] * 100 / total["plan_total"]))

        self.churns.append(RecurringMemberChurnReport.model_validate(total, from_attributes=True))

        return self


class ChallengeConversionsCohortDetailReport(BaseModel):
    member_id: int = Field(..., description="ID of member")
    member_name: str = Field(..., description="Full name of member")
    converted: str = Field(..., description="Whether member challenge plan was converted to full or not")
    challenge_start_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="Date when challenge plan began"
    )
    challenge_end_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="Date when challenge plan ended"
    )
    challenge_plan_name: str = Field(..., description="Challenge plan from which member converted")
    full_membership_plan: str = Field(..., description="Full membership plan to which member converted")


class ChallengeConversionsCohortSummaryReport(BaseModel):
    challenge_plan: str = Field(..., description="Challenge plan name")
    cohort_month: str = Field(..., description="Cohort month name")
    total_participants: int = Field(..., description="Number of total participants for cohort month")
    cohort_end_date: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        ..., description="Plan end date for cohort month"
    )
    members_converted: int = Field(..., description="Number of members who converted to full membership")
    conversion_rate_percentage: int | None = Field(
        ..., description="Percentage of members who converted to full membership"
    )

    @model_validator(mode="after")
    def calculate_conversion_rate_percentage(self) -> Self:
        if self.members_converted == 0 or self.total_participants == 0:
            self.conversion_rate_percentage = None
            return self
        conversion_rate: int = int((self.members_converted * 100) / self.total_participants)
        self.conversion_rate_percentage = conversion_rate
        return self
