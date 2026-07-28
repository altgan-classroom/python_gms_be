from fastapi import APIRouter

from auth_admin_service.auth.endpoints.auth_public_api import auth_public_api
from auth_admin_service.auth.endpoints.auth_private_api import auth_private_api
from auth_admin_service.auth.endpoints.health_api import health_api
from auth_admin_service.admin.endpoints.admin_gym_api import admin_gym_api
from auth_admin_service.admin.endpoints.admin_location_api import admin_location_api
from auth_admin_service.admin.endpoints.admin_user_api import admin_user_api

auth_bp = APIRouter(prefix="/api/v1.1")

auth_bp.include_router(auth_public_api)
auth_bp.include_router(auth_private_api)
auth_bp.include_router(admin_gym_api)
auth_bp.include_router(admin_location_api)
auth_bp.include_router(admin_user_api)
auth_bp.include_router(health_api)
