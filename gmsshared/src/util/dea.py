from datetime import date, datetime, timedelta
from typing import List, Any
import copy
from dateutil.relativedelta import relativedelta
from gmsshared.src.web.context import g
from pandas import Timestamp
import pandas as pd

from gmsshared.src.models.invoice import Invoice
from gmsshared.src.models.invoice_item import InvoiceItem
from gmsshared.src.models.member_payment_history_v2 import MemberPaymentHistory_v2
from gmsshared.src.models._acct_ledger import _AcctLedger
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.plan import Plan
from gmsshared.src.models.membership import Membership
from gmsshared.src.util.validators import to_local_activity_history

from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.util.enums import (
    DurationTypeEnum,
    BillingTypeEnum,
    InvoiceItemStatusTypeEnum,
    InvoiceStatusTypeEnum,
    InvoiceTypeEnum,
    MembershipStatusEnum,
    PaymentCategoryEnum,
    ProductCategoryTypeEnum
)
from gmsshared.src.util.enums import CharterOfAccountsTypeEnum
from gmsshared import db

def get_nth_renewal_start_date(membership: Membership, plan: Plan, n: int,) -> Any:
    plan_start_date = membership.plan_start_date
    if plan.duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
        nth_renewal_start_date = plan_start_date + timedelta(days=(plan.duration * (n - 1)))
    elif plan.duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
        nth_renewal_start_date = plan_start_date + timedelta(weeks=(plan.duration * (n - 1)))
    elif plan.duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
        nth_renewal_start_date = plan_start_date + relativedelta(months=+(plan.duration * (n - 1)))
    elif plan.duration_type_id in [DurationTypeEnum.YEARS.value, DurationTypeEnum.YEAR.value]:
        nth_renewal_start_date = plan_start_date + relativedelta(years=+(plan.duration * (n - 1)))
    return nth_renewal_start_date

def calc_discount(membership, amount):
    discount = 0.0

    if membership.discount_amount_per_payment:
        discount = round(membership.discount_amount_per_payment, 2)
    elif membership.discount_percent_per_payment:
        discount = round(amount * (membership.discount_percent_per_payment / 100), 2)
    return discount

def _prorate_frontend(sdate, amount):
    # Only frontend proration - meaning, only prorate for the beginning of the membership
    sdate = Timestamp(sdate)
    days_in_this_month = sdate.daysinmonth
    remaining_days_in_month = days_in_this_month - sdate.day + 1
    price_per_day = amount / days_in_this_month
    return round(price_per_day * remaining_days_in_month, 2)

def get_plan_end_date(plan_start_date, plan):
    # Calc end_date based on duration_type and duration
    if plan.duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
        end_date = plan_start_date + timedelta(days=plan.duration - 1 if plan.duration else 0)
    if plan.duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
        days = plan.duration * 7 if plan.duration else 0
        end_date = plan_start_date + timedelta(days=days - 1)
    elif plan.duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
        end_date = plan_start_date + relativedelta(months=+plan.duration if plan.duration else 0)
    elif plan.duration_type_id in [DurationTypeEnum.YEARS.value, DurationTypeEnum.YEAR.value]:
        end_date = plan_start_date + relativedelta(years=plan.duration if plan.duration else 0)
    elif plan.billing_type_id in [BillingTypeEnum.SESSION_PACKS.value]:
        end_date = plan_start_date + relativedelta(years=5)
    return end_date

def get_plan_start_date(plan_end_date, plan):
    # Calc end_date based on duration_type and duration
    if plan.duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
        start_date = plan_end_date - timedelta(days=plan.duration - 1 if plan.duration else 0)
    if plan.duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
        days = plan.duration * 7 if plan.duration else 0
        start_date = plan_end_date - timedelta(days=days - 1)
    elif plan.duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
        start_date = plan_end_date - relativedelta(months=+plan.duration if plan.duration else 0)
    elif plan.duration_type_id in [DurationTypeEnum.YEARS.value, DurationTypeEnum.YEAR.value]:
        start_date = plan_end_date - relativedelta(years=plan.duration if plan.duration else 0)
    elif plan.billing_type_id in [BillingTypeEnum.SESSION_PACKS.value]:
        start_date = plan_end_date - relativedelta(years=5)
    return start_date

