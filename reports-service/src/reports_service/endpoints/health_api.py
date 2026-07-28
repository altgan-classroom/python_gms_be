from fastapi import APIRouter

from reports_service.services.health_svc import get_reports_health_info

health_api = APIRouter(tags=["Service Health"])


@health_api.get("/health")
def get_members_health():
    return get_reports_health_info()
