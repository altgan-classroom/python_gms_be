import json
import ast
from http import HTTPStatus
from typing import List

import boto3
from botocore.exceptions import ClientError
from flask import Response

from auth_admin_service.admin.dtos.admin_requests import (
    CreateLocationRequest,
    GetGymLocationsRequest,
    UpdateLocationRequest,
    UpdateGymRequest,
    CreateRoomRequest,
    PayrixOnboardRequest,
    CreateUserRequest,
    UpdateUserRequest,
    CreateDoorRequest,
    UpdateDoorRequest,
    UpdateDoorAccessSettingsRequest
)
from auth_admin_service.admin.dtos.admin_responses import (
    DoorAccessAuthField,
    DoorAccessLocationAuthField,
    LocationResponse,
    ReportResponse,
    RoomResponse,
    LocationInfoResponse,
    DoorAccessDoorResponse,
    DoorAccessAuthResponse)
from auth_admin_service.admin.services.admin_user_svc import (
    create_user,
    activate_kiosk_user,
    update_user_info,
    delete_user_info,
)
from gmsshared.src.models._ref_gym_type import _RefGymType
from gmsshared.src.models.gym import Gym
from gmsshared.src.models.location import Location
from gmsshared.src.models.user import User
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.enums import DoorAccessOnboardStatusEnum, RoleEnum, LocationTypeEnum, GymTypeEnum, \
    ResponseStatusEnum
from gmsshared.src.util.validators import get_timezone, get_timezone_offset
from gmsshared.src.models.room import Room
from gmsshared import celery, db, get_config
from gmsshared.src.models.report import Report
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.models._ref_door_access_vendor_auth import _RefDoorAccessVendorAuth
from gmsshared.src.models.door_access_location_auth import DoorAccessLocationAuth
from gmsshared.src.util.enums import DoorAccessStatusEnum
from gmsshared.src.models.door_access_door import DoorAccessDoor
from gmsshared.src.util.misc import fill_model

# Don't delete these imports
from gmsshared.src.models.plan import Plan
from gmsshared.src.models.session import Class
from gmsshared.src.models.class_access_group import ClassAccessGroup


def get_location_list(query: GetGymLocationsRequest) -> Response:
    locations: List[Location] = Location.find_by_gym(query.gym_id)
    if not locations:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Locations not found",
        )
    locations_info = [
        {
            **LocationResponse.model_validate(location, from_attributes=True).model_dump(),
            "kiosk_username": location.kiosk_user.email if location.kiosk_user else None,
        }
        for location in locations
    ]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Locations found",
        data=locations_info,
    )


def create_location(user_id: int, body: CreateLocationRequest) -> Response:
    if not Gym.find_by_id(id=body.gym_id):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Gym not found",
        )
    location = Location(gym_id=body.gym_id, name=body.location_name)
    location.address_1 = body.address_1
    location.address_2 = body.address_2
    location.primary = body.primary
    location.location_type_id = LocationTypeEnum.PHYSICAL.value
    gym_types = [_RefGymType.find_by_id(GymTypeEnum.HEALTH_CLUB.value)]
    location.gym_types = gym_types
    location.other_gym_type = body.other_gym_type
    location.is_dea = 1
    location.save()
    _attach_user_to_location(user_id, location)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New location created",
    )


def create_location_without_user(body: CreateLocationRequest) -> Response:
    if not Gym.find_by_id(id=body.gym_id):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Gym not found",
        )
    location = Location(gym_id=body.gym_id, name=body.location_name)
    location.address_1 = body.address_1
    location.address_2 = body.address_2
    location.city = body.city
    location.state = body.state
    location.zip = body.zip
    location.country = body.country
    location.primary = body.primary
    location.area_sft = body.area_sft
    location.cs_phone = body.cs_phone
    location.cs_email = body.cs_email
    location.location_type_id = body.location_type_id
    location.other_gym_type = body.other_gym_type
    location.sales_tax = body.sales_tax
    gym_type_ids = body.model_dump()["gym_types"]
    gym_types = []
    if gym_type_ids is None:
        pass
    else:
        for gym_type_id in gym_type_ids:
            gym_types.append(_RefGymType.find_by_id(gym_type_id))
        location.gym_types = gym_types
    location.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New location created",
    )