def get_plan_amount(plan: Plan):
    if plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value:
        plan_amount = plan.paid_in_full_price
    elif plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        plan_amount = plan.class_or_session_pack_price
    elif plan.billing_type_id == BillingTypeEnum.RECURRING.value:
        plan_amount = plan.recurring_amount
    else:
        plan_amount = 0.0
    return plan_amount

def create_signup_invoice_item(mem, plan, sales_tax):
    signup_fee = mem.signup_fee
    tax = round((sales_tax / 100) * signup_fee, 2) if plan.taxable else 0
    description = f"Signup fee - {mem.plan.name}"
    signup_ii = InvoiceItem(mem.location_id, mem.user_id, mem.id, description, signup_fee, 0, tax, mem.signup_fee_due_date)
    return signup_ii

# PIF, First of Month, Recurring Invoice Items
def create_invoice_items(mem: Membership, plan: Plan, sales_tax, mem_start_date = None, renewal = False):
    invoice_items = []

    # Signup Fee Invoice Item
    if mem.signup_fee and mem.signup_fee > 0 and not renewal:
        invoice_items.append(create_signup_invoice_item(mem, plan, sales_tax))

    # Plan Payment Invoice Item
    if plan.first_of_month:
        amount = _prorate_frontend(mem.plan_start_date, plan.recurring_amount)
    else:
        amount = get_plan_amount(plan)

    discount = calc_discount(mem, amount)
    discounted_amount = max(0, amount - discount)
    tax = round((sales_tax / 100) * discounted_amount, 2) if plan.taxable else 0
    description = f"Plan payment - {mem.plan.name}"

    if mem_start_date:
        if mem.next_billing_date and mem.next_billing_date >= mem.plan_start_date:
            scheduled_date = mem.next_billing_date
        else:
            scheduled_date = mem_start_date
    else:
        scheduled_date = mem.first_payment_date if hasattr(mem, "first_payment_date") else mem.plan_start_date

    plan_payment_ii = InvoiceItem(mem.location_id, mem.user_id, mem.id, description, amount, discount, tax, scheduled_date)
    if mem.discount_percent_per_payment:
        plan_payment_ii.discount_percent = mem.discount_percent_per_payment
    invoice_items.append(plan_payment_ii)
    return invoice_items

# Split Payment Invoice items
def create_split_invoice_items(mem, plan, sales_tax, split_payments, renewal = False):
    invoice_items = []

    # Signup Fee Invoice Item
    if mem.signup_fee and mem.signup_fee > 0 and not renewal:
        invoice_items.append(create_signup_invoice_item(mem, plan, sales_tax))

    for i, split in enumerate(split_payments):
        if split["payment_amount"] != 0:
            split_amount = split["payment_amount"]
            discount = 0.0
            if i == 0 or mem.apply_discount_to_all_payments:
                discount = calc_discount(mem, split_amount)
            discounted_amount = max(0, split_amount - discount)
            tax = round((sales_tax / 100) * discounted_amount, 2) if plan.taxable else 0
            description = f"Split payment {i+1} - {mem.plan.name}"
            invoice_item = InvoiceItem(mem.location_id, mem.user_id, mem.id, description, split_amount, discount, tax, split["payment_date"])
            invoice_items.append(invoice_item)

    # Remaining Split Payment Amount
    plan_amount = mem.plan.paid_in_full_price
    total_split_amount = sum([split["payment_amount"] for split in split_payments])
    if total_split_amount < plan_amount:
        remaining_amount = plan_amount - total_split_amount
        discount = 0.0
        if mem.apply_discount_to_all_payments:
            discount = calc_discount(mem, remaining_amount)
        discounted_amount = max(0, remaining_amount - discount)
        tax = round((sales_tax / 100) * discounted_amount, 2) if plan.taxable else 0
        description = f"Remaining split payment - {mem.plan.name}"
        invoice_item = InvoiceItem(mem.location_id, mem.user_id, mem.id, description, remaining_amount, discount, tax, None)
        invoice_items.append(invoice_item)
    return invoice_items

