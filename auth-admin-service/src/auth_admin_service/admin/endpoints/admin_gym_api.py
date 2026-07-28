from fastapi import APIRouter, Depends

from auth_admin_service.admin.dtos.admin_requests import (
    UpdateGymRequest,
    UpdateGymMainSettingsRequest,
    UpdateGymClassSettingsRequest,
)
from auth_admin_service.admin.services.admin_gym_svc import (
    update_gym_info,
    get_gym_main_settings_info,
    update_gym_main_settings_info,
    get_gym_class_settings_info,
    update_gym_class_settings_info,
)
from gmsshared.src.web.fastapi_glue import check_access

_ROLES = ["OWNER", "STAFF", "MANAGER", "COACH"]
admin_gym_api = APIRouter(prefix="/admin", tags=["Gym APIs"])


@admin_gym_api.put("/gyms/{gym_id}")
def update_gym(gym_id: int, body: UpdateGymRequest, _=Depends(check_access(roles=_ROLES))):
    return update_gym_info(gym_id, body)


@admin_gym_api.get("/gyms/{gym_id}/main/settings")
def get_gym_main_settings(gym_id: int, _=Depends(check_access(roles=_ROLES))):
    return get_gym_main_settings_info(gym_id)


@admin_gym_api.put("/gyms/{gym_id}/main/settings")
def update_gym_main_settings(gym_id: int, body: UpdateGymMainSettingsRequest, _=Depends(check_access(roles=_ROLES))):
    return update_gym_main_settings_info(gym_id, body)


@admin_gym_api.get("/gyms/{gym_id}/class/settings")
def get_gym_class_settings(gym_id: int, _=Depends(check_access(roles=_ROLES))):
    return get_gym_class_settings_info(gym_id)


@admin_gym_api.put("/gyms/{gym_id}/class/settings")
def update_gym_class_settings(gym_id: int, body: UpdateGymClassSettingsRequest, _=Depends(check_access(roles=_ROLES))):
    return update_gym_class_settings_info(gym_id, body)
