import json
import logging
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List, Any

from dateutil.relativedelta import relativedelta
from requests import Response
from operator import attrgetter

from gmsshared.src.util.dea import (create_credit_memo_invoice, create_credit_memo_ledger_entries,
                                    create_invoice_ledger_entries, create_void_invoice_ledger_entries, get_next_invoice,
                                    update_next_billing_details, create_signup_invoice_item)
from gmsshared.src.util.enums import InvoiceItemStatusTypeEnum, PaymentCategoryEnum, DoorAccessStatusEnum
from gmsshared.src.util.dea import update_outstanding_balance_and_invoice_status, get_next_payment_date

from gmsshared import celery, db
from gmsshared.src.models.location import Location
from gmsshared.src.models.member_payment_method import MemberPaymentMethod
from gmsshared.src.models.member_payment_schedule_temp import MemberPaymentScheduleTemp
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.membership import Membership
from gmsshared.src.models.membership_session import MembershipSession
from gmsshared.src.models.plan import Plan
from gmsshared.src.models.user import User, user_location
from gmsshared.src.models.user_profile import UserProfile
from gmsshared.src.util.enums import (
    RoleEnum,
    MemberStatusEnum,
    ResponseStatusEnum,
    PayrixOnboardStatusEnum,
    BillingTypeEnum,
    MembershipStatusEnum,
    PaymentStatusEnum,
)
from gmsshared.src.util.misc import row2dict, fill_model
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response, g
from gmsshared.src.config import get_config
from gmsshared.src.util.dea import create_invoice_items, create_split_invoice_items
from gmsshared.src.util.dea import create_invoice, process_payment, void_invoices_for_cancelled_memberships
from gmsshared.src.util.validators import to_local
from gmsshared.src.util.datetime_util import utc_now
from members_service.members.dtos.members_requests import (
    CreateInvoice, CreateMemberRequest,
    InvoiceQuery,
    UpdateInvoiceRequest,
    UpdateMemberProfileRequest,
    MemberFilter,
    CreateMembershipRequest,
    UpdateMembershipRequest,
    CreateMembershipSessionRequest,
    PayrixOnboardMemberRequest,
    CreateMembershipQuery,
    UpdateMembershipFreezeRequest,
    DoorAccessMemberLoginRequest,
    RemoveMembershipSessionRequest,
)
from members_service.members.dtos.members_responses import (
    ActivityHistory,
    MemberListResponse,
    MemberProfileResponse,
    Membership as MembershipResponse,
    ReconciliationItem,
    TempMembershipResponse,
    MemberResponse,
    ProfileResponse,
    MembershipSessionResponse,
    RegisteredMemberResponse,
    InvoiceResponse,
    TempPaymentResponse,
    SessionActivity
)
from members_service.payments.dtos.payments_responses import PaymentResponse
from members_service.payments.dtos.payments_requests import CreatePaymentRequest
from members_service.payments.services.payments_private_svc import get_payments_list, create_payment_info
from gmsshared.src.models.invoice import Invoice
from gmsshared.src.models.invoice_item import InvoiceItem
from gmsshared.src.util.enums import ProductCategoryTypeEnum
from gmsshared.src.models.membership_freeze import MembershipFreeze
from gmsshared.src.util.validators import payment_date_format_validator
from gmsshared.src.util.dea import get_plan_end_date
from gmsshared.src.util.dea import create_split_payment_invoices


def get_members_list(location_id: int, query: MemberFilter) -> Response:
    members_list: List[MemberProfile | dict | MemberResponse]
    members_list = MemberProfile.find_by_location(location_id, query.name)
    if not members_list:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No members found",
        )

    mem_list = []
    for member in members_list:
        mem = dict(member)
        mem["membership_status"] = json.dumps(list(filter(lambda x: len(x) > 0, mem["membership_status"].split(","))))
        mem_list.append(mem)
    members_list = [MemberResponse.model_validate(member, from_attributes=True) for member in mem_list]
    members_response: MemberListResponse = MemberListResponse(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Members found",
        data=members_list,
    )
    return create_response(**members_response.model_dump())


def get_registered_members(location_id: int, query: MemberFilter) -> Response:
    members_records = Membership.find_all_members_by_location(location_id, query)
    if not members_records:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No members found",
        )

    member_by_email = {}
    local_now = datetime.strptime(to_local(utc_now()), "%Y-%m-%d %H:%M")
    for member_ship, member_class, user_id, email, first_name, last_name, phone_number, photo_url in members_records:
        if email not in member_by_email:
            member_by_email[email] = {
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number": phone_number,
                "member_classes": [],
                "photo_url": photo_url,
            }

        if member_class:
            class_date_in_local = datetime.strptime(to_local(member_class.class_time), "%Y-%m-%d %H:%M").date()
            class_end_time_in_local = datetime.strptime(to_local(member_class.clazz.end_time), "%Y-%m-%d %H:%M").time()
            if (
                class_date_in_local == local_now.date()
                and class_end_time_in_local > local_now.time()
                and member_class.member_waitlist == 0
                and member_class.member_cancelled_time is None
                and member_class.member_checked_in_time is None
            ):
                coach_name = (
                    f"{member_class.clazz.main_coach.user_profile.first_name} "
                    f"{member_class.clazz.main_coach.user_profile.last_name}"
                    if (member_class.class_id and member_class.clazz.main_coach_id)
                    else None
                )
                member_by_email[email]["member_classes"].append({**member_class.__dict__, "coach_name": coach_name})

    for email, data in member_by_email.items():
        data["member_classes"].sort(key=lambda x: x["class_time"])

    members_list = [
        RegisteredMemberResponse.model_validate(member_data, from_attributes=True).model_dump()
        for member_data in member_by_email.values()
    ]

    if members_list:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Members found",
            data=members_list,
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No Members found",
        )