def _prorate_backend(bill_date: datetime.date, end_date: datetime.date, plan: Plan, amount):

    days_in_the_period = 1
    if plan.first_of_month:
        days_in_the_period = Timestamp(bill_date).daysinmonth
    elif plan.recurring_duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
        days_in_the_period = plan.recurring_interval * Timestamp(bill_date).daysinmonth
    elif plan.recurring_duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
        days_in_the_period = plan.recurring_interval * 7
    elif plan.recurring_duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
        days_in_the_period = plan.recurring_interval

    price_per_day = amount / days_in_the_period
    bill_date = bill_date.date() if isinstance(bill_date, datetime) else bill_date
    amount = round(price_per_day * ((end_date - bill_date).days + 1), 2)

    if amount > 0:
        return amount
    else:
        return 0

def _get_plan_amount(plan: Plan):

    if plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value:
        plan_amount = plan.paid_in_full_price
    elif plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        plan_amount = plan.class_or_session_pack_price
    elif plan.billing_type_id == BillingTypeEnum.RECURRING.value:
        plan_amount = plan.recurring_amount
    else:
        plan_amount = 0.0

    return plan_amount

def _get_next_split_invoice(invoices: List[Invoice], mem: Membership):
    # Return the pending split payment invoice due_date and amount
    pending_invoices = list(
        filter(lambda invoice: invoice.invoice_status_type_id == InvoiceStatusTypeEnum.PENDING.value, invoices))
    if pending_invoices:
        next_invoice = min(pending_invoices, key=lambda inv: inv.due_date)
        return next_invoice
    elif mem.auto_renewal:
        old_mem_start_date = get_plan_start_date(mem.plan_end_date, mem.plan)
        renewed_split_payments = get_renewed_split_payments(mem, mem.plan_end_date + relativedelta(days=1),
                                                            old_mem_start_date)
        amount = renewed_split_payments[0]["payment_amount"]
        discount = calc_discount(mem, renewed_split_payments[0]["payment_amount"])
        discounted_amount = amount - discount
        due_date = datetime.strptime(renewed_split_payments[0]["payment_date"], "%Y-%m-%d").date()
        tax =  round((mem.location.sales_tax / 100) * discounted_amount, 2) if mem.plan.taxable else 0
        ii = InvoiceItem(mem.location_id, mem.user_id, mem.id, f"Split payment 1 - {mem.plan.name}",
                         amount, discount, tax, due_date)
        invoice = Invoice(mem.location_id, mem.user_id)
        invoice.invoice_items = [ii]
        invoice.create_datetime = due_date
        invoice.description = f"{mem.plan.name} - Renewal - Split payment 1"
        return invoice
    else:
        return None

def _get_next_pif_invoice(invoices: List[Invoice], mem: Membership):
    next_invoice_date =  mem.plan_end_date + relativedelta(days=1)
    if mem.next_billing_date and mem.next_billing_date > next_invoice_date:
        next_invoice_date = mem.next_billing_date
    amount = mem.plan.paid_in_full_price
    discount = calc_discount(mem, amount)
    discounted_amount = amount - discount
    tax = 0.0
    if mem.plan.taxable:
        tax = round((mem.location.sales_tax / 100) * discounted_amount, 2)
    invoice_item= InvoiceItem(mem.location_id, mem.user_id, mem.id,f"Plan payment - {mem.plan.name}", amount, discount, tax, next_invoice_date)
    next_invoice = Invoice(mem.location_id, mem.user_id)
    next_invoice.description = f"Plan payment - {mem.plan.name}"
    next_invoice.invoice_items = [invoice_item]
    next_invoice.invoice_type_id = InvoiceTypeEnum.INVOICE.value
    next_invoice.invoice_status_type_id = InvoiceStatusTypeEnum.PENDING.value
    next_invoice.create_datetime = datetime.combine(next_invoice_date, datetime.min.time())
    return next_invoice


def get_next_billing_details(invoices: List[Invoice], mem: Membership) -> tuple:

    plan: Plan = mem.plan
    if plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value and mem.split_payments:
        next_invoice = _get_next_split_invoice(invoices, mem)
        if next_invoice:
            return next_invoice.due_date, next_invoice.total_amount
        return None, None

    elif plan.billing_type_id in (BillingTypeEnum.RECURRING.value, BillingTypeEnum.PAID_IN_FULL.value):
        # Return the next invoice due_date and amount
        next_invoice = get_next_invoice(mem.location_id, mem.user_id, mem.id)
        if next_invoice:
            return next_invoice.due_date, next_invoice.total_amount
        else: return None, None
    else: return None, None


