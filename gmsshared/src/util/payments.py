from datetime import datetime, timedelta
from typing import List, Any

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import Timestamp, DateOffset

from gmsshared import db
from gmsshared.src.util.enums import DurationTypeEnum, BillingTypeEnum
from gmsshared.src.util.misc import fill_model
from gmsshared.src.models.location import Location
from gmsshared.src.models.plan import Plan
from gmsshared.src.models.member_payment_schedule_temp import MemberPaymentScheduleTemp
from gmsshared.src.models.member_payment_schedule import MemberPaymentSchedule
from gmsshared.src.models.member_payment_history import MemberPaymentHistory
from gmsshared.src.models.membership import Membership
from gmsshared.src.config import get_config
from gmsshared.src.util.datetime_util import utc_now


def calc_dates(membership: Membership, plan: Plan, first_payment_date=None, start_date=None, end_date=None) -> Any:
    if start_date is None:
        plan_start_date = pd.Timestamp(membership.plan_start_date)
    else:
        plan_start_date = pd.Timestamp(start_date)

    if end_date is None:
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

    # Session packs don't expire, so set end_date to 5 years into the future
    if end_date is None or plan.billing_type_id in [BillingTypeEnum.SESSION_PACKS.value]:
        end_date = plan_start_date + relativedelta(years=5)

    dates = []
    if plan.billing_type_id in [BillingTypeEnum.RECURRING.value]:
        # For recurring, check for first_of_month, else use days or months as the recurrence interval type (D or M)
        if plan.first_of_month:
            dates = pd.date_range(plan_start_date, end_date, freq='MS').array
            dates = dates.insert(0, plan_start_date)
        elif plan.recurring_duration_type_id in [DurationTypeEnum.MONTHS.value, DurationTypeEnum.MONTH.value]:
            dates = pd.date_range(plan_start_date, end_date, freq=DateOffset(months=1), inclusive="left").array
        elif plan.recurring_duration_type_id in [DurationTypeEnum.WEEKS.value, DurationTypeEnum.WEEK.value]:
            dates = pd.date_range(plan_start_date, end_date, freq=f"{int(plan.recurring_interval)}W").array
        elif plan.recurring_duration_type_id in [DurationTypeEnum.DAYS.value, DurationTypeEnum.DAY.value]:
            dates = pd.date_range(plan_start_date, end_date, freq=f"{int(plan.recurring_interval)}D").array
    else:
        # For non-recurring just use one date
        dates = pd.date_range(plan_start_date, plan_start_date, 1).array

    dates = [Timestamp(d) for d in dates]
    only_signup = False
    if first_payment_date is not None:
        today, first_payment_date = Timestamp(datetime.today().utcnow().date()), Timestamp(first_payment_date)

        # Signup fee always due today
        dates[0] = Timestamp(dates[0].replace(year=today.year, month=today.month, day=today.day))

        if first_payment_date > today:
            dates.append(first_payment_date)
            only_signup = True

    dates = [d.date() if isinstance(d, Timestamp) else d for d in dates]
    return sorted(set(dates), key=Timestamp.date), end_date.date() if isinstance(end_date, Timestamp) else end_date, only_signup

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

def prorate_payment(sdate, amount):
    # Only frontend proration - meaning, only prorate for the beginning of the membership
    sdate = Timestamp(sdate)
    days_in_this_month = sdate.daysinmonth
    remaining_days_in_month = days_in_this_month - sdate.day
    price_per_day = amount / days_in_this_month
    return round(price_per_day * remaining_days_in_month, 2)