def get_location_info(location_id: int) -> Response:
    location = Location.find_by_id(location_id)
    if not location:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location not found",
        )
    location_resp = LocationResponse.model_validate(location, from_attributes=True).model_dump()
    location_resp["kiosk_username"] = location.kiosk_user.email if location.kiosk_user else None

    door_access_auth = DoorAccessLocationAuth.find_by_location(location_id)
    auth_info = [DoorAccessLocationAuthField.model_validate(auth, from_attributes=True).model_dump() for auth in door_access_auth]
    location_resp["door_access_auth_fields"] = auth_info
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Location found",
        data=location_resp,
    )


def get_door_access_auth_status(location_id: int) -> Response:
    location = Location.find_by_id(location_id)
    door_access_auth = DoorAccessLocationAuth.find_by_location(location_id)
    auth_info = [DoorAccessLocationAuthField.model_validate(auth, from_attributes=True).model_dump() for auth in
                 door_access_auth]
    response_data = DoorAccessAuthResponse(
        door_access=location.door_access,
        door_access_auth_fields=auth_info,
        door_access_auth_status=location.door_access_auth_status,
        door_access_auth_error=location.door_access_auth_error,
        door_access_vendor_id=location.door_access_vendor_id,
        door_access_unlock_doors=location.door_access_unlock_doors
    )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Door access auth status found",
        data = response_data.model_dump()
    )


def update_location_payrix_onboard_info(self, location_id: int, body: PayrixOnboardRequest) -> Response:
    location = Location.find_by_id(location_id)
    location.payrix_merchant_id = body.payrix_merchant_id
    location.payrix_onboarding_status = body.payrix_onboarding_status
    location.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Location info updated",
        data=LocationResponse.model_validate(location, from_attributes=True).model_dump(),
    )


def update_location_info(location_id: int, body: UpdateLocationRequest) -> Response:
    location = Location.find_by_id(location_id)
    if not location:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location not found",
        )

    location.name = body.location_name if body.location_name is not None else location.name
    location.address_1 = body.address_1
    location.address_2 = body.address_2
    location.city = body.city
    location.state = body.state
    location.zip = body.zip
    location.country = body.country
    location.area_sft = body.area_sft
    location.cs_phone = body.cs_phone
    location.cs_email = body.cs_email
    location.location_type_id = (
        body.location_type_id if body.location_type_id is not None else location.location_type_id
    )
    location.other_gym_type = body.other_gym_type
    location.sales_tax = body.sales_tax
    location.timezone_type_id = body.timezone_type_id

    gym_type_ids = body.model_dump()["gym_types"]
    gym_types = []
    if gym_type_ids is None:
        pass
    else:
        for gym_type_id in gym_type_ids:
            gym_types.append(_RefGymType.find_by_id(gym_type_id))
        location.gym_types = gym_types
    location.is_dea = 1

    location.kiosk_enabled = body.kiosk_enabled
    if location.kiosk_enabled:
        location.checkin_type = body.checkin_type.value if body.checkin_type else location.checkin_type
        location.accent_color = body.accent_color
        if body.logo_url:
            location.logo_url = body.logo_url
        if location.kiosk_user_id is None:
            create_user_request = CreateUserRequest(
                location_id=location_id,
                first_name="Kiosk",
                last_name=location.name,
                email=f"{body.kiosk_username}",
                role_type_id=RoleEnum.KIOSK.value,
                password=body.kiosk_password,
            )
            response = create_user(location.id, create_user_request, skip_verification=True)
            if response.status_code == 200:
                location.kiosk_user_id = (User.find_by_email(create_user_request.email)).id
        else:
            activate_kiosk_user(location.kiosk_user_id)
            update_user_request = UpdateUserRequest(
                location_id=location_id,
                first_name="Kiosk",
                last_name=location.name,
                email=f"{location_id}_{location.name}_kiosk",
                role_type_id=RoleEnum.KIOSK.value,
                password=body.kiosk_password,
            )
            response = update_user_info(location.kiosk_user_id, update_user_request)
    else:
        if location.kiosk_user_id:
            delete_user_info(location_id, location.kiosk_user_id)

    _update_session_schedule_settings(location, body)

    location.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Location info updated",
        data=LocationResponse.model_validate(location, from_attributes=True).model_dump(),
    )