def get_profile(location_id: int, user_id: int) -> Response:
    member_profile: MemberProfile = MemberProfile.get_info_by_id(location_id, user_id)
    if member_profile is None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No profile found",
        )

    member_info = MemberProfileResponse.model_validate(member_profile, from_attributes=True).model_dump()
    member_info["payment_status"] = PaymentStatusEnum.CURRENT.value if round(member_info["outstanding_balance"], 2) <= 0 else PaymentStatusEnum.PAST_DUE.value
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Profile found",
        data=member_info,
    )


def create_new_member(location_id: int, body: CreateMemberRequest) -> Response:
    user = User.find_by_email(body.email)
    if user:
        member = MemberProfile.find_by_id(location_id, user.id)
        if member:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.CONFLICT,
                logger_name=__name__,
                message=f"Member with email: {body.email} already exists at location: {location_id}",
            )
    try:
        # Create user
        user = User(body.email, "Test@1234")
        user.active = False

        # Create user profile
        user_profile = UserProfile(body.first_name, body.last_name)
        fill_model(body, user_profile, exclude=["membership_plans"], ignore_nulls=False)
        user.user_profile = user_profile
        user.role_type_id = RoleEnum.MEMBER.value
        user.save_and_commit()

        # Associate user to the location
        db.session.execute(user_location.insert(), params={"location_id": location_id, "user_id": user.id})
        db.session.commit()

        # Create member profile
        member_profile = MemberProfile(user.id, location_id, datetime.now())
        fill_model(body, member_profile, exclude=[], ignore_nulls=False)
        member_profile.member_status_type_id = MemberStatusEnum.ACTIVE.value

        # Onboard the member
        location = Location.find_by_id(location_id)
        if location.payrix_onboarding_status == PayrixOnboardStatusEnum.BOARDED.value:
            member_profile.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
            member_profile.save_and_commit()
            try:
                celery.send_task("onboard_member_in_payrix", (member_profile.location_id, member_profile.user_id,))
            except Exception as e:
                logging.error(f"Error while sending onboarding task to broker: {e}")

        # Add member to door_access_vendor
        if location.door_access:
            celery.send_task("door_access_onboard_member", (location_id, user.id,))

        member_profile.save_and_commit()

        member_data = row2dict(member_profile, ["id"])
        member_data.pop("user_id")
        member_data["id"] = member_profile.user_id
        if body.send_setup_email:
            send_profile_setup_email(user)
    except Exception as e:
        logging.error(f"Error while creating member with email: {body.email}: {e}")
        return create_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            status=ResponseStatusEnum.INTERNAL_ERROR,
            logger_name=__name__,
            message=f"We found an error while creating member with email: {body.email}. \
                               Please contact a system administrator.",
        )

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Member created",
        data=member_data,
    )


def add_membership_info(
    location_id: int, user_id: int, body: CreateMembershipRequest, query: CreateMembershipQuery
) -> Response:
    plan = Plan.find_by_id(body.plan_id)
    if not plan:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.PLAN_DOES_NOT_EXIST,
            logger_name=__name__,
            message="No plan found",
        )

    if _check_active_memberships(location_id, user_id, body, plan):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.ACTIVE_MEMBERSHIP_EXISTS,
            logger_name=__name__,
            message="Active membership found",
        )

    if body.split_payments and (plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value and
            plan.paid_in_full_price > sum(payment.payment_amount for payment in body.split_payments)):
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.ERROR,
                logger_name=__name__,
                message="Split payments don't add up to total plan amount",
            )

    membership = _create_membership(body, plan)
    membership.plan_end_date = get_plan_end_date(membership.plan_start_date, plan)
    sales_tax = membership.location.sales_tax if membership.location.sales_tax else 0.0
    if membership.split_payments:
        for payment in membership.split_payments:
            payment['payment_date'] = payment['payment_date'].strftime('%Y-%m-%d')

    if query.process:
        db.session.add(membership)
        db.session.flush()

    # Create invoice_items as per the plan
    if body.split_payment:
        split_payments_dict = [split_payment.model_dump() for split_payment in body.split_payments]
        invoice_items = create_split_invoice_items(membership, plan, sales_tax, split_payments_dict)
    elif membership.plan.billing_type_id == BillingTypeEnum.FREE.value:
        invoice_items = []
        if membership.signup_fee and membership.signup_fee > 0:
            invoice_items.append(create_signup_invoice_item(membership, plan, sales_tax))
    else:
        invoice_items = create_invoice_items(membership, plan, sales_tax)

    # Process either temp membership or membership(process=true)
    if query.process:
        return _process_membership(membership, invoice_items, query.payment_method_id)
    else:
        return _process_temp_membership(membership, invoice_items)

