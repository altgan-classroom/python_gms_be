from fastapi import APIRouter, Depends

from members_service.payments.dtos.payments_requests import (
    CreatePaymentMethodRequest,
    UpdatePaymentMethodRequest,
    CreatePaymentRequest,
    CreateRefundRequest,
    CreateRetryRequest,
    UpdatePaymentQuery,
    UpdatePaymentRequest
)
from gmsshared.src.web.fastapi_glue import check_access, to_utc
from members_service.payments.services.payments_private_svc import (
    get_payment_method_list,
    create_payment_method_info_card,
    create_payment_method_info_ach,
    get_payment_method_info,
    update_payment_info,
    update_payment_method_info,
    get_payments_list,
    retry_payment_info,
    get_payment_info,
    delete_payment_method_info,
    create_payment_info,
    create_refund_info,
    onboard_member_to_payrix_info,
)

payments_private_api = APIRouter(prefix="/members", tags=["v2 Payments"])


@payments_private_api.post("/locations/{location_id}/members/{member_id}/payrix")
def onboard_member_to_payrix(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return onboard_member_to_payrix_info(location_id, member_id)


@payments_private_api.get("/locations/{location_id}/members/{member_id}/payment-methods")
def get_payment_methods(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return get_payment_method_list(location_id, member_id)


@payments_private_api.post(
    "/locations/{location_id}/members/{member_id}/payment-methods/card"
)
def create_payment_method_card(
    location_id: int,
    member_id: int,
    body: CreatePaymentMethodRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return create_payment_method_info_card(location_id, member_id, body)


@payments_private_api.post(
    "/locations/{location_id}/members/{member_id}/payment-methods/ach"
)
def create_payment_method_ach(
    location_id: int,
    member_id: int,
    body: CreatePaymentMethodRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return create_payment_method_info_ach(location_id, member_id, body)


@payments_private_api.get(
    "/locations/{location_id}/members/{member_id}/payment-methods/{pm_id}"
)
def get_payment_method(
    location_id: int,
    member_id: int,
    pm_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return get_payment_method_info(location_id, member_id, pm_id)


@payments_private_api.put(
    "/locations/{location_id}/members/{member_id}/payment-methods/{pm_id}"
)
def update_payment_method(
    location_id: int,
    member_id: int,
    pm_id: int,
    body: UpdatePaymentMethodRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return update_payment_method_info(location_id, member_id, pm_id, body)


@payments_private_api.delete(
    "/locations/{location_id}/members/{member_id}/payment-methods/{pm_id}"
)
def delete_payment_method(
    location_id: int,
    member_id: int,
    pm_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "MEMBER"])),
):
    return delete_payment_method_info(location_id, member_id, pm_id)


@payments_private_api.get("/locations/{location_id}/members/{member_id}/payments")
def get_payments(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return get_payments_list(location_id, member_id)


@payments_private_api.post("/locations/{location_id}/members/{member_id}/payments")
@to_utc(fields=["scheduled_date"])
def create_payment(
    location_id: int,
    member_id: int,
    body: CreatePaymentRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return create_payment_info(location_id, member_id, body)


@payments_private_api.post(
    "/locations/{location_id}/members/{member_id}/payments/{payment_id}/refunds"
)
def create_refund(
    location_id: int,
    member_id: int,
    payment_id: int,
    body: CreateRefundRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return create_refund_info(location_id, member_id, payment_id, body)


@payments_private_api.post(
    "/locations/{location_id}/members/{member_id}/payments/{payment_id}/retries"
)
def retry_payment(
    location_id: int,
    member_id: int,
    payment_id: int,
    body: CreateRetryRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return retry_payment_info(location_id, member_id, payment_id, body)


@payments_private_api.get(
    "/locations/{location_id}/members/{member_id}/payments/{payment_id}"
)
def get_payment(
    location_id: int,
    member_id: int,
    payment_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return get_payment_info(location_id, member_id, payment_id)


@payments_private_api.put(
    "/locations/{location_id}/members/{member_id}/payments/{payment_id}"
)
def update_payment(
    location_id: int,
    member_id: int,
    payment_id: int,
    body: UpdatePaymentRequest,
    query: UpdatePaymentQuery = Depends(),
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return update_payment_info(location_id, member_id, payment_id, query, body)
