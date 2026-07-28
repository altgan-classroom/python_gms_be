from fastapi import APIRouter, Depends

from auth_admin_service.auth.dtos.auth_requests import UploadRequest
from auth_admin_service.admin.dtos.admin_requests import (
    CreateUserRequest,
    UserPath,
    UpdateStaffProfileRequest,
    UserType,
)
from auth_admin_service.admin.services.admin_user_svc import (
    get_user_list,
    create_user,
    get_user_info,
    get_profile_info,
    update_staff_profile_info,
    delete_user_info,
)
from gmsshared.src.util import upload_service
from gmsshared.src.web.fastapi_glue import check_access, g

admin_user_api = APIRouter(prefix="/admin", tags=["User Admin APIs"])


@admin_user_api.get("/locations/{location_id}/users")
def get_users(
    location_id: int,
    query: UserType = Depends(),
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH", "KIOSK"])),
):
    return get_user_list(location_id, query)


@admin_user_api.post("/locations/{location_id}/users")
def new_user(
    location_id: int,
    body: CreateUserRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return create_user(location_id, body)


@admin_user_api.get("/locations/{location_id}/users/{user_id}")
def get_user(
    location_id: int,
    user_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_user_info(user_id, location_id)


@admin_user_api.get("/locations/{location_id}/users/{user_id}/profile")
def get_staff_profile(
    location_id: int,
    user_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return get_profile_info(user_id, location_id)


@admin_user_api.put("/locations/{location_id}/users/{user_id}/profile")
def update_staff_profile(
    location_id: int,
    user_id: int,
    body: UpdateStaffProfileRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return update_staff_profile_info(location_id, user_id, g.user.role.name.upper(), body)


@admin_user_api.get("/locations/{location_id}/users/{user_id}/presigned_url")
def get_presigned_url(
    location_id: int,
    user_id: int,
    query: UploadRequest = Depends(),
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return upload_service.get_presigned_url(UserPath(location_id=location_id, user_id=user_id), query)


@admin_user_api.delete("/locations/{location_id}/users/{user_id}/profile")
def delete_staff_profile(
    location_id: int,
    user_id: int,
    _=Depends(check_access(roles=["OWNER", "MANAGER", "COACH"])),
):
    return delete_user_info(location_id, user_id)