def _process_membership(membership: Membership, invoice_items: List[InvoiceItem], payment_method_id: int):
    data = {}
    invoice = None
    if invoice_items:
        if membership.split_payments:
            invoices = create_split_payment_invoices(membership.location_id, membership.user_id, invoice_items, membership)
            db.session.add_all(invoices)
            db.session.commit()
            for inv in invoices:
                create_invoice_ledger_entries(inv)
            update_outstanding_balance_and_invoice_status(membership.location_id, membership.user_id)
            payment = process_payment(invoices[0], payment_method_id)
        else:
            invoice = create_invoice(membership.location_id, membership.user_id, invoice_items,
                                     ProductCategoryTypeEnum.MEMBERSHIP.value, membership.plan.name)
            create_invoice_ledger_entries(invoice)
            invoice.create_datetime = membership.plan_start_date
            invoice.save_and_commit()
            update_outstanding_balance_and_invoice_status(membership.location_id, membership.user_id)
            payment = process_payment(invoice, payment_method_id)

        if payment:
            payment.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
            payment.save_and_commit()
            celery.send_task('process_payment_v2', (payment.location_id, payment.user_id, payment.id,))
            data = PaymentResponse.model_validate(payment).model_dump()

    # Reset discount fields if apply_discount_to_all_payments is False
    if not membership.apply_discount_to_all_payments:
        membership.discount_percent_per_payment = 0
        membership.discount_amount_per_payment = 0

    # Only commit after invoice and invoice items are created
    db.session.commit()

    # Update next billing date
    if membership.plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value and membership.auto_renewal and not membership.split_payments:
        membership.next_billing_date = membership.plan_end_date + relativedelta(days=1)
    else:
        update_next_billing_details(membership.location_id, membership.user_id, membership=membership)

    if membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        _create_membership_session(membership, inv = invoice)

    if membership.location.door_access:
        celery.send_task("update_member_to_groups", (membership.location_id, membership.user_id,))

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New membership created",
        data=data,
    )

def _process_temp_membership(membership: Membership, invoice_items: List[InvoiceItem]):
    membership_data = TempMembershipResponse.model_validate(membership, from_attributes=True).model_dump()
    if invoice_items:
        if membership.split_payments:
            payments, total_amount = _calc_split_payments(membership, invoice_items)
        else:
            payments, total_amount = _calc_payments(membership, invoice_items)
        payments_resp = [TempPaymentResponse.model_validate(payment).model_dump() for payment in payments]
        membership_data["payments"] = payments_resp
        membership_data["total_amount"] = total_amount
        membership_data["free"] = False
    else:
        membership_data["free"] = True
        membership.save_and_commit()

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New membership created",
        data=membership_data,
    )


def _calc_payments(membership, invoice_items: List[InvoiceItem]):
    if membership.plan.billing_type_id == BillingTypeEnum.FREE.value:
        return [{
            "signup_fee": invoice_items[0].amount,
            "tax": invoice_items[0].tax,
            "total_amount": invoice_items[0].total_amount,
            "due_date": invoice_items[0].due_date
        }], invoice_items[0].total_amount
    # Only Plan Payment
    if len(invoice_items) == 1:
        return [{
            "plan_payment": invoice_items[0].amount,
            "discount": invoice_items[0].discount,
            "tax": invoice_items[0].tax,
            "total_amount": invoice_items[0].total_amount,
            "due_date": invoice_items[0].due_date
        }], invoice_items[0].total_amount
    elif len(invoice_items) > 1 and invoice_items[0].due_date == invoice_items[1].due_date:
        return [{
            "signup_fee": invoice_items[0].amount,
            "plan_payment": invoice_items[1].amount,
            "tax": invoice_items[0].tax + invoice_items[1].tax,
            "discount": invoice_items[1].discount,
            "total_amount": invoice_items[0].total_amount + invoice_items[1].total_amount,
            "due_date": invoice_items[0].due_date
        }], invoice_items[0].total_amount + invoice_items[1].total_amount
    else:
        return[{
          "signup_fee": invoice_items[0].amount,
          "tax": invoice_items[0].tax,
          "total_amount": invoice_items[0].total_amount,
          "due_date": invoice_items[0].due_date
        },
        {"plan_payment": invoice_items[1].amount,
         "tax": invoice_items[1].tax,
         "discount": invoice_items[1].discount,
         "total_amount": invoice_items[1].total_amount,
         "due_date": invoice_items[1].due_date
        }], invoice_items[0].total_amount + invoice_items[1].total_amount

# Combine both calc_payments to single function
def _calc_split_payments(membership, invoice_items: List[InvoiceItem]):
    if membership.signup_fee and len(invoice_items) > 1:
        if invoice_items[0].due_date != invoice_items[1].due_date:
            return [
            {
                "signup_fee": invoice_items[0].amount,
                "tax": invoice_items[0].tax,
                "total_amount": invoice_items[0].total_amount,
                "due_date": invoice_items[0].due_date
            },
            {
                "plan_payment": invoice_items[1].amount,
                 "tax": invoice_items[1].tax,
                 "discount": invoice_items[1].discount,
                 "total_amount": invoice_items[1].total_amount,
                 "due_date": invoice_items[1].due_date
             }
            ],  invoice_items[0].total_amount + invoice_items[1].total_amount
        else:
            return [{
                "signup_fee": invoice_items[0].amount,
                "plan_payment": invoice_items[1].amount,
                "tax": invoice_items[0].tax + invoice_items[1].tax,
                "discount": invoice_items[1].discount,
                "total_amount": invoice_items[0].total_amount + invoice_items[1].total_amount,
                "due_date": invoice_items[0].due_date
            }], invoice_items[0].total_amount + invoice_items[1].total_amount
    else:
        return [{
            "plan_payment": invoice_items[0].amount,
            "discount": invoice_items[0].discount,
            "tax": invoice_items[0].tax,
            "total_amount": invoice_items[0].total_amount,
            "due_date": invoice_items[0].due_date
        }], invoice_items[0].total_amount


