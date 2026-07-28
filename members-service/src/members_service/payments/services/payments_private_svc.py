from datetime import datetime
from http import HTTPStatus
from io import BytesIO
from typing import List, Any

from xhtml2pdf import pisa

from flask import Response

from gmsshared.src.web.fastapi_glue import g

from gmsshared import celery, db
from gmsshared.src.models.invoice import Invoice
from members_service.payments.dtos.payments_requests import (
    CreatePaymentMethodRequest,
    CreateRetryRequest,
    PayrixOnboardRequest,
    CreatePaymentRequest,
    CreateRefundRequest,
    UpdatePaymentMethodRequest,
    UpdatePaymentQuery,
    UpdatePaymentRequest,
)
from members_service.payments.dtos.payments_responses import (
    PaymentMethodResponse,
    PaymentResponse,
    PaymentStatusResponse,
    PaymentHistResponse,
    PaymentRefundResponse,
)

from gmsshared.src.models.invoice_item import InvoiceItem
from gmsshared.src.models.member_payment_history import MemberPaymentHistory
from gmsshared.src.models.member_payment_method import MemberPaymentMethod
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.util.dea import (
    create_credit_memo_invoice, create_credit_memo_ledger_entries, create_payment_ledger_entries,
    update_outstanding_balance_and_invoice_status
)
from gmsshared.src.util.enums import (
    InvoiceItemStatusTypeEnum, PaymentCategoryEnum,
    ResponseStatusEnum,
    PayrixOnboardStatusEnum,
    PayrixTransactionStatusEnum,
    PaymentTransactionTypeEnum,
    PayrixPaymentMethodEnum
)
from gmsshared.src.util.misc import fill_model
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.models.location import Location
from gmsshared.src.models.member_payment_history_v2 import MemberPaymentHistory_v2
from gmsshared.src.models.plan import Plan


def update_member_payrix_onboard_info(location_id: int, user_id: int, body: PayrixOnboardRequest) -> Response:
    member_profile = MemberProfile.find_by_id(location_id, user_id)
    member_profile.payrix_customer_id = body.payrix_customer_id
    member_profile.payrix_onboarding_status = body.payrix_onboarding_status
    member_profile.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK, status=ResponseStatusEnum.UPDATED, logger_name=__name__, message="Member Updated"
    )


def onboard_member_to_payrix_info(location_id: int, member_id: int) -> Response:
    member = MemberProfile.find_by_id(location_id, member_id)
    if not member:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.MEMBER_DOES_NOT_EXIST,
            logger_name=__name__,
            message="Member does not exist",
        )
    if member.payrix_customer_id:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Member already onboarded on Payrix",
        )

    location = Location.find_by_id(location_id)
    if location.payrix_onboarding_status == PayrixOnboardStatusEnum.BOARDED.value:
        member.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
        member.save_and_commit()
        celery.send_task("onboard_member_in_payrix", (member.location_id, member.user_id))
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Merchant for location: {member.location_id} is not onboarded on Payrix",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Member queued for onboarding on Payrix",
    )


def create_payment_method_info_card(location_id: int, user_id: int, body: CreatePaymentMethodRequest) -> Response:

    payment_method = MemberPaymentMethod(location_id=location_id, member_id=user_id)
    body.method = 2  # TODO: Could be 1, 2, 3, 4, 5. Need to find a way to get this properly. But for now 2 seems to work for all types
    if body.zipcode and not body.token:
        payment_method.zipcode = body.zipcode
        payment_method.payrix_zipcode_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
        payment_method.save_and_commit()

        celery.send_task("update_zipcode", (location_id, user_id, payment_method.id))

    fill_model(body, payment_method, exclude=["default"], ignore_nulls=False)
    payment_method.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New payment method created",
        data=PaymentMethodResponse.model_validate(payment_method, from_attributes=True).model_dump(),
    )


def create_payment_method_info_ach(location_id: int, user_id: int, body: CreatePaymentMethodRequest) -> Response:
    payment_method = MemberPaymentMethod(location_id=location_id, member_id=user_id)
    if (not body.account_ach) or (not body.routing_ach):
        return create_response(
            status_code=HTTPStatus.BAD_REQUEST,
            status=ResponseStatusEnum.ERROR,
            logger_name=__name__,
            message="Missing ACH account or routing info",
        )

    fill_model(body, payment_method, exclude=["default_method", "default"], ignore_nulls=False)
    payment_method.save_and_commit()
    member_profile = MemberProfile.find_by_id(location_id, user_id)
    if member_profile.payrix_onboarding_status == PayrixOnboardStatusEnum.BOARDED.value:
        payment_method.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
        payment_method.save_and_commit()
        celery.send_task(
            "tokenize_ach_for_customer",
            (location_id, user_id, payment_method.id, body.account_ach, body.routing_ach, body.default),
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New payment method created",
        data=PaymentMethodResponse.model_validate(payment_method, from_attributes=True).model_dump(),
    )


