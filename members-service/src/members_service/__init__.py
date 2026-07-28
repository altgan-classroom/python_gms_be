from fastapi import APIRouter

from members_service.members.endpoints.members_private_api import members_private_api
from members_service.payments.endpoints.payments_public_api import payments_public_api
from members_service.payments.endpoints.payments_private_api import payments_private_api

members_api = APIRouter(prefix="/api/v2")

members_api.include_router(members_private_api)
members_api.include_router(payments_public_api)
members_api.include_router(payments_private_api)
