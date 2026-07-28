from fastapi import APIRouter, Depends

from plans_classes_service.plans.dtos.plans_requests import (
    CreatePlanRequest,
    UpdatePlanRequest,
)
from plans_classes_service.plans.services.plans_private_svc import (
    get_plans_list,
    get_plan_data,
    create_new_plan,
    update_plan_info,
    delete_plan,
)

from gmsshared.src.web.fastapi_glue import check_access

_ROLES = ["OWNER", "STAFF", "MANAGER", "COACH"]

plans_private_api = APIRouter(prefix="/plans", tags=["Plan Info"])


@plans_private_api.get("/locations/{location_id}/plans")
def get_plans(location_id: int, _=Depends(check_access(roles=_ROLES))):
    return get_plans_list(location_id)


@plans_private_api.get("/locations/{location_id}/plans/{plan_id}")
def get_plan(location_id: int, plan_id: int, _=Depends(check_access(roles=_ROLES))):
    return get_plan_data(location_id, plan_id)


@plans_private_api.post("/locations/{location_id}/plans")
def create_plan(location_id: int, body: CreatePlanRequest, _=Depends(check_access(roles=_ROLES))):
    return create_new_plan(location_id, body)


@plans_private_api.put("/locations/{location_id}/plans/{plan_id}")
def update_plan(location_id: int, plan_id: int, body: UpdatePlanRequest, _=Depends(check_access(roles=_ROLES))):
    return update_plan_info(location_id, plan_id, body)


@plans_private_api.delete("/locations/{location_id}/plans/{plan_id}")
def del_plan(location_id: int, plan_id: int, _=Depends(check_access(roles=_ROLES))):
    return delete_plan(location_id, plan_id)