def get_payment_method_list(location_id: int, user_id: int) -> Response:
    payment_methods: List[MemberPaymentMethod] = MemberPaymentMethod.find_by_member_id(
        location_id=location_id, member_id=user_id
    )

    if not payment_methods:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment methods not found",
        )
    payment_methods_list = [
        PaymentMethodResponse.model_validate(pm, from_attributes=True).model_dump() for pm in payment_methods
    ]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Payment methods found",
        data=payment_methods_list,
    )


def get_payment_method_info(location_id: int, user_id: int, pm_id: int) -> Response:
    payment_method = MemberPaymentMethod.find_by_id(location_id=location_id, user_id=user_id, pm_id=pm_id)
    if not payment_method:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment method not found",
        )
    payment_method_info = PaymentMethodResponse.model_validate(payment_method, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Payment method found",
        data=payment_method_info,
    )


def update_payment_method_info(
    location_id: int, user_id: int, pm_id: int, body: UpdatePaymentMethodRequest
) -> Response:
    payment_method = MemberPaymentMethod.find_by_id(location_id=location_id, user_id=user_id, pm_id=pm_id)
    if not payment_method:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment method not found",
        )
    if body.default or body.token:  # If CC is being created, make it default
        payment_method.save_as_default()
    fill_model(body, payment_method, exclude=[], ignore_nulls=True)

    if body.token and body.payrix_token_id:
        payment_method.payrix_onboarding_status = PayrixOnboardStatusEnum.BOARDED.value
    payment_method.save_and_commit()
    payment_method_info = PaymentMethodResponse.model_validate(payment_method, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Payment method updated",
        data=payment_method_info,
    )


def delete_payment_method_info(location_id: int, user_id: int, pm_id: int) -> Response:
    pm = MemberPaymentMethod.find_by_id(location_id=location_id, user_id=user_id, pm_id=pm_id)
    if not pm:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment method not found",
        )
    if pm.payrix_token_id:
        celery.send_task("delete_token", (pm.location_id, pm.user_id, pm.id))
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.DELETED,
        logger_name=__name__,
        message="Payment method deleted",
    )

def create_payment_info(location_id: int, user_id: int, body: CreatePaymentRequest, from_invoice = False) -> Response:
    location = Location.find_by_id(location_id)
    if not location.payments:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Payments are disabled for this location",
        )

    if body.payment_method_id != 0:
        payment_method = MemberPaymentMethod.find_by_id(body.location_id, body.member_id, body.payment_method_id)
        if payment_method is None:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.NOT_FOUND,
                logger_name=__name__,
                message="Payment method not found",
            )
        payment = MemberPaymentHistory_v2(location_id, user_id, payment_method.id)
    else:
        payment = MemberPaymentHistory_v2(location_id, user_id, 0)

    fill_model(body, payment, exclude=["payment_method_id"], ignore_nulls=True)
    if body.invoice_id:
        inv = Invoice.find_by_id(location_id, user_id, body.invoice_id)
        payment.invoice_id = inv.id
        payment.invoice_item_ids = [item.id for item in inv.invoice_items]

    payment.save_and_commit()
    _calc_total_payment(payment, body, from_invoice = from_invoice)

    if body.payment_method_id != 0 and payment.scheduled_date <= utc_now().date():
        payment.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
        payment.save_and_commit()
        if from_invoice:
            celery.send_task("process_payment_v2", (payment.location_id, payment.user_id, payment.id, True))
        else:
            celery.send_task("process_payment_v2", (payment.location_id, payment.user_id, payment.id, False))

    data = PaymentResponse.model_validate(payment).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Payment created",
        data=data,
        )