def _create_membership_session(mem: Membership, inv: Invoice = None):
    if mem.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        ms = MembershipSession(mem.location_id, mem.user_id, mem.id)
        ms.sessions_count = mem.sessions_count
        ms.sessions_purchase_date = mem.plan_start_date
        ms.updated_by = g.get('user').id
        if inv and inv.invoice_items:
            ms.total_amount=inv.invoice_items[-1].total_amount
        mem.sessions.append(ms)


def _check_active_memberships(location_id: int, user_id: int, body: CreateMembershipRequest, plan: Plan):
    active_memberships = Membership.find_by_plan_id(location_id, user_id, plan.id)

    for mem in active_memberships:
        if mem.membership_status_type_id in [
            MembershipStatusEnum.ACTIVE.value,
            MembershipStatusEnum.FROZEN.value,
            MembershipStatusEnum.NOT_STARTED.value
        ]:
            if mem.auto_renewal:
                if mem.cancel_date is not None:
                    mem_end_date = mem.cancel_date
                    if mem_end_date > body.plan_start_date:
                        return True
                else:
                    return True
            else:
                if mem.cancel_date:
                    mem_end_date = min(mem.plan_end_date, mem.cancel_date)
                    if mem_end_date > body.plan_start_date:
                        return True
                else:
                    mem_end_date = mem.plan_end_date
                    if mem_end_date >= body.plan_start_date:
                        return True


def _create_membership(body: CreateMembershipRequest, plan: Plan) -> MemberPaymentScheduleTemp:
    if body.plan_start_date <= utc_now().date():
        membership_status = MembershipStatusEnum.ACTIVE.value
    else:
        membership_status = MembershipStatusEnum.NOT_STARTED.value
    membership = Membership(
        body.location_id, body.member_id, plan.id, body.plan_start_date, membership_status
    )
    fill_model(body, membership, exclude=[], ignore_nulls=False)
    membership.signup_fee = body.signup_fee if body.signup_fee is not None else 0
    membership.auto_renewal = body.auto_renewal if body.auto_renewal else False
    membership.sessions_count = body.sessions_count if body.sessions_count is not None else 0
    membership.location = plan.location
    membership.apply_discount_to_all_payments = (
        body.apply_discount_to_all_payments if body.apply_discount_to_all_payments else False
    )
    membership.plan = plan
    return membership


def _update_discount_fields(location_id,user_id,membership_data):
    latest_invoice = Invoice.find_discount_applied_latest_invoice_for_membership(location_id,user_id,membership_data['membership_id'])
    if latest_invoice and latest_invoice.discount_percent and latest_invoice.discount_percent > 0:
        membership_data['discount_percent_per_payment'] = latest_invoice.discount_percent
    elif latest_invoice and latest_invoice.discount and latest_invoice.discount > 0:
        membership_data['discount_amount_per_payment'] = latest_invoice.discount
    return


def get_membership_list(location_id: int, user_id: int) -> Response:
    # Get only active memberships and update next_billing_details
    active_memberships = Membership.find_active_memberships(location_id, user_id)
    for membership in active_memberships:
        update_next_billing_details(location_id, user_id, membership)

    memberships = Membership.get_memberships_by_member_id(location_id, user_id)
    if not memberships or len(memberships) == 0:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No memberships found",
        )
    membership_list = [MembershipResponse.model_validate(r).model_dump() for r in memberships]
    for membership_data in membership_list:
        _update_discount_fields(location_id,user_id,membership_data)

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Memberships found",
        data=membership_list,
    )

def get_membership_info(location_id: int, user_id: int, membership_id) -> Response:
    membership = Membership.find_by_membership_id(location_id, user_id, membership_id)
    if not membership:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No memberships found",
        )

    membership_data = MembershipResponse.model_validate(membership, from_attributes=True).model_dump()
    _update_discount_fields(location_id, user_id, membership_data)
    next_invoice = get_next_invoice(location_id, user_id, membership["membership_id"])
    if next_invoice:
        min_next_billing_date = next_invoice.create_datetime
        mem = Membership.find_by_id(location_id, user_id, membership["membership_id"])
        if not mem.split_payments:
            max_next_billing_date = get_next_payment_date(mem, min_next_billing_date)
            membership_data["next_billing_date_range"] = [payment_date_format_validator(min_next_billing_date.date()), payment_date_format_validator(max_next_billing_date.date())]
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Membership found",
        data=membership_data,
    )