def get_next_invoice(location_id: int, user_id: int, membership_id: int, invoices: List[Invoice] = None) -> Invoice | None:

    if not invoices:
        invoices = Invoice.find_all_invoices_by_member_id(location_id, user_id)

    membership_invoices = list(filter(lambda item: item.membership_id == membership_id, invoices))
    if not membership_invoices:
        return None

    mem = Membership.find_by_id(location_id, user_id, membership_id)
    plan: Plan = mem.plan

    if plan.billing_type_id in (
            BillingTypeEnum.SESSION_PACKS.value,
            BillingTypeEnum.FREE.value,
    ): # There is no next invoice for these types of memberships
        return None

    # PIF next invoice
    if plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value:
        if mem.split_payments and len(mem.split_payments) > 0:
            return _get_next_split_invoice(membership_invoices, mem)
        if mem.auto_renewal:
            return _get_next_pif_invoice(membership_invoices, mem)
        else:
            return None

    # Recurring next invoice
    latest_invoice = max(membership_invoices, key=lambda invoice: invoice.create_datetime) if membership_invoices else None
    next_invoice_date = get_next_payment_date(mem, latest_invoice.create_datetime)
    if not next_invoice_date:
        return None

    # Factor in freezes
    if hasattr(mem, 'freezes') and mem.freezes:
        total_freeze = sum([(freeze.freeze_to - freeze.freeze_from).days for freeze in mem.freezes
                            if min(latest_invoice.create_datetime.date(), freeze.freeze_from) <= latest_invoice.create_datetime.date() <= freeze.freeze_to
                            ]) + 1
    else:
        total_freeze = 0
    next_invoice_date = next_invoice_date + timedelta(days=total_freeze)

    # No next invoice if next_invoice_date > plan_end_date
    if (next_invoice_date.date() > mem.plan_end_date) and (mem.auto_renewal == False):
        return None

    # Figure out the payment amount for the next invoice
    amount, discount, tax, total_amount = calc_next_payment(mem, plan, next_invoice_date,  mem.location.sales_tax)

    # Figure out the due_date for the next invoice
    if mem.next_billing_date and (mem.next_billing_date > next_invoice_date.date()):
        due_date = mem.next_billing_date
    else:
        due_date = next_invoice_date.date()

    # Return the next invoice. Can we use create_invoice_item()??
    invoice_item: InvoiceItem = InvoiceItem(mem.location_id, mem.user_id, mem.id,f"Plan payment - {mem.plan.name}", amount, discount, tax, due_date)
    if mem.discount_percent_per_payment:
        invoice_item.discount_percent = mem.discount_percent_per_payment
    next_invoice: Invoice = Invoice(mem.location_id, mem.user_id)
    next_invoice.description = f"Plan payment - {mem.plan.name}"
    next_invoice.invoice_items = [invoice_item]
    next_invoice.invoice_type_id = InvoiceTypeEnum.INVOICE.value
    next_invoice.invoice_status_type_id = InvoiceStatusTypeEnum.PENDING.value
    next_invoice.create_datetime = next_invoice_date
    return next_invoice

def get_next_payment_date(mem: Membership, bill_date: datetime.date) -> datetime.date:

    next_date = bill_date
    plan = mem.plan
    if plan.billing_type_id == BillingTypeEnum.RECURRING.value:
        if plan.first_of_month:
            next_date = bill_date + relativedelta(months=1)
            next_date = datetime(next_date.year, next_date.month, 1)
        elif plan.recurring_duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
            next_date = bill_date + relativedelta(months=+int(plan.recurring_interval if plan.recurring_interval else 0))
        elif plan.recurring_duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
            next_date = bill_date + relativedelta(weeks=+int(plan.recurring_interval) if plan.recurring_interval else 0)
        elif plan.recurring_duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
            next_date = bill_date + relativedelta(days=+int(plan.recurring_interval if plan.recurring_interval else 0))
        elif plan.recurring_duration_type_id in [DurationTypeEnum.YEARS.value, DurationTypeEnum.YEAR.value]:
            next_date = bill_date + relativedelta(years=+int(plan.recurring_interval if plan.recurring_interval else 0))
    elif plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value:
        if plan.duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
            next_date = bill_date + relativedelta(months=+int(plan.duration if plan.duration else 0)) + timedelta(days=1)
        elif plan.duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
            next_date = bill_date + relativedelta(weeks=+int(plan.duration) if plan.duration else 0) + timedelta(days=1)
        elif plan.duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
            next_date = bill_date + relativedelta(days=+int(plan.duration if plan.duration else 0)) + timedelta(days=1)
        elif plan.duration_type_id in [DurationTypeEnum.YEARS.value, DurationTypeEnum.YEAR.value]:
            next_date = bill_date + relativedelta(years=+int(plan.duration if plan.duration else 0)) + timedelta(days=1)

    return next_date