def update_payment_info(location_id: int, user_id: int, payment_id: int, query: UpdatePaymentQuery, body: UpdatePaymentRequest) -> Response:
    payment = MemberPaymentHistory_v2.find_by_id(body.location_id, body.member_id, body.payment_id)
    if payment is None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment not found",
        )

    fill_model(body, payment, exclude=[], ignore_nulls=True)
    if query and query.update_type == 1:
        return _forgive_payment(payment)
    elif query and query.update_type == 2:
        return _reinforce_payment(payment)
    elif query and query.update_type == 3:
        return _cancel_payment(payment)
    elif query and query.update_type == 4:
        return _restore_payment(payment)
    else:
        _calc_total_payment(payment, body)
        payment.save_and_commit()
    payment_status_data=PaymentStatusResponse.model_validate(payment, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Payment updated",
        data=payment_status_data,
    )

def create_refund_info(location_id: int, user_id: int, payment_id: int, body: CreateRefundRequest) -> Response:
    location = Location.find_by_id(location_id)
    if not location.payments:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Payments are disabled for this location",
        )

    payment = MemberPaymentHistory_v2.find_by_id(body.location_id, body.member_id, body.payment_id)
    if payment is None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment not found",
        )

    if payment.payrix_transaction_status not in (
        PayrixTransactionStatusEnum.APPROVED.value,
        PayrixTransactionStatusEnum.CAPTURED.value,
        PayrixTransactionStatusEnum.SETTLED.value,
    ):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Payment not eligible for refund",
        )

    refunded_amount = 0
    for refunded_payment in payment.refunds_retries:
        if (
            refunded_payment.payment_transaction_type_id == PaymentTransactionTypeEnum.REFUND.value
            and refunded_payment.payrix_transaction_status
            in (
                PayrixTransactionStatusEnum.PENDING.value,
                PayrixTransactionStatusEnum.APPROVED.value,
                PayrixTransactionStatusEnum.CAPTURED.value,
                PayrixTransactionStatusEnum.SETTLED.value,
            )
        ):
            refunded_amount = refunded_amount + refunded_payment.total_amount

    if payment.total_amount < refunded_amount + body.total_amount:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Refunds exceed the original transaction amount",
        )

    refund = MemberPaymentHistory_v2(location_id, user_id, payment.payment_method_id)
    fill_model(body, refund, exclude=[], ignore_nulls=True)
    refund.for_payment_id = payment.id
    refund.payment_transaction_type_id = PaymentTransactionTypeEnum.REFUND.value
    refund.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
    refund.save_and_commit()

    celery.send_task("refund_payment_v2", (refund.location_id, refund.user_id, refund.id))
    data = PaymentResponse.model_validate(refund).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Refund created",
        data=data,
    )


def get_payments_list(location_id: int, user_id: int, invoice_payments = None) -> Response|list:
    if not invoice_payments:
        payments = MemberPaymentHistory_v2.find_history_by_member_id(location_id=location_id, user_id=user_id)
    else:
        payments = invoice_payments

    data = []
    for payment in payments:
        resp = _fill_payment_hist_response(payment)
        refunds_resp, retries_resp = _get_refunds_and_retries(payment)
        resp["refunds"] = [r.model_dump() for r in refunds_resp]
        resp["retries"] = [r.model_dump() for r in retries_resp]
        data.append(resp)

    if invoice_payments:
        return data

    if data is None or len(data) == 0:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payments not found",
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Payments found",
            data=data,
        )


def _fill_payment_hist_response(payment: MemberPaymentHistory_v2):
    pm = None
    pm_type = None
    if payment.payment_method and (payment.payment_method.last_4_digits_card is None or payment.payment_method.last_4_digits_card == ""):
        pm = payment.payment_method.last_4_digits_account
        pm_type = "ACH"
    elif payment.payment_method and (payment.payment_method.last_4_digits_card is not None or payment.payment_method.last_4_digits_card != ""):
        pm = payment.payment_method.last_4_digits_card
        pm_type = "Card"
    elif payment.payment_method_id == 0:
        pm = "Cash"
        pm_type = "Cash"

    if payment.processed_by is None or payment.processed_by == "":
        processed_by = ""
    elif payment.processed_by == 0:
        processed_by = "Automatic"
    else:
        processed_by = "User"

    resp = PaymentHistResponse.model_validate(payment)
    resp.payment_method_last_4_digits = pm
    resp.description = _payment_description(payment)
    resp.payment_type = pm_type
    resp.source = processed_by
    resp.payment_status = _payment_status(payment.payrix_transaction_status)
    resp.total_amount = round(payment.total_amount, 2)
    return resp.model_dump()