def get_invoice_list(location_id: int, user_id: int, query: InvoiceQuery) -> Response:

    invoices = Invoice.find_all_invoices_by_member_id(location_id, user_id)
    if not invoices:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No invoices found",
        )

    if query.membership_id:
        invoices = list(filter(lambda item: item.invoice_items[0].product_id == query.membership_id, invoices))

    if query.next_invoice and query.membership_id:
        invoice = get_next_invoice(location_id, user_id, query.membership_id, invoices)
        if invoice:
            invoices = [invoice]
        else:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.NOT_FOUND,
                logger_name=__name__,
                message="No Charges found",
            )

    # Update create_datetime only if next_invoice is false
    if not query.next_invoice:
        for i in invoices:
            i.create_datetime = i.invoice_items[0].create_datetime

    # Order invoices by due_date and create_datetime
    invoices_with_due_date = [inv for inv in invoices if inv.due_date is not None]
    invoices_without_due_date = [inv for inv in invoices if inv.due_date is None]
    sorted_with_due_date = sorted(invoices_with_due_date, key=attrgetter('due_date', 'create_datetime'), reverse=True)
    sorted_without_due_date = sorted(invoices_without_due_date, key=attrgetter('create_datetime'), reverse=True)
    invoices = sorted_with_due_date + sorted_without_due_date

    invoices_resp = [InvoiceResponse.model_validate(r).model_dump() for r in invoices]

    # Reusing get_payments_list to fill out payment history fields(description, payment_status etc)
    for invoice in invoices_resp:
        invoice["payments"] = get_payments_list(location_id, user_id, invoice["payments"]) if invoice["payments"] else []

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Charges found",
        data=invoices_resp,
    )


def get_invoice_info(location_id: int, user_id: int, invoice_id: int) -> Response:

    invoice = Invoice.find_by_id(location_id, user_id, invoice_id)
    if not invoice:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No Charge found",
        )

    # Check if membership is split type and add due_date to the description
    if invoice.membership_id:
        inv_membership = list(filter(lambda mem: invoice.membership_id == mem.id, invoice.member.memberships))[0]
        if inv_membership.split_payments:
            for item in invoice.invoice_items:
                if item.description.lower().startswith("remaining"):
                    item.description = f"{item.description} on {inv_membership.plan_end_date.strftime('%B %d, %Y')}"
                else:
                    item.description = f"{item.description} on {item.due_date.strftime('%B %d, %Y')}"
    invoice.create_datetime = invoice.invoice_items[0].create_datetime
    invoice_info = InvoiceResponse.model_validate(invoice).model_dump()
    invoice_info["tax"] = round(invoice_info["tax"], 2)

    # Reusing get_payments_list to fill out payment history fields(description, payment_status etc)
    payment_info = get_payments_list(location_id, user_id, invoice.payments) if invoice.payments else []
    invoice_info['payments'] = payment_info
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Charge found",
        data=invoice_info,
    )


def update_invoice_info(location_id: int, user_id: int, invoice_id: int, body: UpdateInvoiceRequest) -> Response:

    invoice = Invoice.find_by_id(location_id, user_id, invoice_id)
    if not invoice:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No Charge found",
        )

    fill_model(body, invoice, exclude=["location_id", "user_id", "invoice_id"], ignore_nulls=True)
    invoice.void_by = g.get('user').id
    invoice.void_datetime = utc_now()
    create_void_invoice_ledger_entries(invoice)
    invoice.save_and_commit()
    update_outstanding_balance_and_invoice_status(location_id, user_id)

    payment_info = get_payments_list(location_id, user_id, invoice.payments) if invoice.payments else []
    invoice_info = InvoiceResponse.model_validate(invoice).model_dump()
    invoice_info['payments'] = payment_info
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Charge found",
        data=invoice_info,
    )


def create_creditmemo(location_id: int, user_id: int, body) -> Response:

    invoice_item = InvoiceItem(
        location_id, user_id, None, "Credit Memo", body.total_amount, 0, 0, utc_now().date())
    invoice_item.invoice_item_status_type_id = InvoiceItemStatusTypeEnum.PROCESSED.value
    invoice = create_credit_memo_invoice(invoice_item, body.notes if body.notes else None)
    create_credit_memo_ledger_entries(invoice)
    invoice.save_and_commit()
    update_outstanding_balance_and_invoice_status(location_id, user_id)
    invoice_info = InvoiceResponse.model_validate(invoice).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Created Credit Memo",
        data=invoice_info,
    )

def add_invoice_info(location_id: int, user_id: int, body: CreateInvoice) -> Response:

    if body.payment_category_type_id:
        description = _get_payment_category_text(body.payment_category_type_id)
        if body.notes:
            description = (description + f" - {body.notes}")[:300]

        invoice_item = InvoiceItem(
            location_id,
            user_id,
            body.payment_category_type_id,
            description,
            amount=body.amount,
            discount=0,
            tax=body.total_amount - body.amount,
            due_date=body.scheduled_date if body.scheduled_date else utc_now().date())
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_REQUEST,
            logger_name=__name__,
            message="No Category provided",
        )

    invoice_item.invoice_item_status_type_id = InvoiceItemStatusTypeEnum.PENDING.value
    invoice = create_invoice(location_id, user_id, [invoice_item], ProductCategoryTypeEnum.FEES.value,
                             description)
    invoice.save_and_commit()

    if not body.auto_payment_on_due:
        update_outstanding_balance_and_invoice_status(location_id, user_id)
        payment_info = CreatePaymentRequest(
            location_id=location_id,
            member_id=user_id,
            invoice_id=invoice.id,
            payment_method_id=body.payment_method_id,
            amount=body.total_amount,
            description=body.notes,
            scheduled_date=body.scheduled_date
        )
        create_payment_info(location_id, user_id, payment_info, from_invoice = True)

    update_outstanding_balance_and_invoice_status(location_id, user_id)

    #Temporarily commented out the invoice response data to fix the missing invoice_id in payment_history_v2
    #invoice.payments = []
    #invoice_info = InvoiceResponse.model_validate(invoice).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Created Charge",
    )

