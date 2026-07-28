from fastapi import APIRouter, Depends

from auth_admin_service.admin.dtos.admin_requests import (
    GetGymLocationsRequest,
    CreateLocationRequest,
    UpdateLocationRequest,
    LocationPath,
    CreateRoomRequest,
    UpdateRoomRequest,
    PayrixOnboardRequest,
    CreateDoorRequest,
    UpdateDoorRequest,
    UpdateDoorAccessSettingsRequest,
)
from auth_admin_service.admin.services.admin_location_svc import (
    door_access_member_sync_info,
    get_location_list,
    create_location_without_user,
    get_location_info,
    update_location_info,
    update_location_payrix_onboard_info,
    delete_location_info,
    get_rooms_list,
    create_room,
    get_room_info,
    update_room_info,
    delete_room_info,
    get_report_embed_url_info,
    get_all_user_reports,
    location_contact_info,
    create_new_door,
    get_doors,
    get_door,
    update_door_info,
    update_door_access_settings_info,
    get_door_access_auth_status,
)
from auth_admin_service.auth.dtos.auth_requests import UploadRequest
from gmsshared.src.util import upload_service
from gmsshared.src.web.fastapi_glue import check_access, g

_STD = ["OWNER", "STAFF", "MANAGER", "COACH"]
_WITH_MEMBER = ["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"]
_WITH_KIOSK = ["OWNER", "STAFF", "MANAGER", "COACH", "KIOSK"]

admin_location_api = APIRouter(prefix="/admin", tags=["Location APIs"])


@admin_location_api.get("/locations")
def get_locations(query: GetGymLocationsRequest = Depends(), _=Depends(check_access(roles=_WITH_KIOSK))):
    return get_location_list(query)


@admin_location_api.post("/locations")
def new_location(body: CreateLocationRequest, _=Depends(check_access(roles=_STD))):
    return create_location_without_user(body)


@admin_location_api.get("/locations/{location_id}")
def get_location(location_id: int, _=Depends(check_access(roles=_WITH_KIOSK))):
    return get_location_info(location_id)


@admin_location_api.put("/locations/{location_id}")
def update_location(location_id: int, body: UpdateLocationRequest, _=Depends(check_access(roles=_STD))):
    return update_location_info(location_id, body)


@admin_location_api.get("/locations/{location_id}/presigned_url")
def get_presigned_url(location_id: int, query: UploadRequest = Depends(), _=Depends(check_access(roles=_WITH_MEMBER))):
    return upload_service.get_presigned_url(LocationPath(location_id=location_id), query)


@admin_location_api.put("/locations/{location_id}/payrix_onboard")
def update_location_payrix_onboard(location_id: int, body: PayrixOnboardRequest, _=Depends(check_access(roles=_STD))):
    return update_location_payrix_onboard_info(location_id, body)


@admin_location_api.delete("/locations/{location_id}")
def delete_location(location_id: int, _=Depends(check_access(roles=_STD))):
    return delete_location_info(location_id)


@admin_location_api.get("/locations/{location_id}/rooms")
def get_rooms(location_id: int, _=Depends(check_access(roles=_STD))):
    return get_rooms_list(location_id)


@admin_location_api.post("/locations/{location_id}/rooms")
def new_room(location_id: int, body: CreateRoomRequest, _=Depends(check_access(roles=_STD))):
    return create_room(location_id, body)


@admin_location_api.get("/locations/{location_id}/rooms/{room_id}")
def get_room(location_id: int, room_id: int, _=Depends(check_access(roles=_STD))):
    return get_room_info(room_id, location_id)


@admin_location_api.put("/locations/{location_id}/rooms/{room_id}")
def update_room(location_id: int, room_id: int, body: UpdateRoomRequest, _=Depends(check_access(roles=_STD))):
    return update_room_info(room_id, location_id, body)


@admin_location_api.delete("/locations/{location_id}/rooms/{room_id}")
def delete_room(location_id: int, room_id: int, _=Depends(check_access(roles=_STD))):
    return delete_room_info(room_id, location_id)


@admin_location_api.get("/locations/{location_id}/reports")
def get_reports_embedded(location_id: int, _=Depends(check_access(roles=_STD))):
    return get_all_user_reports(location_id=location_id, user_id=g.user_id)


@admin_location_api.get("/locations/{location_id}/reports/{report_id}/url")
def get_report_embed_url(location_id: int, report_id: int, _=Depends(check_access(roles=_STD))):
    # NOTE: the Flask version also applied @check_report_access(); port that as a
    # dependency if per-report authorization is required.
    return get_report_embed_url_info(location_id, report_id)


@admin_location_api.get("/locations/{location_id}/contact_us")
def contact_us(location_id: int, _=Depends(check_access(roles=_WITH_MEMBER))):
    return location_contact_info(location_id)


@admin_location_api.post("/locations/{location_id}/door_access/doors")
def create_door(location_id: int, body: CreateDoorRequest, _=Depends(check_access(roles=_WITH_MEMBER))):
    return create_new_door(location_id, body)


@admin_location_api.get("/locations/{location_id}/door_access/doors/{door_id}")
def get_door_by_id(location_id: int, door_id: int, _=Depends(check_access(roles=_WITH_MEMBER))):
    return get_door(location_id, door_id)


@admin_location_api.get("/locations/{location_id}/door_access/doors")
def get_all_doors(location_id: int, _=Depends(check_access(roles=_WITH_MEMBER))):
    return get_doors(location_id)


@admin_location_api.put("/locations/{location_id}/door_access/doors/{door_id}")
def update_door(location_id: int, door_id: int, body: UpdateDoorRequest, _=Depends(check_access(roles=_WITH_MEMBER))):
    return update_door_info(location_id, door_id, body)


@admin_location_api.put("/locations/{location_id}/door_access/member_sync")
def door_access_member_sync(location_id: int, _=Depends(check_access(roles=_STD))):
    return door_access_member_sync_info(location_id)


@admin_location_api.put("/locations/{location_id}/door_access/settings")
def update_door_access_settings(
    location_id: int, body: UpdateDoorAccessSettingsRequest, _=Depends(check_access(roles=_WITH_MEMBER))
):
    return update_door_access_settings_info(location_id, body)


@admin_location_api.get("/locations/{location_id}/door_access/auth_status")
def get_door_access_auth_status_info(location_id: int, _=Depends(check_access(roles=_WITH_MEMBER))):
    return get_door_access_auth_status(location_id)