def _payment_description(payment: MemberPaymentHistory_v2):

    if payment.payrix_transaction_status == PayrixTransactionStatusEnum.RETURNED.value:
        return payment.notes
    elif hasattr(payment, "invoice") and payment.invoice:
        if payment.invoice_item_ids and set(payment.invoice_item_ids).issubset(set([item.id for item in payment.invoice.invoice_items])):
            if len(payment.invoice_item_ids) > 1:
                return list(filter(lambda item: item.id == payment.invoice_item_ids[1], payment.invoice.invoice_items))[0].description
            else:
                return list(filter(lambda item: item.id == payment.invoice_item_ids[0], payment.invoice.invoice_items))[0].description
        return ""
    else:
        return payment.notes


def _payment_status(status: int):

    if status == PayrixTransactionStatusEnum.APPROVED.value:
        return "Approved"
    elif status == PayrixTransactionStatusEnum.PENDING.value:
        return "Processing"
    elif status == PayrixTransactionStatusEnum.CAPTURED.value:
        return "Processed"
    elif status == PayrixTransactionStatusEnum.SETTLED.value:
        return "Funded"
    elif status in [PayrixTransactionStatusEnum.FAILED.value, PayrixTransactionStatusEnum.RETURNED.value]:
        return "Failed"
    elif status == PayrixTransactionStatusEnum.FORGIVEN.value:
        return "Forgiven"
    elif status == PayrixTransactionStatusEnum.CANCELLED.value:
        return "Cancelled"
    return "Approved"

def _get_refunds_and_retries(payment: MemberPaymentHistory_v2):
    refunds_resp = []
    retries_resp = []
    for trans in payment.refunds_retries:
        if trans.payment_method and trans.payment_method.method in (
                PayrixPaymentMethodEnum.CHECKING.value,
                PayrixPaymentMethodEnum.SAVINGS.value,
                PayrixPaymentMethodEnum.CORP_CHECKING.value,
                PayrixPaymentMethodEnum.CORP_SAVINGS.value,
        ):
            payment_type = "ACH"
        elif trans.payment_method:
            payment_type = "Card"
        else:
            payment_type = "Cash"
        resp = PaymentRefundResponse(
            payment_id=trans.id,
            total_amount=trans.total_amount,
            description=_payment_description(trans),
            processed_date=trans.processed_date,
            payment_status=_payment_status(trans.payrix_transaction_status),
            payment_method_last_4_digits=trans.payment_method,
            payment_type=payment_type
        )

        if trans.payment_transaction_type_id == PaymentTransactionTypeEnum.REFUND.value:
            refunds_resp.append(resp)
        elif trans.payment_transaction_type_id == PaymentTransactionTypeEnum.RETRY_SALE.value:
            retries_resp.append(resp)

    return refunds_resp, retries_resp


def get_payment_info(location_id: int, user_id: int, payment_id: int) -> Response:
    payment_status = MemberPaymentHistory_v2.find_by_id(location_id, user_id, payment_id)
    if not payment_status:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment not found",
        )

    payment_status_data = PaymentStatusResponse.model_validate(payment_status, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Payment found",
        data=payment_status_data,
    )


def retry_payment_info(location_id: int, user_id: int, payment_id: int, body: CreateRetryRequest) -> Response:
    location = Location.find_by_id(location_id)
    if not location.payments:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Payments are disabled for this location",
        )

    payment = _retry_payment(body)
    if not payment:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment not found or Payment method not found or retry payment already in process",
        )
    else:
        payment_status = MemberPaymentHistory_v2.find_by_id(location_id, user_id, payment.id)

    payment_status_data = PaymentStatusResponse.model_validate(payment_status, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Payment found",
        data=payment_status_data,
    )


def _retry_payment(body: CreateRetryRequest):
    payment = MemberPaymentHistory_v2.find_by_id(body.location_id, body.member_id, body.payment_id)
    if not payment:
        return None

    # Get the default payment method. Always use default payment and ignore whatever FE sends - GMS-1380
    payment_method = MemberPaymentMethod.find_by_member_id2(body.location_id, body.member_id, default_method=True)
    if not payment_method:
        return None

    # Check if there is an existing retry payment in process(payrix_transaction_status not in failed, returned) for the original payment.
    if _existing_retry(payment):
        return None

    retry = MemberPaymentHistory_v2(payment.location_id, payment.user_id, payment_method.id)
    fill_model(payment, retry, exclude=['id', 'create_datetime', 'update_datetime', 'payment_method_id', 'processed_date'
                                        'payrix_transaction_status', 'payrix_transaction_error', 'notes'], ignore_nulls=True)
    retry.scheduled_date = utc_now().date()
    retry.processed_by = g.get("user").id if (g and g.get("user")) else 0
    retry.original_total_amount = payment.total_amount
    retry.for_payment_id = payment.for_payment_id if payment.for_payment_id else payment.id
    retry.payment_transaction_type_id = PaymentTransactionTypeEnum.RETRY_SALE.value
    retry.save_and_commit()

    retry.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
    celery.send_task('process_payment_v2', (retry.location_id, retry.user_id, retry.id,))
    retry.save_and_commit()

    return retry


