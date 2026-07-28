from fastapi import APIRouter, Depends

from gmsshared.src.util.enums import ReportTypeEnum
from reports_service.dtos.reports_requests import ReportsQuery
from reports_service.services.reports_svc import get_report
from gmsshared.src.web.fastapi_glue import check_access, to_utc


reports_private_api = APIRouter(tags=["Reports Service"])


@reports_private_api.get("/locations/{location_id}/{report}")
@to_utc(fields=["report_date_from", "report_date_to"])
def sales_report(
    location_id: int,
    report: ReportTypeEnum,
    query: ReportsQuery = Depends(),
    _=Depends(check_access()),
):
    return get_report(location_id, report.name, query)
