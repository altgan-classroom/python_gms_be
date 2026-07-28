from fastapi import APIRouter

from plans_classes_service.plans.endpoints.health_api import health_api
from plans_classes_service.plans.endpoints.plans_private_api import plans_private_api
from plans_classes_service.classes.endpoints.classes_private_api import (
    classes_private_api,
)

plans_classes_api = APIRouter(prefix="/api/v1")

plans_classes_api.include_router(plans_private_api)
plans_classes_api.include_router(classes_private_api)
plans_classes_api.include_router(health_api)
