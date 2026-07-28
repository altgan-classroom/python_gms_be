from fastapi import APIRouter, Depends

from auth_admin_service.auth.dtos.auth_requests import UpdateUserInfo
from auth_admin_service.auth.services.auth_private_svc import get_user_info, update_user_info
from gmsshared.src.web.fastapi_glue import check_access, g

auth_private_api = APIRouter(prefix="/auth", tags=["User Info"])


@auth_private_api.get("/user")
def get_user(_=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER", "KIOSK"]))):
    return get_user_info(g.user_id)


@auth_private_api.put("/user")
def update_user(
    body: UpdateUserInfo,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return update_user_info(g.user_id, body)
