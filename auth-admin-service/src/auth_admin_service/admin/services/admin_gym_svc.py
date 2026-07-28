from http import HTTPStatus
from flask import Response
from pydantic import BaseModel

from auth_admin_service.admin.dtos.admin_requests import (
    UpdateGymRequest,
    UpdateGymMainSettingsRequest,
    UpdateGymClassSettingsRequest,
)
from auth_admin_service.admin.dtos.admin_responses import GymMainSettingsResponse, GymClassSettingsResponse

from gmsshared.src.models.gym import Gym
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.enums import ResponseStatusEnum


def update_gym_info(gym_id: int, body: UpdateGymRequest) -> Response:
    gym: Gym = Gym.find_by_id(gym_id)
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
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Gym info updated",
    )


def get_gym_main_settings_info(gym_id: int) -> Response:
    gym: Gym = Gym.find_by_id(gym_id)
    if not gym:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Gym Main Settings not found",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Gym Main Settings found",
        data=GymMainSettingsResponse.model_validate(gym, from_attributes=True).model_dump(),
    )


def update_gym_main_settings_info(gym_id: int, body: UpdateGymMainSettingsRequest) -> Response:
    gym = Gym.find_by_id(gym_id)
    if not gym:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND.value,
            logger_name=__name__,
            message="Gym Main Settings not found",
        )
    _fill_gym(gym, body)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Gym Main Settings info updated",
        data=GymMainSettingsResponse.model_validate(gym, from_attributes=True).model_dump(),
    )


def get_gym_class_settings_info(gym_id: int) -> Response:
    gym = Gym.find_by_id(gym_id)
    if not gym:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND.value,
            logger_name=__name__,
            message="Gym Class Settings not found",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Gym Class Settings found",
        data=GymClassSettingsResponse.model_validate(gym, from_attributes=True).model_dump(),
    )


def update_gym_class_settings_info(gym_id: int, body: UpdateGymClassSettingsRequest) -> Response:
    gym = Gym.find_by_id(gym_id)
    if not gym:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND.value,
            logger_name=__name__,
            message="Gym Class Settings not found",
        )
    _fill_gym(gym, body)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Gym Class Settings info updated",
        data=GymClassSettingsResponse.model_validate(gym, from_attributes=True).model_dump(),
    )


def _fill_gym(gym: Gym, body: BaseModel):
    for attr in body.model_dump().items():
        gym.__setattr__(attr[0], attr[1])
    gym.save_and_commit()
