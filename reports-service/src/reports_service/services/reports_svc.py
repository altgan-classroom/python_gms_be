from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from http import HTTPStatus
from typing import List

from fastapi.responses import JSONResponse as Response
from gmsshared.src.models.member_payment_history import MemberPaymentHistory
from gmsshared.src.models.report import Report
from gmsshared.src.util.datetime_util import time_replace, time_str_replace, utc_now
from gmsshared.src.util.enums import (
    SalesReportTypeEnum,
    OperationsReportTypeEnum,
    FinancialReportTypeEnum,
    ResponseStatusEnum,
)
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.validators import (
    to_local,
    to_local_for_return_datetime_obj,
    to_utc
)
from pytz import timezone
from pytz.tzinfo import StaticTzInfo

from reports_service.dtos.reports_requests import ReportsQuery
from reports_service.dtos.reports_responses import (
    ReportsResponse,
    RecordsList,
    NewContactList,
    NewContact,
    NewSalesList,
    NewSales,
    AttendanceList,
    Attendance,
    MemberSessionAttendance,
    LocationMembershipCount,
    AtRiskAttendance,
    MemberPaymentHistoryReport,
    BalanceAndFutureContractValueReport,
    RecurringMemberChurnReport,
    ChallengeConversionsCohortDetailReport,
    ChallengeConversionsCohortSummaryReport,
    RecurringMemberChurnList,
    ForecastedRevenueReport,
    ContactAttendance,
)
from functools import wraps

from gmsshared.src.util.exceptions import ApiForbidden
from gmsshared.src.web.fastapi_glue import g


def check_access(roles=None):
    """Role guard for internal report helpers.

    The request token is validated and ``g.user`` is populated by the
    endpoint-level ``Depends(check_access())`` dependency. This decorator only
    re-enforces the per-report role restriction that the Flask version applied
    via ``@check_access(roles=[...])`` on these helper functions."""

    def decorate(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if roles:
                user = g.get("user")
                if user is None or user.role.name.upper() not in roles:
                    raise ApiForbidden(
                        description="You do not have the proper role to access this resource"
                    )
            return fn(*args, **kwargs)

        return decorated

    return decorate


def get_report(location_id: int, report: str, query: ReportsQuery) -> Response:
    response: Response
    query = _update_query_dates(query)
    report_type = _report_exists(report)
    if not report_type:
        response = create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_REQUEST,
            message=f"Unknown report type {report}",
            data=None,
        )
    elif report_type in SalesReportTypeEnum:
        return _get_sales_report(location_id, report_type, query)
    elif report_type == OperationsReportTypeEnum.MEMBER_SESSIONS_ATTENDANCE:
        return __get_member_session_attendance_lifetime(location_id, query)
    elif report_type == OperationsReportTypeEnum.CONTACT_ATTENDANCE_HISTORY:
        return get_contact_attendance_history(location_id, query)
    elif report_type in OperationsReportTypeEnum:
        return _get_operations_report(location_id, report_type, query)
    elif report_type in FinancialReportTypeEnum:
        return _get_financial_report(location_id, report_type, query)
    else:
        response = create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_REQUEST,
            message=f"Report type {report} not implemented yet",
            data=None,
        )
    return create_response(**response.model_dump())


def _update_query_dates(query: ReportsQuery) -> ReportsQuery:
    now = utc_now()
    month_to_date_from_date = datetime(now.year, now.month, 1, 0, 0, 0)
    if not query.report_date_from:
        query.report_date_from = month_to_date_from_date
    if not query.report_date_to:
        query.report_date_to = now
    return query


def _get_sales_report(location_id: int, report: SalesReportTypeEnum, query: ReportsQuery) -> Response:
    response: ReportsResponse
    if report == SalesReportTypeEnum.NEW_CONTACTS:
        response = __get_sales_new_contacts_report(location_id, query)
    elif report == SalesReportTypeEnum.NEW_MEMBERSHIP_SALES:
        response = __get_sales_new_sales_report(location_id, query)
    else:
        response = ReportsResponse(
            status_code=HTTPStatus,
            status=ResponseStatusEnum.NOT_IMPLEMENTED,
            message=f"Sales report {report.value} not implemented yet",
            data=RecordsList.model_validate(
                {
                    "reports": [query.model_dump(mode="json")],
                    "from_date": query.report_date_from,
                    "to_date": query.report_date_to,
                },
                from_attributes=True,
            ),
        )
    return create_response(**response.model_dump())


