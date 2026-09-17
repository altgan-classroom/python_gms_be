from http import HTTPStatus

from gmsshared import celery
from flask import Response

from plans_classes_service.plans.dtos.plans_requests import (
    CreatePlanRequest,
    UpdatePlanRequest,
)
from plans_classes_service.plans.dtos.plans_responses import Plan as PlanPydantic

from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.enums import ResponseStatusEnum, PlanStatusType
from gmsshared.src.models.plan import Plan
from gmsshared.src.models._ref_plan_type import _RefPlanType
from gmsshared.src.models.location import Location
from gmsshared.src.models.class_access_group import ClassAccessGroup


def get_plans_list(location_id: int) -> Response:
    plans_list = Plan.find_by_location(location_id)
    if not plans_list:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No plans found",
        )

    plans_list = [
        {
            **plan,
            "class_access_group": (
                [int(x.strip()) for x in plan.get("class_access_group", "").split(",") if x.strip()]
                if plan.get("class_access_group")
                else []
            )
        }
        for plan in plans_list
    ]
    plans = [dict(r) for r in plans_list]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message=f"Plans found:{len(plans)}",
        data=plans,
    )


def get_plan_data(location_id: int, plan_id: int) -> Response:
    plan_data, member_count = Plan.find_by_location_and_plan_with_member_count(location_id, plan_id)
    if not plan_data:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No plan found",
        )
    plan_types = [p.id for p in plan_data.plan_types]
    class_access_groups = [group.id for group in plan_data.class_access_groups]
    plan = PlanPydantic.model_validate(plan_data, from_attributes=True).model_dump()
    plan["plan_types"] = plan_types
    plan["member_count"] = member_count
    plan["class_access_groups"] = class_access_groups
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Plan found",
        data=plan,
    )


def create_new_plan(location_id: int, body: CreatePlanRequest) -> Response:
    new_plan = Plan()
    if _is_plan_name_exist(location_id, body):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Plan Name already exists. Please modify your entry to ensure uniqueness",
        )

    _fill_plan(new_plan, body)
    plan_types = [p.id for p in new_plan.plan_types]
    plan = PlanPydantic.model_validate(new_plan, from_attributes=True).model_dump()
    plan["plan_types"] = plan_types

    if new_plan.location.door_access and body.class_access_groups:
        plan_class_access_groups = [cg.id for cg in new_plan.class_access_groups]
        celery.send_task("update_members_to_group", (location_id, plan_class_access_groups, None))

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Successfully created plan",
        data=plan,
    )


def _is_plan_name_exist(location_id: int, body: CreatePlanRequest, plan_id=None):
    if plan := Plan.find_non_cancelled_plans_by_location_and_plan_name(location_id,body.name):
        if plan_id and plan.id == plan_id:
            return False

        return True
    return False


def _fill_plan(plan: Plan, body: CreatePlanRequest):
    for attr in body.dict().items():
        if attr[0] == "plan_types" or attr[0] == "location_permissions" or attr[0] == "class_access_groups":
            pass
        else:
            plan.__setattr__(attr[0], attr[1])

    plan_type_ids = body.dict()["plan_types"]
    if plan_type_ids:
        plan_types = []
        for plan_type_id in plan_type_ids:
            plan_types.append(_RefPlanType.find_by_id(plan_type_id))
        plan.plan_types = plan_types

    class_access_group_ids = body.dict().get("class_access_groups", [])
    class_access_groups = []
    for group_id in class_access_group_ids:
        group = ClassAccessGroup.find_by_id(body.location_id, group_id)
        if group is not None:
            class_access_groups.append(group)
    plan.class_access_groups = class_access_groups

    plan_location_ids = body.dict()["location_permissions"]
    if plan_location_ids:
        plan_locations = []
        for plan_location_id in plan_location_ids:
            plan_locations.append(Location.find_by_id(plan_location_id))
        plan.plan_locations = plan_locations

    plan.save_and_commit()


def update_plan_info(location_id: int, plan_id: int, body: UpdatePlanRequest) -> Response:
    plan = Plan.find_by_location_and_plan(location_id=location_id, plan_id=plan_id)
    if not plan:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Plan not found",
        )

    if _is_plan_name_exist(location_id, body, plan_id):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Plan Name already exists. Please modify your entry to ensure uniqueness",
        )

    # Capture this before copying over body to plan
    plan_class_access_groups = [cg.id for cg in plan.class_access_groups]
    _fill_plan(plan, body)

    if plan.location.door_access:
        remove = list(set(plan_class_access_groups) - set(body.class_access_groups))
        add = list(set(body.class_access_groups) - set(plan_class_access_groups))
        celery.send_task("update_members_to_group", (location_id, add, remove,))

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Successfully updated plan",
    )


def delete_plan(location_id: int, plan_id: int) -> Response:
    class PlanMembers:
        active_member_count: int
        frozen_member_count: int

        def __init__(self, frozen_member_count: int, active_member_count: int):
            self.frozen_member_count = frozen_member_count
            self.active_member_count = active_member_count

    plan = Plan.find_by_location_and_plan(location_id, plan_id)
    if not plan:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Not plan found to be deleted",
        )

    plan_info = Plan.get_active_and_frozen_memberships(location_id, plan_id)
    members = PlanMembers(**plan_info)

    if members.active_member_count > 0 or members.frozen_member_count > 0:
        message = "Plan cannot be deleted, active or frozen memberships linked to it"
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_REQUEST,
            logger_name=__name__,
            message=message,
            data=vars(members),
        )

    plan.plan_status_type_id = PlanStatusType.CANCELLED.value
    plan.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.DELETED,
        logger_name=__name__,
        message=f"Plan {plan_id} has been deleted",
    )