# Call this function for next_invoice only. NOT for the first invoice
def calc_next_payment(membership: Membership,
                      plan: Plan,
                      bill_date: datetime.date,
                      sales_tax: float):

    amount = _get_plan_amount(plan)

    # First of month
    if plan.billing_type_id in [BillingTypeEnum.RECURRING.value] and plan.first_of_month and bill_date.day != 1:
        amount = _prorate_frontend(bill_date, amount)

    # Get next_date after the bill_date to decide if proration is required
    next_date = get_next_payment_date(membership, bill_date)
    if (next_date.date() > membership.plan_end_date) and (membership.auto_renewal == False):
        amount = _prorate_backend(bill_date, membership.plan_end_date, membership.plan, amount)

    # Discount
    discount = 0.0

    if membership.discount_amount_per_payment:
        discount = round(membership.discount_amount_per_payment, 2)
    elif membership.discount_percent_per_payment:
        discount = round(amount * (membership.discount_percent_per_payment / 100), 2)
    discounted_amount = max(0, amount - discount)

    # Sales tax
    tax = 0.0
    sales_tax = sales_tax if sales_tax else 0.0
    if plan.taxable:
        tax = round((sales_tax / 100) * discounted_amount, 2)

    total_amount = round(discounted_amount + tax, 2)

    if plan.billing_type_id == BillingTypeEnum.FREE.value:
        return 0, 0, 0, 0

    return amount, discount, tax, total_amount


def get_renewed_split_payments(mem, new_mem_start_date, old_mem_start_date):

    first_split_payment_date = datetime.strptime(mem.split_payments[0]['payment_date'], '%Y-%m-%d').date()
    new_first_split_payment_date = new_mem_start_date + timedelta(days=(first_split_payment_date - old_mem_start_date).days)
    temp = None
    split_payments = [payment.copy() for payment in mem.split_payments]

    for i, split in enumerate(split_payments):
        if i == 0:
            temp = split['payment_date']
            split['payment_date'] = new_first_split_payment_date.strftime('%Y-%m-%d')
        else:
            diff_days = (datetime.strptime(split['payment_date'], '%Y-%m-%d').date() - datetime.strptime(temp, '%Y-%m-%d').date()).days
            temp = split['payment_date']
            new_split_payment_date = datetime.strptime(split_payments[i-1]['payment_date'], '%Y-%m-%d') + timedelta(days=diff_days)
            split['payment_date'] = new_split_payment_date.strftime('%Y-%m-%d')
    return split_payments


def create_invoice(location_id: int, user_id: int, items: List[InvoiceItem], product_category_type_id: int, description = None) -> Invoice:

    invoice: Invoice = Invoice(location_id, user_id)
    invoice.product_category_type_id = product_category_type_id
    invoice.processed_user_id = g.get("user").id if g.get("user") else 0
    invoice.invoice_items = items
    invoice.description = description
    return invoice