def _get_payment_category_text(category_id: int) -> str | None:
    if category_id == PaymentCategoryEnum.LATE_FEE.value:
        return "Late Fee"
    elif category_id == PaymentCategoryEnum.NOSHOW_FEE.value:
        return "No Show Fee"
    elif category_id == PaymentCategoryEnum.CANCELLATION_FEE.value:
        return "Cancellation Fee"
    else:
        return "Other"


def update_membership_info(
    location_id: int, user_id: int, membership_id: int, body: UpdateMembershipRequest
) -> Response:
    membership = Membership.find_by_id(location_id, user_id, membership_id)
    if not membership:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No memberships found",
        )

    if body.membership_status_type_id == MembershipStatusEnum.FROZEN.value and (
        membership.membership_status_type_id
        not in [MembershipStatusEnum.FROZEN.value, MembershipStatusEnum.CANCELLED.value]
    ):  # Freeze
        _freeze_membership(membership, body)
    elif body.membership_status_type_id == MembershipStatusEnum.CANCELLED.value:  # Cancel
        _cancel_membership(membership, body)
    elif (
        body.membership_status_type_id == MembershipStatusEnum.ACTIVE.value
        and membership.membership_status_type_id == MembershipStatusEnum.FROZEN.value
    ):  # Unfreeze
        _unfreeze_membership(membership)

    # If plan_start_date is moved(only for NOT_STARTED memberships), move the plan_end_date
    if (
        membership.membership_status_type_id == MembershipStatusEnum.NOT_STARTED.value
        and body.plan_start_date
        and body.plan_start_date != membership.plan_start_date
    ):
        membership.plan_end_date = membership.plan_end_date + (body.plan_start_date - membership.plan_start_date)

    fill_model(body, membership, exclude=["membership_status_type_id"], ignore_nulls=True)

    # Change the membership status from NOT_STARTED to ACTIVE(if needed)
    if (
        membership.membership_status_type_id == MembershipStatusEnum.NOT_STARTED.value
        and membership.plan_start_date <= datetime.strptime(g.get("today_date").split(" ")[0], "%Y-%m-%d").date()
    ):
        membership.membership_status_type_id = MembershipStatusEnum.ACTIVE.value

    membership.save_and_commit()

    update_outstanding_balance_and_invoice_status(location_id, user_id)
    return create_response(
        status_code=HTTPStatus.OK, status=ResponseStatusEnum.UPDATED, logger_name=__name__, message="Membership updated"
    )

def _freeze_membership(mem: Membership, body: Any) -> None:
    # Create a new edit record for the freeze
    mem_edit = MembershipFreeze(mem.location_id, mem.user_id, mem.id)
    today_date = datetime.strptime(g.get("today_date").split(" ")[0], "%Y-%m-%d")
    if body.freeze_from <= today_date.date():
        freeze_interval = timedelta(days=abs(body.freeze_to - body.freeze_from).days + 1)
        mem.plan_end_date = mem.plan_end_date + freeze_interval
        if mem.next_billing_date:
            mem.next_billing_date = mem.next_billing_date + freeze_interval
        mem_edit.freeze_date = mem.freeze_date = utc_now().date()

        if body.freeze_to >= utc_now().date():  # Only freeze the membership if the freeze_to is in the future
            mem.membership_status_type_id = MembershipStatusEnum.FROZEN.value

    mem_edit.freeze_reason_type_id = body.freeze_reason_type_id
    mem_edit.freeze_from = body.freeze_from
    mem_edit.freeze_to = body.freeze_to
    mem_edit.freeze_by = mem.freeze_by = g.get('user').id
    db.session.add_all([mem_edit, mem])
    db.session.commit()

    if mem.location.door_access:
        celery.send_task("update_member_to_groups", (mem.location_id, mem.user_id,))


def _cancel_membership(mem: Membership, body: Any) -> None:
    today_date = datetime.strptime(g.get("today_date").split(" ")[0], "%Y-%m-%d")
    if today_date.date() == body.cancel_date:
        mem.cancelled_date = utc_now().date()
        mem.membership_status_type_id = MembershipStatusEnum.CANCELLED.value
    mem.cancelled_by = g.get('user').id
    void_invoices_for_cancelled_memberships(mem, body.cancel_date)
    mem.save_and_commit()

    if mem.location.door_access:
        celery.send_task("update_member_to_groups", (mem.location_id, mem.user_id,))


