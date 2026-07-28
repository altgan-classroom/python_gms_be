from fastapi import APIRouter, Depends

from plans_classes_service.classes.dtos.classes_requests import (
    CreateClassRequest,
    ClassPath,
    UpdateClassRequest,
    SessionFilter,
    BookClassRequest,
    MemberClassFilter,
    UpdateBookingRequest,
    DeleteClassQuery,
    BookingFilter,
    ClassFilter,
    CreateClassAccessGroupRequest,
    UpdateClassAccessGroupRequest,
)
from plans_classes_service.classes.services.classes_private_svc import (
    get_class_list,
    get_class_data,
    create_new_class,
    create_member_booking,
    update_class_info,
    return_class_status,
    get_booking,
    delete_member_booking,
    get_booking_info,
    update_booking,
    get_booking_info_for_location,
    delete_class_info,
    opengym_checkin,
    create_new_class_access_group,
    update_class_access_group,
    get_class_access_groups_info,
    get_class_access_group_info,
)

from gmsshared.src.web.fastapi_glue import check_access, g, to_utc

classes_private_api = APIRouter(prefix="/classes", tags=["Session API Information"])

_STD = ["OWNER", "STAFF", "MANAGER", "COACH"]
_WITH_MEMBER = ["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"]
_WITH_KIOSK = ["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH", "KIOSK"]


@classes_private_api.get("/locations/{location_id}/classes")
@to_utc(fields=["start_date", "end_date"])
def get_classes(
    location_id: int, query: SessionFilter = Depends(), _=Depends(check_access(roles=_WITH_KIOSK))
):
    return get_class_list(location_id, query)


@classes_private_api.get("/locations/{location_id}/classes/{class_id}")
@to_utc(fields=["class_time"])
def get_class(
    location_id: int, class_id: int, query: ClassFilter = Depends(), _=Depends(check_access(roles=_WITH_KIOSK))
):
    return get_class_data(location_id, class_id, query)


@classes_private_api.post("/locations/{location_id}/classes")
@to_utc(fields=["start_time", "end_time", "recurrence_end_date"])
def create_class(location_id: int, body: CreateClassRequest, _=Depends(check_access(roles=_STD))):
    return create_new_class(location_id, body)


@classes_private_api.post("/locations/{location_id}/classes/{class_id}/status")
@to_utc(fields=["start_time", "end_time", "recurrence_end_date"])
def get_class_status(
    location_id: int, class_id: int, body: UpdateClassRequest, _=Depends(check_access(roles=_STD))
):
    return return_class_status(ClassPath(location_id=location_id, class_id=class_id), body)


@classes_private_api.put("/locations/{location_id}/classes/{class_id}")
@to_utc(
    fields=[
        "start_time",
        "end_time",
        "class_cancellation_time",
        "class_time",
        "recurrence_end_date",
    ]
)
def update_class(
    location_id: int, class_id: int, body: UpdateClassRequest, _=Depends(check_access(roles=_STD))
):
    return update_class_info(location_id, body)


@classes_private_api.delete("/locations/{location_id}/classes/{class_id}")
@to_utc(fields=["class_time", "class_cancellation_time"])
def delete_class(
    location_id: int, class_id: int, query: DeleteClassQuery = Depends(), _=Depends(check_access(roles=_STD))
):
    return delete_class_info(location_id, class_id, query)


@classes_private_api.get("/locations/{location_id}/classes/{class_id}/bookings")
@to_utc(fields=["class_time"])
def get_bookings(
    location_id: int, class_id: int, query: MemberClassFilter = Depends(), _=Depends(check_access(roles=_WITH_MEMBER))
):
    return get_booking_info(location_id, class_id, query)


@classes_private_api.get("/locations/{location_id}/classes/bookings")
@to_utc(fields=["start_date", "end_date"])
def get_bookings_for_location(
    location_id: int, query: BookingFilter = Depends(), _=Depends(check_access(roles=_WITH_MEMBER))
):
    return get_booking_info_for_location(location_id, query)


@classes_private_api.post("/locations/{location_id}/bookings")
@to_utc(fields=["class_time"])
def create_booking_no_class(
    location_id: int, body: BookClassRequest, _=Depends(check_access(roles=_WITH_KIOSK))
):
    if body.opengym_checkin:
        return opengym_checkin(location_id, body)
    else:
        # Original Flask route had no class_id path param here (ClassPath.class_id was None).
        return create_member_booking(location_id, None, body, g.user.role.name.upper())


@classes_private_api.post("/locations/{location_id}/classes/{class_id}/bookings")
@to_utc(fields=["class_time"])
def create_booking(
    location_id: int, class_id: int, body: BookClassRequest, _=Depends(check_access(roles=_WITH_KIOSK))
):
    if body.opengym_checkin:
        return opengym_checkin(location_id, body)
    else:
        return create_member_booking(location_id, class_id, body, g.user.role.name.upper())


@classes_private_api.get("/locations/{location_id}/classes/{class_id}/bookings/{booking_id}")
def get_booking_by_id(
    location_id: int, class_id: int, booking_id: int, _=Depends(check_access(roles=_WITH_MEMBER))
):
    return get_booking(location_id, class_id, booking_id)


@classes_private_api.put("/locations/{location_id}/classes/{class_id}/bookings/{booking_id}")
@to_utc(fields=["member_checked_in_time", "member_cancelled_time"])
def update_booking_by_id(
    location_id: int,
    class_id: int,
    booking_id: int,
    body: UpdateBookingRequest,
    _=Depends(check_access(roles=_WITH_KIOSK)),
):
    return update_booking(location_id, class_id, booking_id, body)


@classes_private_api.delete("/locations/{location_id}/classes/{class_id}/bookings/{booking_id}")
@to_utc(fields=["member_checked_in_time", "member_cancelled_time"])
def delete_booking(
    location_id: int, class_id: int, booking_id: int, _=Depends(check_access(roles=_WITH_MEMBER))
):
    return delete_member_booking(location_id, class_id, booking_id, g.user.id)


@classes_private_api.post("/locations/{location_id}/class_access_groups")
def create_class_access_group(
    location_id: int, body: CreateClassAccessGroupRequest, _=Depends(check_access(roles=_STD))
):
    return create_new_class_access_group(location_id, body)


@classes_private_api.put("/locations/{location_id}/class_access_groups/{class_access_group_id}")
def update_class_access(
    location_id: int,
    class_access_group_id: int,
    body: UpdateClassAccessGroupRequest,
    _=Depends(check_access(roles=_STD)),
):
    return update_class_access_group(location_id, body)


@classes_private_api.get("/locations/{location_id}/class_access_groups")
def get_class_access_groups(location_id: int, _=Depends(check_access(roles=_STD))):
    return get_class_access_groups_info(location_id)


@classes_private_api.get("/locations/{location_id}/class_access_groups/{class_access_group_id}")
def get_class_access_group(
    location_id: int, class_access_group_id: int, _=Depends(check_access(roles=_STD))
):
    return get_class_access_group_info(location_id, class_access_group_id)