def create_split_payment_invoices(location_id: int, user_id: int, items: List[InvoiceItem], membership: Membership,
                                  is_renewal=False) -> List[Invoice]:
    invoices = []
    has_signup_fee = True if membership.signup_fee and membership.signup_fee > 0 and not is_renewal else False
    # Calculate how many split payment items we have (excluding signup fee)
    split_items = items[1:] if has_signup_fee else items
    for i in range(len(split_items)):
        invoice: Invoice = Invoice(location_id, user_id)
        invoice.product_category_type_id = ProductCategoryTypeEnum.MEMBERSHIP.value
        invoice.processed_user_id = g.get("user").id if g.get("user") else 0
        if i == 0 and has_signup_fee:
            # First invoice: signup fee + first split payment
            invoice.invoice_items = [items[0], split_items[0]]
        else:
            # Subsequent invoices: one split payment each
            invoice.invoice_items = [split_items[i]]
        invoice.description = f"{membership.plan.name} - Split payment {i + 1}" if not is_renewal else f"{membership.plan.name} - Renewal {membership.renewal_count} - Split payment {i + 1}"
        invoices.append(invoice)
    return invoices

def process_payment(invoice: Invoice, payment_method_id: int):

    pay_today_invoice_items = list(filter(lambda item: item.due_date is not None and item.due_date <= utc_now().date(), invoice.invoice_items))

    # consolidate all invoice items of the invoice into one payment
    amount = sum(item.amount for item in pay_today_invoice_items)
    discount = sum(item.discount for item in pay_today_invoice_items)
    tax = sum(item.tax for item in pay_today_invoice_items)
    total_amount = sum(item.total_amount for item in pay_today_invoice_items)
    invoice_item_ids = [item.id for item in pay_today_invoice_items]

    if total_amount > 0:
        payment: MemberPaymentHistory_v2 = MemberPaymentHistory_v2(invoice.location_id, invoice.user_id, payment_method_id)
        payment.amount = amount
        payment.discount = discount
        payment.tax = tax
        payment.total_amount = total_amount
        payment.original_total_amount = total_amount
        payment.invoice = invoice
        payment.description = invoice.description
        payment.invoice_item_ids = invoice_item_ids
        payment.processed_by = g.get('user').id
        payment.save_and_commit()

        return payment
    return None

def update_outstanding_balance_and_invoice_status(location_id: int, user_id: int):

    # Get total payments
    payments_total = MemberPaymentHistory_v2.get_payments_total(location_id, user_id)
    if payments_total["payments_total"] is not None:
        payments_total_remaining = payments_total["payments_total"]
    else:
        payments_total_remaining = 0

    # Get all invoices and filter them as needed
    invoices = Invoice.find_all_invoices_by_member_id(location_id, user_id)
    unvoided_invoices = list(filter(lambda invoice: invoice.invoice_status_type_id != InvoiceStatusTypeEnum.VOID.value, invoices))

    # Calc all credits and add them to payments
    credits_total = sum([invoice.total_amount for invoice in unvoided_invoices if invoice.invoice_type_id == InvoiceTypeEnum.CREDIT_MEMO.value])
    payments_total = payments_total_remaining + credits_total
    payments_total_remaining = payments_total

    # Use debits (invoices), payments and due date to figure out which invoices can be marked as paid / past due
    updated_data = []
    debit_invoices = list(filter(lambda invoice: invoice.invoice_type_id == InvoiceTypeEnum.INVOICE.value, unvoided_invoices))
    sorted_debit_invoices = sorted(debit_invoices, key=lambda invoice: invoice.due_date)
    for invoice in sorted_debit_invoices:
        payments_total_remaining = payments_total_remaining - invoice.total_amount
        if round(payments_total_remaining, 2) >= 0 and invoice.due_date and utc_now().date() >= invoice.due_date:
            invoice.invoice_status_type_id = InvoiceStatusTypeEnum.PAID.value
        else:
            if invoice.due_date and invoice.due_date <= utc_now().date():
                invoice.invoice_status_type_id = InvoiceStatusTypeEnum.PAST_DUE.value
            else:
                invoice.invoice_status_type_id = InvoiceStatusTypeEnum.PENDING.value
        updated_data.append(invoice)

    activity_history = MemberProfile.get_activity_history(location_id, user_id)
    activity_history_df = pd.DataFrame(activity_history)
    if len(activity_history_df) > 0:
        outstanding_balance = sum(activity_history_df[pd.to_datetime(activity_history_df['activity_date']).dt.date <= datetime.strptime(
            to_local_activity_history(utc_now().date()), '%Y-%m-%d').date()][-1:]['balance'])
    else:
        outstanding_balance = 0

    # Update the member_profile.outstanding balance
    if not invoices:
        member_profile = MemberProfile.find_by_id(location_id, user_id)
    else:
        member_profile = invoices[0].member
    member_profile.outstanding_balance = outstanding_balance

    # Update next billing details for split payments after balance calculation
    for membership in member_profile.memberships:
        if membership.split_payments:
            update_next_billing_details(location_id, user_id, membership=membership)

    updated_data.append(member_profile)
    db.session.add_all(updated_data)
    db.session.commit()