def calc_payments(membership, plan, dates, only_signup, sales_tax, renewal_count=None, first_discount=True, signup=True, is_from_dea=False,last_payment_number=0):
    payment_schedule = []

    if plan.billing_type_id == BillingTypeEnum.PAID_IN_FULL.value:
        plan_amount = plan.paid_in_full_price
    elif plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        plan_amount = plan.class_or_session_pack_price
    elif plan.billing_type_id == BillingTypeEnum.RECURRING.value:
        plan_amount = plan.recurring_amount
    else:
        plan_amount = 0.0

    for i, sdate in enumerate(dates):

        signup_fee = 0.0
        # Signup fee - Note: For renewal: set membership.signup_fee = 0.0 and only_signup = False before invoking this fn
        if i == 0 and signup:
            signup_fee = round(membership.signup_fee, 2)

        if i == 0 and only_signup and signup:
            amount = 0.0
        else:
            amount = plan_amount

        # First of month
        if (plan.billing_type_id in [BillingTypeEnum.RECURRING.value] and plan.first_of_month and
                (i == 1 if only_signup else i == 0) and sdate.day != 1):
            amount = prorate_payment(sdate, amount)

        # Discount
        discount = 0.0
        if membership.apply_discount_to_all_payments and i != 0:
            discount = calc_discount(membership, amount)
        elif (i == 1 if only_signup else i == 0) and first_discount:
            discount = calc_discount(membership, amount)
        discounted_amount = amount - discount + signup_fee

        # Sales tax
        tax = 0.0
        if plan.taxable:
            tax = round((sales_tax / 100) * discounted_amount, 2)

        total_amount = round(discounted_amount + tax, 2)

        if renewal_count is not None and renewal_count != 0:
            schedule = MemberPaymentSchedule(membership.location_id, membership.user_id)
            fill_model(membership, schedule, exclude=['signup_fee', 'id'], ignore_nulls=False)
            schedule.membership_id = membership.id
            schedule.renewal_count = renewal_count
        else:
            schedule = MemberPaymentScheduleTemp(membership.location_id, membership.user_id)
            fill_model(membership, schedule, exclude=[], ignore_nulls=False)

        if is_from_dea:
            last_payment_number=last_payment_number+1
            schedule.payment_number, schedule.amount, schedule.signup_fee, schedule.tax = last_payment_number, amount, signup_fee, tax
            schedule.discount, schedule.total_amount, schedule.scheduled_date = discount, total_amount, sdate
            payment_schedule.append(schedule)
            if plan.billing_type_id == BillingTypeEnum.FREE.value:
                break
            continue

        schedule.payment_number, schedule.amount, schedule.signup_fee, schedule.tax = i + 1, amount, signup_fee, tax
        schedule.discount, schedule.total_amount, schedule.scheduled_date = discount, total_amount, sdate
        payment_schedule.append(schedule)

        if plan.billing_type_id == BillingTypeEnum.FREE.value:
            break

    return payment_schedule

def calc_split_payments(membership, plan, sales_tax, split_payments):
    payment_schedule = []
    payment_number = 1
    for payment in membership.split_payments:
        payment['payment_date'] = payment['payment_date'].strftime('%Y-%m-%d')  # Convert to string

    # Create payment 1 with signup fee due today if first payment > today else include it in first payment
    if membership.first_payment_date > utc_now().date():
        schedule = MemberPaymentScheduleTemp(membership.location_id, membership.user_id)
        fill_model(membership, schedule, exclude=[], ignore_nulls=False)
        schedule.amount = 0
        schedule.discount = 0
        schedule.signup_fee = round(membership.signup_fee, 2)
        schedule.scheduled_date = utc_now().date()
        schedule.payment_number = payment_number
        payment_number += 1
        schedule.total_amount = schedule.signup_fee
        payment_schedule.append(schedule)

    for i, split in enumerate(split_payments):
        if split.payment_amount != 0:
            plan_amount = split.payment_amount
            signup_fee = 0

            if i==0 and membership.first_payment_date <= utc_now().date():
                signup_fee = round(membership.signup_fee, 2)

            # Discount
            discount = 0.0
            if i == 0 or membership.apply_discount_to_all_payments:
                discount = calc_discount(membership, plan_amount)

            discounted_amount = plan_amount - discount + signup_fee

            # Sales tax
            tax = 0.0
            if plan.taxable:
                tax = round((sales_tax / 100) * discounted_amount, 2)

            total_amount = round(discounted_amount + tax, 2)

            schedule = MemberPaymentScheduleTemp(membership.location_id, membership.user_id)
            fill_model(membership, schedule, exclude=[], ignore_nulls=False)
            schedule.payment_number = payment_number
            payment_number += 1
            schedule.split_payments = membership.split_payments
            schedule.tax = tax
            schedule.signup_fee = signup_fee
            schedule.amount =  split.payment_amount
            schedule.discount = discount
            schedule.total_amount = total_amount
            schedule.scheduled_date = split.payment_date
            payment_schedule.append(schedule)
    return payment_schedule


