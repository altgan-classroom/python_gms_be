from fastapi import APIRouter

from members_service.payments.dtos.payments_requests import PayrixTxnUpdateRequest
from members_service.payments.services.payments_public_svc import update_payrix_txns

payments_public_api = APIRouter(prefix="/members", tags=["v2 Public"])


@payments_public_api.post("/payrix_txn_updates")
def update_txn_from_payrix(body: PayrixTxnUpdateRequest):
    return update_payrix_txns(body)