def update_door_access_settings_info(location_id: int, body:UpdateDoorAccessSettingsRequest) -> Response:
    location = Location.find_by_id(location_id)

    location.door_access = body.door_access

    if (body.door_access_vendor_id and body.door_access_auth_fields):
        _update_door_access(location, body)

    if body.door_access_unlock_doors is not None:
        location.door_access_unlock_doors = body.door_access_unlock_doors
    location.save_and_commit()

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Door access settings updated",
    )


def _update_door_access(location: Location, body: UpdateDoorAccessSettingsRequest):
    location.door_access_vendor_id = body.door_access_vendor_id
    DoorAccessLocationAuth.delete_by_location_id(location.id)

    location_vendor_auth_details = []
    for auth in body.door_access_auth_fields:
        auth_detail = DoorAccessLocationAuth()
        auth_detail.location_id = location.id
        auth_detail.field_id = auth.field_id
        auth_detail.field_value = auth.field_value
        location_vendor_auth_details.append(auth_detail)

    # Save the auth fields and kick off async process to validate them
    db.session.add_all(location_vendor_auth_details)
    db.session.commit()

    # Send async task to validate credentials
    location.door_access_auth_status = DoorAccessStatusEnum.PROCESSING.value
    celery.send_task("door_access_validate_credentials", (location.id, ))
    return


def _update_session_schedule_settings(location: Location, body: UpdateLocationRequest):
    session_settings = [
        "waitlist",
        "no_show_credit",
        "registration_start_time_value",
        "registration_start_time_type_id",
        "registration_end_time_type_id",
        "registration_end_time_value",
        "late_cancellation_time_type_id",
        "late_cancellation_time_value",
        "block_registrations_on_balance_due",
        "late_cancellation",
        "class_access_group"
    ]
    if location.no_show_credit == False and body.no_show_credit == True:
        location.no_show_enabled_datetime = utc_now()
    elif location.no_show_credit == True and body.no_show_credit == False:
        location.no_show_enabled_datetime = None

    for setting in session_settings:
        value = getattr(body, setting, None)
        if value is not None:
            setattr(location, setting, value.value if hasattr(value, "value") else value)

    if body.late_cancellation == False:
        location.late_cancellation_time_value = None
        location.late_cancellation_time_type_id = None


def delete_location_info(location_id: int) -> Response:
    location = Location.find_by_id(location_id)
    if not location:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location not found",
        )
    deleted = _delete_location(location)
    if not deleted:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message=f"Location - '{location.name}' is the only location for this Gym and cannot be deleted",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.DELETED,
        logger_name=__name__,
        message="Location deleted",
    )


def update_gym_info(gym_id: int, body: UpdateGymRequest) -> Response:
    gym = Gym.find_by_id(gym_id)
    if not gym:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Gym not found",
        )
    gym.name = body.name
    gym.logo_url = body.logo_url
    gym.save()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Gym info updated",
    )


def create_room(location_id: int, body: CreateRoomRequest) -> Response:
    if not Location.find_by_id(id=location_id):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location not found",
        )
    rooms = Room(location_id=location_id, name=body.name)
    rooms.sft = body.sft
    rooms.capacity = body.capacity
    rooms.notes = body.notes
    rooms.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New Room created",
    )


def get_rooms_list(location_id: int) -> Response:
    rooms: List[Room] = Room.find_by_location(location_id=location_id)
    if not rooms:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Rooms not found",
        )
    rooms_info = [RoomResponse.model_validate(room, from_attributes=True).model_dump() for room in rooms]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Rooms found",
        data=rooms_info,
    )


def get_room_info(room_id: int, location_id: int) -> Response:
    room_info = Room.find_by_location_and_room(room_id, location_id)
    if not room_info:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Room not found",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Room found",
        data=RoomResponse.model_validate(room_info, from_attributes=True).model_dump(),
    )