def _unfreeze_membership(mem: Membership):

    original_freeze = timedelta(days=abs(mem.freeze_to - mem.freeze_from).days + 1)
    current_freeze = timedelta(days=(utc_now().date() - mem.freeze_from).days)
    diff_freeze = original_freeze if current_freeze.days < 0 else original_freeze - current_freeze

    mem.plan_end_date = mem.plan_end_date - diff_freeze
    mem.freeze_from = mem.freeze_to = mem.freeze_by = mem.freeze_date = mem.freeze_reason_type_id = None
    mem.membership_status_type_id = MembershipStatusEnum.ACTIVE.value
    mem.unfreeze_date = utc_now().date()
    mem.unfreeze_by = g.get('user').id
    mem_freeze = None   # Update the freeze record for the freeze that is being unfrozen which is the last record in the freeze table
    if mem.freezes:
        mem_freeze = mem.freezes[-1]
        mem_freeze.unfreeze_date = mem.unfreeze_date
        mem_freeze.unfreeze_by = mem.unfreeze_by
        mem_freeze.freeze_to = mem.unfreeze_date
    db.session.add_all([mem_freeze, mem])
    db.session.commit()

    if mem.location.door_access:
        celery.send_task("update_member_to_groups", (mem.location_id, mem.user_id,))


def update_membership_freeze_info(location_id: int, body: UpdateMembershipFreezeRequest):
    mem = Membership.find_by_id(location_id, body.member_id, body.membership_id)
    if not mem:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Membership not found",
        )

    freeze = next((f for f in mem.freezes if f.id == body.freeze_id), None)
    if not freeze:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Freeze not found",
        )

    today = utc_now().date()

    # Cancel upcoming freeze
    if body.cancel_date and freeze.freeze_from > today:
        db.session.delete(freeze)
        db.session.commit()
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.SUCCESS,
            logger_name=__name__,
            message="Upcoming freeze cancelled",
        )

    # Adjust dates if duration has changed
    old_duration = (freeze.freeze_to - freeze.freeze_from).days + 1
    new_duration = (body.freeze_to - body.freeze_from).days + 1
    diff_days = new_duration - old_duration

    if diff_days != 0:
        mem.plan_end_date += timedelta(days=diff_days)
        if mem.next_billing_date:
            mem.next_billing_date += timedelta(days=diff_days)

    # Update freeze details
    if mem.freeze_to == freeze.freeze_to:
        mem.freeze_to = body.freeze_to
    freeze.freeze_from = body.freeze_from
    freeze.freeze_to = body.freeze_to
    freeze.freeze_reason_type_id = body.freeze_reason_type_id
    freeze.freeze_date = utc_now().date() if body.freeze_from != freeze.freeze_from else freeze.freeze_date

    # Update membership status based on freeze window
    if body.freeze_from <= today <= body.freeze_to:
        mem.membership_status_type_id = MembershipStatusEnum.FROZEN.value
    else:
        mem.membership_status_type_id = MembershipStatusEnum.ACTIVE.value

    mem.save_and_commit()

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SUCCESS,
        logger_name=__name__,
        message="Freeze updated",
    )


def get_member_profile_info(location_id: int, user_id: int) -> Response:
    member_info: MemberProfile = MemberProfile.get_profile_info_by_id(location_id, user_id)
    if not member_info:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No profile found",
        )
    member_profile_response: ProfileResponse = ProfileResponse.model_validate(dict(member_info), from_attributes=True)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Profile found",
        data=member_profile_response.model_dump(),
    )


def get_member_reconciliation_info(location_id: int, user_id: int) -> Response:
    reconciliation_info = MemberProfile.get_reconciliation_info(location_id, user_id)
    data = [ReconciliationItem.model_validate(r, from_attributes=True).model_dump() for r in reconciliation_info]
    if not data:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No Reconciliation found",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Reconciliation found",
        data=data,
    )

def get_member_activity_history(location_id: int, user_id: int) -> Response:
    activity_history = MemberProfile.get_activity_history(location_id, user_id)
    data = [ActivityHistory.model_validate(r, from_attributes=True).model_dump() for r in activity_history]
    if not data:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No Activity History found",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Activity History found",
        data=data,
    )


def update_member_profile_info(location_id: int, user_id: int, body: UpdateMemberProfileRequest) -> Response:
    user: User = User.find_by_location_and_user(user_id, location_id)
    if user:
        user_profile: UserProfile = user.user_profile
        member_profile: MemberProfile = MemberProfile.find_by_id(location_id, user.id)
        if user_profile and member_profile:
            fill_model(body, user_profile, exclude=[], ignore_nulls=False)
            user_profile.save_and_commit()
            user.user_profile = user_profile
            user.role_type_id = RoleEnum.MEMBER.value
            user.email = body.email
            user.save_and_commit()
            old_door_access_credential = member_profile.door_access_credential
            fill_model(body, member_profile, exclude=[], ignore_nulls=False)
            member_profile.save_and_commit()

            if body.door_access_credential and  (old_door_access_credential != body.door_access_credential):
                # Delete the old card and create a new one
                celery.send_task("door_access_create_credential", (location_id, user.id, body.door_access_credential))

            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.UPDATED,
                logger_name=__name__,
                message="Member Updated",
            )
        else:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.MEMBER_DOES_NOT_EXIST,
                logger_name=__name__,
                message="Member does not exist",
            )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.MEMBER_DOES_NOT_EXIST,
            logger_name=__name__,
            message="Member does not exist",
        )