def _existing_retry(payment: MemberPaymentHistory_v2):
    # Check if there are any queued retry payments for the original payment to ensure only one retry is in flight
    if MemberPaymentHistory_v2.get_queued_retry_payment_of_original_payment(
        payment.location_id, payment.id, PaymentTransactionTypeEnum.RETRY_SALE.value
    ):
        return False

    for trans in payment.refunds_retries:
        if (
            trans.payment_transaction_type_id == PaymentTransactionTypeEnum.RETRY_SALE.value
            and trans.payrix_transaction_status
            not in (PayrixTransactionStatusEnum.FAILED.value, PayrixTransactionStatusEnum.RETURNED.value)
        ):
            return True
    return False

def _forgive_payment(payment: MemberPaymentHistory_v2):
    if payment.payrix_transaction_status == PayrixTransactionStatusEnum.FAILED.value:
        payment.payrix_transaction_status = PayrixTransactionStatusEnum.FORGIVEN.value
        payment.save_and_commit()
        # TODO: Create a writeoff / creditmemo invoice and add appropriate ledger entries? Check with Maggie and Chris
        payment_status_data = PaymentStatusResponse.model_validate(payment, from_attributes=True).model_dump()
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UPDATED,
            logger_name=__name__,
            message="Payment marked as Forgiven",
            data=payment_status_data,
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Only failed payment can be forgiven")


def _reinforce_payment(payment: MemberPaymentHistory_v2):
    if payment.payrix_transaction_status == PayrixTransactionStatusEnum.FORGIVEN.value:
        payment.payrix_transaction_status = PayrixTransactionStatusEnum.FAILED.value
        payment.save_and_commit()
        payment_status_data = PaymentStatusResponse.model_validate(payment, from_attributes=True).model_dump()

        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UPDATED,
            logger_name=__name__,
            message="Payment marked as Failed",
            data=payment_status_data,
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Payment is already marked Failed")

def _cancel_payment(payment: MemberPaymentHistory_v2):
    if payment.processed_date is None and payment.payrix_onboarding_status == PayrixOnboardStatusEnum.NOT_READY.value:
        payment.payrix_transaction_status = PayrixTransactionStatusEnum.CANCELLED.value
        payment.save_and_commit()
        payment_status_data = PaymentStatusResponse.model_validate(payment, from_attributes=True).model_dump()

        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UPDATED,
            logger_name=__name__,
            message="Payment marked as Cancelled",
            data=payment_status_data,
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Payment has already been processed and cannot be cancelled")

def _restore_payment(payment: MemberPaymentHistory_v2):
    if payment.payrix_transaction_status == PayrixTransactionStatusEnum.CANCELLED.value:
        payment.payrix_transaction_status = None
        payment.save_and_commit()
        payment_status_data = PaymentStatusResponse.model_validate(payment, from_attributes=True).model_dump()

        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UPDATED,
            logger_name=__name__,
            message="Payment is restored",
            data=payment_status_data,
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Only cancelled payment can be restored")


def _calc_total_payment(payment: MemberPaymentHistory_v2, body: Any, from_invoice=False):
    location = payment.location
    amount = payment.amount
    tax = 0.0
    if body.taxable:
        tax = 0.0 if not location.sales_tax else (location.sales_tax / 100) * (amount)
    payment.total_amount = round(amount + tax, 2)
    payment.tax = tax
    payment.original_total_amount = payment.total_amount
    payment.processed_by = g.get("user").id if (g and g.get("user")) else 0
    payment.payment_method_id = body.payment_method_id if body.payment_method_id else payment.payment_method_id
    if body.payment_method_id == 0:  # Payment has been realized (cash). So set all the payment related stuff and ledger entries
        payment.scheduled_date = utc_now().date()
        payment.processed_date = utc_now()
        payment.payrix_transaction_status = PayrixTransactionStatusEnum.SETTLED.value
        create_payment_ledger_entries(payment)
    payment.save_and_commit()
    if not from_invoice:
        update_outstanding_balance_and_invoice_status(payment.location_id, payment.user_id)
    return payment

