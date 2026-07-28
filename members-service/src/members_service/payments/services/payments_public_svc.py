from http import HTTPStatus

from flask import Response

from gmsshared.src.models.member_payment_history_v2 import MemberPaymentHistory_v2
from members_service.payments.dtos.payments_requests import PayrixTxnUpdateRequest

from gmsshared.src.util.enums import (
    ResponseStatusEnum,
    PayrixTransactionStatusEnum,
    PayrixResourceEnum,
    PaymentTransactionTypeEnum,
)
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response

from gmsshared.src.models.member_payment_history import MemberPaymentHistory
from gmsshared.src.models.payrix_updates_log import PayrixUpdatesLog


def update_payrix_txns(body: PayrixTxnUpdateRequest) -> Response:

    payrix_transaction_id = body.response.alert.txnId
    payrix_transaction_status = PayrixTransactionStatusEnum[f"{body.response.alert.txnStatus.upper()}"].value
    payrix_return_description = ""
    if payrix_transaction_status == PayrixTransactionStatusEnum.RETURNED.value:
        payrix_return_description = body.response.alert.returnDescription

    payrix_updates_log = PayrixUpdatesLog()
    payrix_updates_log.payrix_resource = PayrixResourceEnum.TRANSACTION.value
    payrix_updates_log.payrix_request_payload = body.model_dump_json()
    payrix_updates_log.payrix_transaction_id = payrix_transaction_id
    payrix_updates_log.payrix_transaction_status = payrix_transaction_status
    payrix_updates_log.save_and_commit()

    payment = MemberPaymentHistory.find_by_payrix_txn_id(payrix_transaction_id=payrix_transaction_id)
    if not payment:
        payment = MemberPaymentHistory_v2.find_by_payrix_txn_id(payrix_transaction_id=payrix_transaction_id)

    if payment:
        if payment.for_payment_id and (payment.payment_transaction_type == PaymentTransactionTypeEnum.RETRY_SALE.value):
            original_payment = payment.original_payment
            original_payment.payrix_transaction_status = payrix_transaction_status
            if payrix_transaction_status == PayrixTransactionStatusEnum.RETURNED.value:
                payment.payrix_transaction_status = payrix_transaction_status
                original_payment.notes = payrix_return_description

            original_payment.save_and_commit()
        else:
            payment.payrix_transaction_status = payrix_transaction_status
            if payrix_transaction_status == PayrixTransactionStatusEnum.RETURNED.value:
                payment.notes = payrix_return_description
            payment.save_and_commit()
        return create_response(
            status_code=HTTPStatus.OK, status=ResponseStatusEnum.FOUND, logger_name=__name__, message="Updated status"
        )
    return create_response(
        status_code=HTTPStatus.NOT_FOUND, status=ResponseStatusEnum.NOT_FOUND, logger_name=__name__, message="Payment not found"
    )