def add_membership_sessions(
    location_id: int, user_id: int, membership_id: int, body: CreateMembershipSessionRequest
) -> Response:

    mem = Membership.find_by_id(location_id, user_id, membership_id)
    if not mem:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No membership found",
        )

    payment_method = MemberPaymentMethod.find_by_id(body.location_id, body.member_id, body.payment_method_id)
    if payment_method is None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Payment method not found",
        )

    amount = round(body.sessions_count * body.price_per_session, 2)
    tax = 0.0
    if mem.plan.taxable:
        tax = amount * (mem.location.sales_tax / 100) if mem.location.sales_tax else 0.0
        tax = round(tax, 2)
    total_amount = round(amount + tax, 2)

    invoice_item = InvoiceItem(
        location_id, user_id, mem.id, f"{body.sessions_count} sessions - {mem.plan.name}",
        amount=total_amount,
        discount=0.0,
        tax=tax,
        due_date=utc_now().date(),
    )
    invoice = create_invoice(location_id, user_id, [invoice_item], ProductCategoryTypeEnum.MEMBERSHIP.value, f"{mem.plan.name} - Add Session Pack")
    create_invoice_ledger_entries(invoice)
    invoice.save_and_commit()
    _add_membership_session(mem, body, inv = invoice)

    update_outstanding_balance_and_invoice_status(location_id, user_id)
    payment = process_payment(invoice, body.payment_method_id)
    if payment:
        payment.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
        payment.save_and_commit()
        celery.send_task('process_payment_v2', (payment.location_id, payment.user_id, payment.id,))
        data = PaymentResponse.model_validate(payment).model_dump()
    else:
        data = {}

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="New sessions created",
        data=data,
    )


def remove_membership_sessions(
    location_id: int, user_id: int, membership_id: int, body: RemoveMembershipSessionRequest
) -> Response:

    mem = Membership.find_by_id(location_id, user_id, membership_id)
    if not mem:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No membership found",
        )

    if body.sessions_count > 0:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="The removed sessions count must be negative value",
        )
    if mem.sessions_count < -body.sessions_count:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="The removed sessions count must be less or equal to the remaining sessions count",
        )

    _remove_membership_session(mem, body)

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.DELETED,
        logger_name=__name__,
        message="sessions deleted"
    )


def add_member_to_payrix(location_id: int, user_id: int, body: PayrixOnboardMemberRequest) -> Response:
    mem = MemberProfile.find_by_id(location_id, user_id)
    if not mem:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No member found",
        )

    if (mem.location.payrix_onboarding_status == PayrixOnboardStatusEnum.BOARDED.value) and (
        mem.payrix_customer_id is None
    ):
        mem.payrix_onboarding_status = PayrixOnboardStatusEnum.QUEUED.value
        mem.save_and_commit()
        try:
            celery.send_task("onboard_member_in_payrix", (mem.location_id, mem.user_id))
        except Exception as e:
            logging.error(f"Error while sending onboarding task to broker: {e}")
    mem.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Member onboarded to Payrix created",
    )


def get_membership_sessions_list(location_id: int, user_id: int, membership_id: int) -> Response:
    mem = Membership.find_by_id(location_id, user_id, membership_id)
    if not mem:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No membership found",
        )

    mem_sessions = MembershipSession.get_sessions_detail_by_id(location_id, user_id, membership_id)
    response = MembershipSessionResponse.model_validate(mem_sessions, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Membership session found",
        data=response,
    )


def _add_membership_session(mem: Membership, body: CreateMembershipSessionRequest, inv: Invoice = None) -> Response:
    plan: Plan = mem.plan
    if plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        ms = MembershipSession(mem.location_id, mem.user_id, mem.id)
        ms.sessions_count = body.sessions_count
        ms.sessions_purchase_date = utc_now().date()
        ms.price_per_session = body.price_per_session
        ms.updated_by = g.get('user').id
        if inv:
            ms.total_amount = inv.total_amount
        mem.sessions_count = mem.sessions_count + ms.sessions_count
        mem.sessions.append(ms)
        mem.save_and_commit()


def _remove_membership_session(mem: Membership, body: RemoveMembershipSessionRequest) -> Response:
    plan: Plan = mem.plan
    if plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        ms = MembershipSession(mem.location_id, mem.user_id, mem.id)
        ms.sessions_count = body.sessions_count
        ms.sessions_purchase_date = utc_now().date()
        ms.notes = body.reason if body.reason else None
        ms.updated_by = g.get('user').id
        mem.sessions_count = mem.sessions_count + ms.sessions_count
        mem.sessions.append(ms)
        mem.save_and_commit()


def send_profile_setup_email(user: User | int):
    if isinstance(user, int):
        user = User.find_by_id(user)
    token = User.generate_verification_token(user.email)
    link = f"{get_config().STOREFRONT_URL}/setup-profile?token={token}"
    data = {"first_name": user.user_profile.first_name, "gym_name": user.locations[0].gym.name, "link": link}
    celery.send_task("profile_setup_email", (user.email, data))
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.SENT_MAIL,
        logger_name=__name__,
        message="Profile Setup Email Sent",
    )

def get_membership_session_history(location_id: int, user_id: int, membership_id: int):
    session_history = Membership.session_activity_history(location_id, user_id, membership_id)
    data = [SessionActivity.model_validate(i, from_attributes=True).model_dump() for i in session_history]
    if not data:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No Session Activity History found",
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Session Activity History found",
        data=data,
    )