def __get_sales_new_contacts_report(location_id: int, query: ReportsQuery) -> ReportsResponse:
    contacts: List[dict]
    if query.filter:
        contacts = Report.new_contacts_filter(location_id, query.report_date_from, query.report_date_to, query.filter)
    else:
        contacts = Report.new_contacts(location_id, query.report_date_from, query.report_date_to)
    if len(contacts) > 0:
        new_contacts: NewContactList = NewContactList(
            contacts=[NewContact.model_validate(contact, from_attributes=True) for contact in contacts]
        )
        reports = [new_contact.model_dump() for new_contact in new_contacts.contacts]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Sales New Contact Report: {len(reports)} records found",
            data=RecordsList.model_validate(
                {
                    "reports": reports,
                    "from_date": query.report_date_from,
                    "to_date": query.report_date_to,
                },
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Sales New Contact Reports: no records found",
            data=None,
        )
    return response


@check_access(roles=["OWNER", "MANAGER"])
def __get_sales_new_sales_report(location_id: int, query: ReportsQuery) -> ReportsResponse:
    sales: List[dict]
    if query.filter:
        sales = Report.new_membership_sales_filter(
            location_id, query.report_date_from, query.report_date_to, query.filter
        )
    else:
        sales = Report.new_membership_sales(location_id, query.report_date_from, query.report_date_to)
    if len(sales) > 0:
        new_sales: NewSalesList = NewSalesList(
            sales=[NewSales.model_validate(sale, from_attributes=True) for sale in sales]
        )
        reports = [new_sale.model_dump() for new_sale in new_sales.sales]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Sales New Sales Report: {len(reports)} records found",
            data=RecordsList.model_validate(
                {
                    "reports": reports,
                    "from_date": query.report_date_from,
                    "to_date": query.report_date_to,
                },
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Sales New Sales Reports: no records found",
            data=None,
        )
    return response


def _get_operations_report(location_id: int, report: OperationsReportTypeEnum, query: ReportsQuery) -> Response:
    response: ReportsResponse
    if report == OperationsReportTypeEnum.CONTACT_ATTENDANCE_PER_MONTH:
        response = __get_contact_attendance_per_year(location_id, query)
    elif report == OperationsReportTypeEnum.LOCATION_MEMBERSHIP_COUNT:
        response = __get_location_membership_count(location_id)
    elif report == OperationsReportTypeEnum.AT_RISK_ATTENDANCE:
        response = __get_at_risk_attendance(location_id, query)
    elif report == OperationsReportTypeEnum.RECURRING_MEMBER_CHURN:
        response = __get_recurring_member_churn(location_id, query)
    elif report == OperationsReportTypeEnum.CHALLENGE_CONVERSION_BY_COHORT_DETAIL:
        response = __get_challenge_conversions_cohort_detail(location_id, query)
    elif report == OperationsReportTypeEnum.CHALLENGE_CONVERSION_BY_COHORT_SUMMARY:
        response = __get_challenge_conversions_cohort_summary(location_id, query)
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_IMPLEMENTED,
            message=f"Operations report {report.value} not implemented yet",
            data=RecordsList.model_validate(
                {
                    "reports": [query.model_dump(mode="json")],
                    "from_date": query.report_date_from,
                    "to_date": query.report_date_to,
                },
                from_attributes=True,
            ),
        )
    return create_response(**response.model_dump())


def __get_contact_attendance_per_year(location_id: int, query: ReportsQuery) -> ReportsResponse:
    attendance_per_year: List[dict]
    if query.filter:
        attendance_per_year = Report.contact_attendance_filter(
            location_id, query.report_date_from, query.filter, query.report_date_to
        )
    else:
        attendance_per_year = Report.contact_attendance(location_id, query.report_date_from, query.report_date_to)
    if attendance_per_year:
        attendance: AttendanceList = AttendanceList(
            monthly_attendance=[Attendance.model_validate(att, from_attributes=True) for att in attendance_per_year]
        )
        reports = [new_contact.model_dump() for new_contact in attendance.monthly_attendance]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Member Attendance Report: {len(reports)} records found",
            data=RecordsList.model_validate(
                {
                    "reports": reports,
                    "from_date": query.report_date_from,
                    "to_date": query.report_date_to,
                },
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Member Attendance Report: no records found",
            data=None,
        )
    return response


