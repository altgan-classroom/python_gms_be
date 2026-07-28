from fastapi import APIRouter

from auth_admin_service.auth.services.health_svc import get_auth_health_info

health_api = APIRouter(prefix="/auth", tags=["Service Health"])


@health_api.get("/health")
def get_auth_health():
    return get_auth_health_info()