def update_next_billing_details(location_id: int, user_id: int, membership: Membership = None):

    # Get all invoices and filter them as needed
    invoices = Invoice.find_all_invoices_by_member_id(location_id, user_id)
    unvoided_invoices = list(filter(lambda invoice: (invoice.membership_id == membership.id) and invoice.invoice_status_type_id != InvoiceStatusTypeEnum.VOID.value, invoices))
    debit_invoices = list(filter(lambda invoice: invoice.invoice_type_id == InvoiceTypeEnum.INVOICE.value, unvoided_invoices))
    unpaid_invoices = list(filter(lambda invoice: invoice.invoice_status_type_id != InvoiceStatusTypeEnum.PAID.value, debit_invoices))

    next_billing_date, next_billing_amount = get_next_billing_details(unpaid_invoices, membership)

    # If next_billing_date > plan_end_date, there is no next billing date and amount
    if next_billing_date and (next_billing_date  >= membership.plan_end_date) and (membership.auto_renewal == False):
        membership.next_billing_date = None
        membership.next_billing_amount = None
    else:
        membership.next_billing_date = next_billing_date
        membership.next_billing_amount = next_billing_amount

    db.session.add(membership)
    db.session.commit()

def create_credit_memo_invoice(invoice_item: InvoiceItem, notes: str = None):

    invoice = Invoice(invoice_item.location_id, invoice_item.user_id)
    invoice.invoice_items = [invoice_item]
    invoice.processed_user_id = g.get("user").id if (g and g.get("user")) else 0
    invoice.notes = notes
    invoice.description = "Credit memo"
    invoice.invoice_type_id = InvoiceTypeEnum.CREDIT_MEMO.value
    invoice.invoice_status_type_id = InvoiceStatusTypeEnum.PAID.value
    return invoice

def create_credit_memo_ledger_entries(invoice: Invoice):

    merchant_entry = _AcctLedger(location_id=invoice.location_id, user_id=None, amount=invoice.total_amount,
                           account_id=CharterOfAccountsTypeEnum.ACCOUNTS_REC.value, credit=True)
    member_entry = _AcctLedger(location_id=invoice.location_id, user_id=invoice.user_id, amount=invoice.total_amount,
                           account_id=invoice.user_id, credit=False)
    db.session.add_all([merchant_entry, member_entry])

def create_invoice_ledger_entries(invoice: Invoice):

    merchant_entry = _AcctLedger(location_id=invoice.location_id, user_id=None, amount=invoice.total_amount,
                           account_id=CharterOfAccountsTypeEnum.ACCOUNTS_REC.value, credit=False)
    member_entry = _AcctLedger(location_id=invoice.location_id, user_id=invoice.user_id, amount=invoice.total_amount,
                           account_id=invoice.user_id, credit=True)
    db.session.add_all([merchant_entry, member_entry])

def create_void_invoice_ledger_entries(invoice: Invoice):

    merchant_entry = _AcctLedger(location_id=invoice.location_id, user_id=None, amount=invoice.total_amount,
                           account_id=CharterOfAccountsTypeEnum.ACCOUNTS_REC.value, credit=True)
    member_entry = _AcctLedger(location_id=invoice.location_id, user_id=invoice.user_id, amount=invoice.total_amount,
                           account_id=invoice.user_id, credit=False)
    db.session.add_all([merchant_entry, member_entry])