def __get_member_session_attendance_lifetime(location_id: int, query: ReportsQuery) -> Response:
    member_attendance_lifetime: List[dict] | None
    if (not query) or (not query.filter):
        member_attendance_lifetime = Report.member_sessions_attendance_report(location_id)
    else:
        if len(query.filter.keys()) == 1 and query.filter.get("member_id", None) is not None:
            member_attendance_lifetime = Report.member_sessions_attendance_report(
                location_id, query.filter["member_id"]
            )
        else:
            member_attendance_lifetime = Report.member_sessions_attendance_report_filter(location_id, query.filter)
    if len(member_attendance_lifetime) > 0:
        reports = [
            MemberSessionAttendance.model_validate(att, from_attributes=True).model_dump()
            for att in member_attendance_lifetime
        ]
        data = {"reports": reports}
        response = create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Member Session Attendance Report: {len(reports)} records found",
            data=data,
        )
    else:
        response = create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Member Session Attendance Report: no records found",
            data=None,
        )
    return response


@check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])
def get_contact_attendance_history(location_id: int, query: ReportsQuery) -> Response:
    attendance_history: List[dict] = Report.contact_attendance_history(
        location_id, query.member_id, query.report_date_from, query.report_date_to
    )
    if len(attendance_history) > 0:
        records = [
            ContactAttendance.model_validate(att, from_attributes=True).model_dump() for att in attendance_history
        ]
        response = create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Contact Attendance History Report: {len(records)} records found",
            data=records,
        )
    else:
        response = create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Contact Attendance History Report: no records found",
            data=None,
        )
    return response


def __get_location_membership_count(location_id: int) -> ReportsResponse:
    location_membership_count: List[dict] = Report.location_membership_type_count_report(location_id)
    if len(location_membership_count) > 0:
        reports = [
            LocationMembershipCount.model_validate(count, from_attributes=True).model_dump()
            for count in location_membership_count
        ]
        data = RecordsList.model_validate(
            {"reports": reports, "from_date": None, "to_date": datetime.utcnow()},
            from_attributes=True,
        )
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message="Location Memberships Count Report found",
            data=data,
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Location Memberships Count Report not found",
            data=None,
        )
    return response


def __get_at_risk_attendance(location_id: int, query: ReportsQuery) -> ReportsResponse:
    def last_sunday_at_midnight() -> datetime:
        now = datetime.now()
        days_to_subtract = (now.weekday() - 6) % 7
        last_sunday = now - timedelta(days=days_to_subtract)
        last_sunday_at_midnite = last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        return to_utc(last_sunday_at_midnite)

    def reports_time_to_local(at_risk_reports: List[dict]) -> None:
        for i in range(len(at_risk_reports)):
            last_attended: str | None = at_risk_reports[i]["last_attended_date"]
            if last_attended == "Never":
                last_attended = None
            at_risk_reports[i]["last_attended_date"] = to_location_time_str(location_id, last_attended)
            last_scheduled: str | None = at_risk_reports[i]["last_scheduled_date"]
            if last_scheduled == "Never":
                last_scheduled = None
            at_risk_reports[i]["last_scheduled_date"] = to_location_time_str(location_id, last_scheduled)

    at_risk_attendance: List[dict]
    from_date: datetime = last_sunday_at_midnight()
    local_to_date: datetime = datetime.strptime(to_local(datetime.utcnow()), "%Y-%m-%d %H:%M")
    if query.filter:
        at_risk_attendance = Report.at_risk_attendance_reports_filter(location_id, from_date, query.filter)
    else:
        at_risk_attendance = Report.at_risk_attendance_report(location_id, from_date)
    if len(at_risk_attendance) > 0:
        reports = [
            AtRiskAttendance.model_validate(report, from_attributes=True).model_dump() for report in at_risk_attendance
        ]
        reports_time_to_local(reports)
        data = RecordsList.model_validate(
            {"reports": reports, "from_date": from_date, "to_date": datetime.utcnow()},
            from_attributes=True,
        )
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"At Risk Attendance Report found, from {to_location_time(location_id, from_date).date()} 00:00 to {local_to_date.date()} {local_to_date.hour}:{'0' if local_to_date.minute < 10 else ''}{local_to_date.minute} (now)",
            data=data,
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="At Risk Attendance Report not found",
            data=None,
        )
    return response


