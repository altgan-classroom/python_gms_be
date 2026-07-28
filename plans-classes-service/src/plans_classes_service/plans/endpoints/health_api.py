from fastapi import APIRouter

from plans_classes_service.plans.services.health_svc import get_plans_health_info

health_api = APIRouter(prefix="/pp", tags=["Service Health"])


@health_api.get("/health")
def get_plans_health():
    return get_plans_health_info()