def renew_split_payments(membership, plan, sales_tax, split_payments, renewal_count , new_start_date):
    renewal_payment_schedule = []

    for payment in split_payments:
        payment['payment_date'] = datetime.strptime(payment['payment_date'], '%Y-%m-%d').date()

    recent_start_date = get_nth_renewal_start_date(membership, plan, renewal_count)
    temp = recent_start_date

    for i, split in enumerate(split_payments):
        if i == 0:
            # First payment date: calculate difference from recent_start_date and apply it to new_start_date
            days_diff = (split['payment_date'] - recent_start_date).days
            temp = split['payment_date']
            split['payment_date'] = new_start_date + timedelta(days=days_diff)
            current_payment_date = split['payment_date']  # Set current payment date for further calculations
        else:
            # For subsequent payments, calculate based on the difference from the previous payment date
            days_diff = (split['payment_date'] - temp).days
            temp = split['payment_date']
            current_payment_date += timedelta(days=days_diff)  # Move forward by the days_diff
            split['payment_date'] = current_payment_date
        # Discount
        discount = 0.0
        amount = split['payment_amount']
        if membership.apply_discount_to_all_payments and i != 0:
            discount = calc_discount(membership, amount)
        discounted_amount = amount - discount

        # Sales tax
        tax = 0.0
        if plan.taxable:
            tax = round((sales_tax / 100) * discounted_amount, 2)

        total_amount = round(discounted_amount + tax, 2)

        schedule = MemberPaymentSchedule(membership.location_id, membership.user_id)
        fill_model(membership, schedule, exclude=['signup_fee', 'id'], ignore_nulls=False)
        schedule.payment_number = i + 1
        schedule.membership_id = membership.id
        schedule.renewal_count = renewal_count
        schedule.split_payments = split_payments
        schedule.tax = tax
        schedule.amount = split['payment_amount']
        schedule.discount = discount
        schedule.total_amount = total_amount
        schedule.scheduled_date = split['payment_date']
        renewal_payment_schedule.append(schedule)

    for payment in split_payments:
        payment['payment_date'] = payment['payment_date'].strftime('%Y-%m-%d')

    return split_payments, renewal_payment_schedule


def get_next_billing_date(mem: Membership, plan: Plan, freeze_from, freeze_to):
    if plan.recurring_duration_type_id in [DurationTypeEnum.DAY.value, DurationTypeEnum.DAYS.value]:
        recurring_days = plan.recurring_interval
    elif plan.recurring_duration_type_id in [DurationTypeEnum.WEEK.value, DurationTypeEnum.WEEKS.value]:
        recurring_days = plan.recurring_interval * 7
    elif plan.recurring_duration_type_id in [DurationTypeEnum.MONTH.value, DurationTypeEnum.MONTHS.value]:
        next_scheduled_date = freeze_to + relativedelta(months=plan.recurring_interval)
        recurring_days = (next_scheduled_date - freeze_to).days
    elif plan.recurring_duration_type_id in [DurationTypeEnum.YEAR.value, DurationTypeEnum.YEARS.value]:
        next_scheduled_date = freeze_to + relativedelta(years=plan.recurring_interval)
        recurring_days = (next_scheduled_date - freeze_to).days

    last_payment = MemberPaymentHistory.find_last_payment_processed(
        location_id=mem.location_id,
        membership_id=mem.id,
        user_id=mem.user_id
    )
    if not last_payment:
        return freeze_to + timedelta(days=1)
        
    previous_paid_date = last_payment.processed_date.date()
    # If freeze_from is in past and if it is before the previous payment, account for inactive days in past billing
    if freeze_from < utc_now().date() and freeze_from < previous_paid_date:
        inactive_days_in_past_billing = abs(freeze_from - previous_paid_date).days
        next_scheduled_date = freeze_to + timedelta(days=inactive_days_in_past_billing) + timedelta(recurring_days+1)
        return next_scheduled_date

    # else go with recurring days - active days in current billing cycle
    active_days = (freeze_from - previous_paid_date).days
    remaining_days = recurring_days - (active_days % recurring_days)
    next_scheduled_date = freeze_to + timedelta(days=remaining_days+1)
    return next_scheduled_date


def regenerate_schedule_for_recurring(mem: Membership, next_billing_date: Any) -> None:
    dates, end_date, _ = calc_dates(mem, mem.plan, first_payment_date=None, start_date=next_billing_date, end_date=mem.plan_end_date)
    sales_tax = mem.location.sales_tax if mem.location.sales_tax else 0.0
    first_discount = False
    if mem.apply_discount_to_all_payments:
        first_discount = True
    else:
        if next_payment_schedule := MemberPaymentSchedule.find_by_membership_id(mem.location_id, mem.user_id, mem.id):
            if next_payment_schedule[0].discount > 0.0:
                first_discount = True
    new_payment_schedule = calc_payments(mem, mem.plan, dates, False, sales_tax, first_discount=first_discount, signup=False)
    new_schedule = []
    for i, ps in enumerate(new_payment_schedule):
        new_ps = MemberPaymentSchedule(location_id=mem.location_id, user_id=mem.user_id)
        fill_model(ps, new_ps, exclude=['id'], ignore_nulls=True)
        new_ps.membership_id = mem.id
        new_schedule.append(new_ps)
    Membership.delete_upcoming_payments(mem.location_id, mem.user_id, mem.id)
    db.session.add_all(new_schedule)
    db.session.commit()
    mem.update_final_payment_date(0 if mem.renewal_count is None else mem.renewal_count)

def get_headers(key: str = None) -> dict:
    header = {'APIKEY': get_config().PAYRIX_APIKEY,
            'Content-Type': 'application/json'}
    if key:
        header['REQUEST-TOKEN'] = key
    return header