def update_room_info(room_id: int, location_id: int, body: CreateRoomRequest) -> Response:
    rooms = Room.find_by_location_and_room(room_id, location_id)
    if not rooms:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Room not found",
        )
    if not Location.find_by_id(id=body.location_id):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location not found",
        )
    rooms.location_id = body.location_id
    rooms.name = body.name
    rooms.sft = body.sft
    rooms.capacity = body.capacity
    rooms.notes = body.notes
    rooms.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Room info updated",
    )


def delete_room_info(room_id: int, location_id: int) -> Response:
    room = Room.find_by_location_and_room(room_id, location_id)
    if not room:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Room not found",
        )
    room.delete()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.DELETED,
        logger_name=__name__,
        message="Room deleted",
    )


def get_all_user_reports(location_id: int, user_id: int) -> Response:
    reports = [
        ReportResponse.model_validate(report, from_attributes=True).model_dump()
        for report in Report.find_by_user(environment=get_config().ENV, user_id=user_id)
    ]
    if not reports:
        return create_response(
            status_code=HTTPStatus.NOT_FOUND,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Reports not found",
        )

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Report found",
        data=reports,
    )


def get_report_embed_url_info(location_id: int, report_id: int) -> Response:
    report = Report.find_by_id(environment=get_config().ENV, id=report_id)
    if not report:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message=f"Report {report_id} not found",
        )

    # TODO: Make account, region and user config driven
    account_id = "843164030240"
    quicksight_user_name = get_config().QUICKSIGHT_USER_NAME
    try:
        error = ""
        if report.sheet_id and report.visual_id:
            report_url = _get_visual_embed_url(account_id, quicksight_user_name, report)
            dashboard_url = ""
        else:
            report_url = ""
            dashboard_url = _get_dashboard_embed_url(account_id, quicksight_user_name, report)
    except Exception as e:
        error, report_url, dashboard_url = str(e), "", ""

    if report_url or dashboard_url:
        data = {
            "name": report.name,
            "description": report.description,
            "report_url": report_url,
            "dashboard_url": dashboard_url,
            "location_id": location_id,
            "timezone_offset": get_timezone_offset(get_timezone()),
            "active": report.active,
        }
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Report URL found",
            data=data,
        )
    elif error:
        return create_response(
            status_code=HTTPStatus.OK, status=ResponseStatusEnum.ERROR, logger_name=__name__, message=error
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Could not find report",
        )


def _get_dashboard_embed_url(account_id, quicksight_user_name: str, report: Report) -> str:
    exp_config = {"Dashboard": {"InitialDashboardId": report.dashboard_id}}
    dashboard_url = _get_embed_url(account_id, quicksight_user_name, exp_config)
    return dashboard_url


def _get_visual_embed_url(account_id, quicksight_user_name: str, report: Report) -> str:
    exp_config = {
        "DashboardVisual": {
            "InitialDashboardVisualId": {
                "DashboardId": f"{report.dashboard_id}",
                "SheetId": f"{report.sheet_id}",
                "VisualId": f"{report.visual_id}",
            }
        }
    }
    visual_url = _get_embed_url(account_id, quicksight_user_name, exp_config)
    return visual_url


def _get_embed_url(account_id, quicksight_user_name: str, exp_config: dict) -> str:
    embed_url = ""
    response = get_embedding_url(
        account_id=account_id,
        experience_configuration=exp_config,
        user_arn=f"arn:aws:quicksight:us-east-1:{account_id}:user/default/{quicksight_user_name}",
    )
    if isinstance(response, dict) and response["statusCode"] == HTTPStatus.OK:
        _dict = ast.literal_eval(response["body"])
        if _dict["Status"] == HTTPStatus.OK:
            embed_url = _dict["EmbedUrl"]
    return embed_url


