from fastapi import APIRouter

from reports_service.endpoints.health_api import health_api
from reports_service.endpoints.reports_private_api import reports_private_api

reports_api = APIRouter(prefix="/api/v1/reports")

reports_api.include_router(health_api)
reports_api.include_router(reports_private_api)