@check_access(roles=["OWNER", "MANAGER"])
def __get_recurring_member_churn(location_id: int, query: ReportsQuery) -> ReportsResponse:
    recurring_member_churn: List[dict]
    if query.filter:
        recurring_member_churn = Report.recurring_member_churn_report_filter(
            location_id, query.report_date_from, query.report_date_to, query.filter
        )
    else:
        recurring_member_churn = Report.recurring_member_churn_report(
            location_id, query.report_date_from, query.report_date_to
        )
    if len(recurring_member_churn) > 0:
        member_churn: RecurringMemberChurnList = RecurringMemberChurnList(
            churns=[
                RecurringMemberChurnReport.model_validate(rmc, from_attributes=True).model_dump()
                for rmc in recurring_member_churn
            ]
        )
        reports = [churn.model_dump() for churn in member_churn.churns]
        data = RecordsList.model_validate(
            {
                "reports": reports,
                "from_date": query.report_date_from,
                "to_date": (query.report_date_to if query.report_date_to < datetime.utcnow() else datetime.utcnow()),
            },
            from_attributes=True,
        )
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message="Recurring Member Churn Report found",
            data=data,
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Recurring Member Churn Report not found",
            data=None,
        )
    return response


def __get_challenge_conversions_cohort_detail(location_id: int, query: ReportsQuery) -> ReportsResponse:
    challenge_conversions_cohort_detail: List[dict]
    if query.filter:
        challenge_conversions_cohort_detail = Report.challenge_conversions_cohort_detail_report_filter(
            location_id, query.filter, query.report_date_from, query.report_date_to
        )
    else:
        challenge_conversions_cohort_detail = Report.challenge_conversions_cohort_detail_report(
            location_id, query.report_date_from, query.report_date_to
        )
    if len(challenge_conversions_cohort_detail) > 0:
        reports = [
            ChallengeConversionsCohortDetailReport.model_validate(cchd, from_attributes=True).model_dump()
            for cchd in challenge_conversions_cohort_detail
        ]
        data = RecordsList.model_validate(
            {
                "reports": reports,
                "from_date": query.report_date_from,
                "to_date": query.report_date_to,
            },
            from_attributes=True,
        )
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message="Challenge Conversions Cohort Detail Report found",
            data=data,
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Challenge Conversions Cohort Detail Report not found",
            data=None,
        )
    return response


def __get_challenge_conversions_cohort_summary(location_id: int, query: ReportsQuery) -> ReportsResponse:
    challenge_conversions_cohort_summary: List[dict]
    if query.filter:
        challenge_conversions_cohort_summary = Report.challenge_conversions_cohort_summary_report_filter(
            location_id, query.filter, query.report_date_from, query.report_date_to
        )
    else:
        challenge_conversions_cohort_summary = Report.challenge_conversions_cohort_summary_report(
            location_id, query.report_date_from, query.report_date_to
        )
    if len(challenge_conversions_cohort_summary) > 0:
        reports = [
            ChallengeConversionsCohortSummaryReport.model_validate(cchs, from_attributes=True).model_dump()
            for cchs in challenge_conversions_cohort_summary
        ]
        data = RecordsList.model_validate(
            {
                "reports": reports,
                "from_date": query.report_date_from,
                "to_date": query.report_date_to,
            },
            from_attributes=True,
        )
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message="Challenge Conversions Cohort Detail Report found",
            data=data,
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Challenge Conversions Cohort Detail Report not found",
            data=None,
        )
    return response


def _get_financial_report(location_id: int, report: FinancialReportTypeEnum, query: ReportsQuery) -> Response:
    response: ReportsResponse
    if report == FinancialReportTypeEnum.MTD_REVENUE:
        response = __get_financial_month_to_date_report(location_id)
    elif report == FinancialReportTypeEnum.LAST_MONTH_REVENUE:
        response = __get_financial_last_month_report(location_id)
    elif report == FinancialReportTypeEnum.FORECASTED_REVENUE:
        response = __get_financial_forecasted_revenue(location_id)
    elif report == FinancialReportTypeEnum.BALANCE_AND_FUTURE_CONTRACT_VALUE:
        response = __get_balance_and_future_contract_value_report(location_id, query)
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_IMPLEMENTED,
            message=f"Financial report {report.value} not implemented yet",
            data=RecordsList.model_validate(
                {
                    "reports": [query.model_dump(mode="json")],
                    "from_date": query.report_date_from,
                    "to_date": query.report_date_to,
                },
                from_attributes=True,
            ),
        )
    return create_response(**response.model_dump())


@check_access(roles=["OWNER", "MANAGER"])
def __get_financial_month_to_date_report(location_id: int) -> ReportsResponse:
    today: datetime = to_local_for_return_datetime_obj(datetime.now())
    from_date: datetime = to_utc(datetime(today.year, today.month, 1, 0, 0, 0))
    to_date: datetime = to_utc(datetime(today.year, today.month, today.day, 23, 59, 59))
    finances: List[dict] = Report.member_payment_history_report(location_id, from_date, to_date)
    if len(finances) > 0:
        reports = [
            MemberPaymentHistoryReport.model_validate(mtd, from_attributes=True).model_dump() for mtd in finances
        ]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Financial Month to Date Revenue Report: {len(reports)} records found",
            data=RecordsList.model_validate(
                {"reports": reports, "from_date": from_date, "to_date": to_date},
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Financial Month to Date Revenue Report: no records found",
            data=None,
        )
    return response


