from fastapi import APIRouter, Depends

from members_service.members.dtos.members_requests import (
    InvoiceQuery,
    PayrixOnboardMemberRequest,
    CreateMemberRequest,
    UpdateInvoiceRequest, UpdateMemberProfileRequest,
    MemberFilter,
    CreateMembershipRequest,
    UpdateMembershipRequest,
    CreateMembershipSessionRequest,
    CreateMembershipQuery,
    CreateInvoice,
    UpdateMembershipFreezeRequest,
    RemoveMembershipSessionRequest
)
from members_service.members.services.members_private_svc import (
    add_invoice_info, add_member_to_payrix,
    get_member_activity_history,
    get_member_reconciliation_info,
    get_members_list,
    create_new_member,
    get_membership_info,
    get_profile,
    get_member_profile_info,
    update_invoice_info,
    update_member_profile_info,
    add_membership_info,
    get_membership_list,
    update_membership_info,
    get_registered_members,
    add_membership_sessions,
    get_membership_sessions_list,
    get_invoice_list,
    get_invoice_info,
    create_creditmemo,
    update_membership_freeze_info,
    remove_membership_sessions,
    get_membership_session_history
)
from gmsshared.src.web.fastapi_glue import check_access, to_utc

members_private_api = APIRouter(prefix="/members", tags=["v2 Members"])


@members_private_api.get("/locations/{location_id}/members")
def get_members(
    location_id: int,
    query: MemberFilter = Depends(),
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH", "KIOSK"])),
):
    if query.registered:
        return get_registered_members(location_id, query)
    else:
        return get_members_list(location_id, query)


@members_private_api.post("/locations/{location_id}/members")
def create_member(
    location_id: int,
    body: CreateMemberRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return create_new_member(location_id, body)


@members_private_api.get("/locations/{location_id}/members/{member_id}")
def get_single_profile(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_profile(location_id, member_id)


@members_private_api.get("/locations/{location_id}/members/{member_id}/profile")
def get_member_profile(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_member_profile_info(location_id, member_id)


@members_private_api.put("/locations/{location_id}/members/{member_id}/profile")
def update_member_profile(
    location_id: int,
    member_id: int,
    body: UpdateMemberProfileRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return update_member_profile_info(location_id, member_id, body)


@members_private_api.get("/locations/{location_id}/members/{member_id}/reconciliation")
def get_member_reconciliation(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_member_reconciliation_info(location_id, member_id)


@members_private_api.get("/locations/{location_id}/members/{member_id}/activity-history")
def get_member_activity(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_member_activity_history(location_id, member_id)


@members_private_api.get(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}/session-history"
)
def get_session_history(
    location_id: int,
    member_id: int,
    membership_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return get_membership_session_history(location_id, member_id, membership_id)


@members_private_api.post("/locations/{location_id}/members/{member_id}/memberships")
@to_utc(fields=["plan_start_date", "first_payment_date"])
def add_membership(
    location_id: int,
    member_id: int,
    body: CreateMembershipRequest,
    query: CreateMembershipQuery = Depends(),
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return add_membership_info(location_id, member_id, body, query)


@members_private_api.get(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}/sessions"
)
def get_membership_sessions(
    location_id: int,
    member_id: int,
    membership_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return get_membership_sessions_list(location_id, member_id, membership_id)


@members_private_api.put(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}"
)
@to_utc(fields=["freeze_from", "freeze_to", "unfreeze_date", "cancel_date"])
def update_membership(
    location_id: int,
    member_id: int,
    membership_id: int,
    body: UpdateMembershipRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return update_membership_info(location_id, member_id, membership_id, body)


@members_private_api.put(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}/freezes/{freeze_id}"
)
@to_utc(fields=["freeze_from", "freeze_to", "cancel_date"])
def update_membership_freeze(
    location_id: int,
    member_id: int,
    membership_id: int,
    freeze_id: int,
    body: UpdateMembershipFreezeRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return update_membership_freeze_info(location_id, body)


@members_private_api.post(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}/sessions"
)
def add_membership_session(
    location_id: int,
    member_id: int,
    membership_id: int,
    body: CreateMembershipSessionRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return add_membership_sessions(location_id, member_id, membership_id, body)


@members_private_api.delete(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}/sessions"
)
def remove_membership_session(
    location_id: int,
    member_id: int,
    membership_id: int,
    body: RemoveMembershipSessionRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "COACH"])),
):
    return remove_membership_sessions(location_id, member_id, membership_id, body)


@members_private_api.post("/locations/{location_id}/members/{member_id}/payrix_onboard")
def add_member_payrix(
    location_id: int,
    member_id: int,
    body: PayrixOnboardMemberRequest,
    _=Depends(check_access(roles=['OWNER', 'STAFF', 'MANAGER', 'COACH'])),
):
    return add_member_to_payrix(location_id, member_id, body)


@members_private_api.get("/locations/{location_id}/members/{member_id}/memberships")
def get_memberships(
    location_id: int,
    member_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_membership_list(location_id, member_id)


@members_private_api.get(
    "/locations/{location_id}/members/{member_id}/memberships/{membership_id}"
)
def get_membership(
    location_id: int,
    member_id: int,
    membership_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_membership_info(location_id, member_id, membership_id)


@members_private_api.get("/locations/{location_id}/members/{member_id}/invoices")
def get_invoices(
    location_id: int,
    member_id: int,
    query: InvoiceQuery = Depends(),
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_invoice_list(location_id, member_id, query)


@members_private_api.get(
    "/locations/{location_id}/members/{member_id}/invoices/{invoice_id}"
)
def get_invoice(
    location_id: int,
    member_id: int,
    invoice_id: int,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return get_invoice_info(location_id, member_id, invoice_id)


@members_private_api.put(
    "/locations/{location_id}/members/{member_id}/invoices/{invoice_id}"
)
def update_invoice(
    location_id: int,
    member_id: int,
    invoice_id: int,
    body: UpdateInvoiceRequest,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return update_invoice_info(location_id, member_id, invoice_id, body)


@members_private_api.post(
    "/locations/{location_id}/members/{member_id}/invoices/creditmemo"
)
def add_creditmemo(
    location_id: int,
    member_id: int,
    body: CreateInvoice,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return create_creditmemo(location_id, member_id, body)


@members_private_api.post("/locations/{location_id}/members/{member_id}/invoices")
def add_invoice(
    location_id: int,
    member_id: int,
    body: CreateInvoice,
    _=Depends(check_access(roles=["OWNER", "STAFF", "MANAGER", "MEMBER", "COACH"])),
):
    return add_invoice_info(location_id, member_id, body)