def create_payment_ledger_entries(payment: MemberPaymentHistory_v2):

    update_invoice_item_status(payment)

    entries = []
    # Decrease Member balance
    entries.append(_AcctLedger(location_id=payment.location_id, user_id=payment.user_id, amount=payment.total_amount,
                               account_id=payment.user_id, credit=False))

    # Decrease merchant receivable
    entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.total_amount,
                               account_id=CharterOfAccountsTypeEnum.ACCOUNTS_REC.value, credit=True))

    # Increase Merchant Tax Payable
    if payment.tax != 0:
        entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.tax,
                                   account_id=CharterOfAccountsTypeEnum.SALES_TAX.value, credit=True))

    # Increase Merchant Service Revenue (only if not FEES invoice)
    if payment.invoice and payment.invoice.product_category_type_id != ProductCategoryTypeEnum.FEES.value:
        entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.amount,
                                    account_id=CharterOfAccountsTypeEnum.SERVICE_REVENUE.value, credit=True))

    # Increase Merchant Process Receivables
    entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.total_amount,
                               account_id=CharterOfAccountsTypeEnum.MERCHANT_PROCESS_REC.value, credit=False))

    # Only for FEES invoices
    if payment.invoice and payment.invoice.product_category_type_id == ProductCategoryTypeEnum.FEES.value:
        if payment.invoice.invoice_items[0].product_id == PaymentCategoryEnum.LATE_FEE.value:
            entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.total_amount,
                                       account_id=CharterOfAccountsTypeEnum.LATE_FEE_REVENUE.value, credit=True))
        elif payment.invoice.invoice_items[0].product_id == PaymentCategoryEnum.NOSHOW_FEE.value:
            entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.total_amount,
                                       account_id=CharterOfAccountsTypeEnum.NO_SHOW_FEE_REVENUE.value, credit=True))
        elif payment.invoice.invoice_items[0].product_id == PaymentCategoryEnum.CANCELLATION_FEE.value:
            entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.total_amount,
                                       account_id=CharterOfAccountsTypeEnum.CANCEL_FEE_REVENUE.value, credit=True))

    # Increase Merchant Discount
    if payment.discount != 0:
        entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.discount,
                                   account_id=CharterOfAccountsTypeEnum.DISCOUNT_REVENUE.value, credit=False))

    if entries:
        db.session.add_all(entries)

def create_refund_ledger_entries(payment: MemberPaymentHistory_v2):

    entries = []

    if payment.tax != 0:
        entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.tax,
                                   account_id=CharterOfAccountsTypeEnum.SALES_TAX.value, credit=False))

    entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.total_amount,
                               account_id=CharterOfAccountsTypeEnum.MERCHANT_PROCESS_REC.value, credit=True))

    entries.append(_AcctLedger(location_id=payment.location_id, user_id=None, amount=payment.amount,
                               account_id=CharterOfAccountsTypeEnum.SERVICE_REVENUE.value, credit=False))

    if entries:
        db.session.add_all(entries)


def update_invoice_item_status(payment: MemberPaymentHistory_v2):

    if payment.invoice_item_ids:     # Get the list of invoice items for the payment
        invoice_items = InvoiceItem.find_by_ids(payment.location_id, payment.user_id, payment.invoice_item_ids)
        for item in invoice_items:
            # Mark the invoice items as processed
            item.invoice_item_status_type_id = InvoiceItemStatusTypeEnum.PROCESSED.value

def void_invoices_for_cancelled_memberships(mem: Membership, cancel_date):
    mem_invoices: List[Invoice] = Invoice.find_all_invoices_by_membership_id(mem.location_id, mem.user_id, mem.id,
                                                                             pending=True)
    # Void all membership invoices if due_date > cancel_date
    for inv in mem_invoices:
        # If all invoice items are pending or there is only one invoice item --> void the invoice
        if all(item.invoice_item_status_type_id == InvoiceItemStatusTypeEnum.PENDING.value for item in
               inv.invoice_items) or len(inv.invoice_items) == 1:
            if inv.due_date is None or inv.due_date >= cancel_date:
                inv.invoice_status_type_id = InvoiceStatusTypeEnum.VOID.value
                inv.void_datetime = utc_now()
                inv.void_by = 0
        else:
            for item in inv.invoice_items:
                if (item.due_date is None or item.due_date >= cancel_date) and item.invoice_item_status_type_id == InvoiceItemStatusTypeEnum.PENDING.value:
                    item.invoice_item_status_type_id = InvoiceItemStatusTypeEnum.CANCELLED.value

    db.session.commit()
    update_outstanding_balance_and_invoice_status(mem.location_id, mem.user_id)