@check_access(roles=["OWNER", "MANAGER"])
def __get_financial_last_month_report(location_id: int) -> ReportsResponse:
    current_date: datetime = to_local_for_return_datetime_obj(datetime.now())
    current_year, current_month = current_date.year, current_date.month
    december, is_january = 12, current_month == 1
    last_month = december if is_january else current_month - 1
    year_of_last_month = current_year - 1 if is_january else current_year
    last_day_of_last_month = monthrange(year_of_last_month, last_month)[1]
    from_date: datetime = to_utc(datetime(year_of_last_month, last_month, 1, 0, 0, 0))
    to_date: datetime = to_utc(datetime(year_of_last_month, last_month, last_day_of_last_month, 23, 59, 59))
    finances: List[dict] = Report.member_payment_history_report(location_id, from_date, to_date)
    if len(finances) > 0:
        reports = [
            MemberPaymentHistoryReport.model_validate(mtd, from_attributes=True).model_dump() for mtd in finances
        ]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Financial Last Month Revenue Report: {len(reports)} records found",
            data=RecordsList.model_validate(
                {"reports": reports, "from_date": from_date, "to_date": to_date},
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Financial Last Month Revenue Report: no records found",
            data=None,
        )
    return response


@check_access(roles=["OWNER", "MANAGER"])
def __get_financial_forecasted_revenue(location_id: int) -> ReportsResponse:
    now = to_local_for_return_datetime_obj(datetime.now())
    first_day_next_month = now.replace(day=1) + relativedelta(months=1)
    last_day_next_month = first_day_next_month + relativedelta(months=1, days=-1)
    finances: List[dict] = Report.member_payment_schedule_report(location_id=location_id,
                                                                 from_date=first_day_next_month,
                                                                 to_date=last_day_next_month)
    if len(finances) > 0:
        reports = [ForecastedRevenueReport.model_validate(mtd, from_attributes=True).model_dump() for mtd in finances]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Forecasted Revenue Report: {len(reports)} records found",
            data=RecordsList.model_validate(
            {"reports": reports, "from_date": first_day_next_month, "to_date": last_day_next_month},
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Forecasted Revenue Report: no records found",
            data=None,
        )
    return response


@check_access(roles=["OWNER", "MANAGER"])
def __get_balance_and_future_contract_value_report(location_id: int, query: ReportsQuery) -> ReportsResponse:
    finances: List[dict]
    if query.filter:
        finances = Report.balance_and_future_contract_value_report_filter(location_id, query.filter)
    else:
        finances = Report.balance_and_future_contract_value_report(location_id)
    if len(finances) > 0:
        reports = [
            BalanceAndFutureContractValueReport.model_validate(bfcv, from_attributes=True).model_dump()
            for bfcv in finances
        ]
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            message=f"Financial Balance and Future Contract Value Report: {len(reports)} records found",
            data=RecordsList.model_validate(
                {"reports": reports, "from_date": None, "to_date": None},
                from_attributes=True,
            ),
        )
    else:
        response = ReportsResponse(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            message="Financial Balance and Future Contract Value Report: no records found",
            data=None,
        )
    return response


def _report_exists(
    report: str,
) -> SalesReportTypeEnum | OperationsReportTypeEnum | FinancialReportTypeEnum | None:
    if report in vars(SalesReportTypeEnum).keys():
        return SalesReportTypeEnum[report]
    elif report in vars(OperationsReportTypeEnum).keys():
        return OperationsReportTypeEnum[report]
    elif report in vars(FinancialReportTypeEnum).keys():
        return FinancialReportTypeEnum[report]
    else:
        return None


def to_location_time(location_id: int, utc_time: datetime) -> datetime:
    utc: StaticTzInfo = timezone("Etc/UTC")
    tzdata = Report.location_timezone(location_id)
    location_timezone: StaticTzInfo = timezone(tzdata)
    return time_replace(utc_time, utc, location_timezone)


def to_location_time_str(location_id: int, utc_time: str) -> str:
    utc: StaticTzInfo = timezone("Etc/UTC")
    tzdata = Report.location_timezone(location_id)
    location_timezone: StaticTzInfo = timezone(tzdata)
    return time_str_replace(utc_time, utc, location_timezone)