def get_embedding_url(account_id: str, experience_configuration: dict, user_arn: str):
    try:
        quicksight_client = boto3.client("quicksight", region_name="us-east-1")
        response = quicksight_client.generate_embed_url_for_registered_user(
            AwsAccountId=account_id,
            ExperienceConfiguration=experience_configuration,
            UserArn=user_arn,
            SessionLifetimeInMinutes=600,
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type"},
            "body": json.dumps(response),
            "isBase64Encoded": bool("false"),
        }
    except ClientError as e:
        return "Error generating embedding url: " + str(e)


def _attach_user_to_location(user_id: int, location: Location) -> None:
    user = User.find_by_id(user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    user.locations.append(location)

    if user.role_type_id != RoleEnum.OWNER.value:
        owner = User.find_owner_by_gym(location.gym_id)
        if owner:
            owner.locations.append(location)


def _delete_location(location: Location):
    locations = Location.find_by_gym(location.gym_id)
    location = Location.find_by_id(location.id)
    if len(locations) <= 1:
        return False
    for user in location.users:
        if not user.owner:
            user.delete()
    db.session.commit()
    return True


def location_contact_info(location_id: int) -> Response:
    location: Location = Location.find_by_id(location_id)
    if not location:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location info not found",
        )
    email = location.cs_email if location.cs_email else ""
    phone = location.cs_phone if location.cs_phone else ""
    if email == "" and phone == "":
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message="Location doesn't have contact information",
        )
    info = LocationInfoResponse(email=email, phone=phone, door_access_place_id=location.door_access_place_id).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Location info found",
        data=info,
    )


def get_vendor_auth_data(vendor_id: int) -> Response:
    auth_fields: List[_RefDoorAccessVendorAuth] = _RefDoorAccessVendorAuth.find_by_vendor_id(vendor_id)
    if not auth_fields:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No auth fields found for this door access vendor",
        )

    auth_info = [DoorAccessAuthField.model_validate(auth, from_attributes=True).model_dump() for auth in auth_fields]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Door access vendor auth info found",
        data=auth_info,
    )

def create_new_door(location_id: int, body: CreateDoorRequest) -> Response:
    old_door = DoorAccessDoor.find_door_by_location_and_name(location_id, body.name)
    if old_door:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Door already exists. Please modify your entry to ensure uniqueness",
        )
    door = DoorAccessDoor(location_id, body.name, body.door_location)
    door.door_access_door_status = DoorAccessStatusEnum.PROCESSING.value
    door.save_and_commit()
    door_info = DoorAccessDoorResponse.model_validate(door, from_attributes=True).model_dump()

    if door.location.door_access:
        celery.send_task("update_door", (location_id, door.location.door_access_vendor_id, door.id, None))

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="New door created",
        data=door_info,
    )


def get_doors(location_id: int) -> Response:
    doors = DoorAccessDoor.find_by_location_id(location_id)
    if not doors:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="No doors found",
        )
    doors_info = [DoorAccessDoorResponse.model_validate(door, from_attributes=True).model_dump() for door in doors]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Doors found",
        data=doors_info,
    )

def get_door(location_id: int, door_id: int) -> Response:
    door = DoorAccessDoor.find_by_id(location_id, door_id)
    if not door:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="No door found",
        )
    door_info = DoorAccessDoorResponse.model_validate(door, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Door found",
            data=door_info,
        )

def update_door_info(location_id: int, door_id: int, body: UpdateDoorRequest) -> Response:
    door = DoorAccessDoor.find_by_id(location_id, door_id)
    if not door:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="No door found",
        )

    old_door_status = door.active
    fill_model(body, door, exclude=["location_id"], ignore_nulls=False)
    door.save_and_commit()

    # Passing in old_door status to skip activation/deactivation of door in tasks
    if door.location.door_access:
        celery.send_task("update_door", (location_id, door.location.door_access_vendor_id, door.id, old_door_status))

    door_info = DoorAccessDoorResponse.model_validate(door, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Door info updated",
        data=door_info,
    )


def door_access_member_sync_info(location_id: int) -> Response:
    location = Location.find_by_id(location_id)
    if not location:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Location not found",
        )

    if location.door_access:
        celery.send_task("member_sync", (location_id,))

    return create_response(
        status_code=HTTPStatus.ACCEPTED,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Door access member sync started",
    )
