import copy
from datetime import datetime, timedelta, tzinfo
from typing import List

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrulestr
from gmsshared.src.web.fastapi_glue import g

from gmsshared.src.models.member_class import MemberClass
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.session import Class
from gmsshared.src.models.location import Location
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.util.enums import ClassUpdateTypeEnum

from gmsshared import celery, db
from gmsshared.src.models.membership import Membership
from plans_classes_service.classes.dtos.classes_requests import (
    BookClassRequest,
    UpdateClassRequest,
)
from gmsshared.src.util.enums import (
    BillingTypeEnum,
    ClassFrequencyEnum,
    SessionChangeEmailTypeEnum,
    SessionActionTypeEnum,
    SessionChangeTypeEnum,
    DurationTypeEnum,
    MembershipStatusEnum,
    ResponseStatusEnum,
    RoleEnum,
)
from gmsshared.src.util.misc import fill_model, copy_model_to_model
from gmsshared.src.util.validators import (
    to_local,
    to_utc,
    to_local_for_return_datetime_obj,
)
from gmsshared.src.util.datetime_util import to_local_format
from gmsshared.src.util.enums import RegistrationTimesType
from gmsshared.src.util.validators import normalize_local_times


def _get_time(class_time, time_type, time_value, class_create_time):
    # To calculate the start and end time registration limits
    if time_value is None:
        time_value = 0
    if time_type == RegistrationTimesType.AT_START_TIME.value:
        return class_time
    elif time_type == RegistrationTimesType.IMMEDIATELY.value:
        return class_create_time
    time_offset = {
        RegistrationTimesType.MINUTES_BEFORE.value: timedelta(minutes=time_value),
        RegistrationTimesType.HOURS_BEFORE.value: timedelta(hours=time_value),
        RegistrationTimesType.DAYS_BEFORE.value: timedelta(days=time_value),
        RegistrationTimesType.WEEKS_BEFORE.value: timedelta(weeks=time_value),
    }
    return class_time - time_offset.get(time_type, timedelta())


def is_booking_too_late(clazz: Class, start_time, location: Location) -> bool:
    # Too late
    registration_end_time = _get_time(
        start_time,
        location.registration_end_time_type_id,
        location.registration_end_time_value,
        clazz.create_datetime,
    ) if location.registration_end_time_type_id is not None else start_time
    if registration_end_time < datetime.utcnow():
        return True
    return False


def is_booking_too_early(clazz: Class, start_time, location: Location, user_role: str) -> bool:
    # Too early
    if user_role == RoleEnum.MEMBER.name:
        registration_start_time = _get_time(
            start_time,
            location.registration_start_time_type_id,
            location.registration_start_time_value,
            clazz.create_datetime,
        ) if location.registration_start_time_type_id is not None else clazz.create_datetime
        if registration_start_time > datetime.utcnow():
            return True
    return False


def is_booking_time_valid(clazz: Class, body: BookClassRequest):
    # Check if the class time is a valid event for the class
    if clazz.recurring and not clazz.is_class_valid(body.class_time):
        return False
    elif not clazz.recurring and clazz.start_time != body.class_time:
        return False

    return True


def has_member_booked_this_class(member_bookings: List[MemberClass], clazz: Class, class_time: datetime):
    for booking in member_bookings:
        if (
            (booking.class_id == clazz.id)
            and (booking.class_time == class_time)
            and (booking.member_cancelled_time is None)
        ):
            return True
    return False


def does_member_have_outstanding_balance(member):
    user = g.get("user")
    if member.location.is_dea and member.location.block_registrations_on_balance_due and user.role_type_id in [
        RoleEnum.MEMBER.value, RoleEnum.KIOSK.value] and round(member.outstanding_balance, 2) > 0:
        return True
    return False


def has_member_checked_in(member_bookings: List[MemberClass], clazz: Class, class_time: datetime):
    for booking in member_bookings:
        if (
            (booking.class_id == clazz.id)
            and (booking.class_time == class_time)
            and (booking.member_cancelled_time is None)
            and (booking.member_checked_in_time is not None)
        ):
            return True
    return False


def does_member_have_valid_and_active_plans(memberships: List[Membership], clazz: Class):
    class_plans = []
    local_temp_class_time = to_local_for_return_datetime_obj(clazz.start_time)
    active_member_plans = [
        membership.plan
        for membership in memberships
        if membership.membership_status_type_id in [MembershipStatusEnum.ACTIVE.value, MembershipStatusEnum.NOT_STARTED.value]
        and (membership.plan_start_date <= local_temp_class_time.date() <= membership.plan_end_date or membership.auto_renewal)
    ]
    if memberships and memberships[0].location.class_access_group:
        for cag in clazz.class_access_groups:
            if cag.active:
                class_plans.extend(cag.plans)
    else:
        class_plans = clazz.plans
    intersect = set(active_member_plans).intersection(class_plans)
    if len(intersect) == 0:
        return False
    return True


def get_eligible_memberships(memberships: List[Membership], clazz: Class, body: BookClassRequest):
    # Filter out the cancelled and frozen memberships
    active_memberships = [membership for membership in memberships if membership.membership_status_type_id in (MembershipStatusEnum.ACTIVE.value,MembershipStatusEnum.NOT_STARTED.value)]

    temp_class_time = copy.deepcopy(body.class_time)
    local_temp_class_time = to_local_for_return_datetime_obj(temp_class_time)

    # Make sure they are active, today's date > plan_start_date
    active_memberships = [
        membership for membership in active_memberships if membership.plan_start_date <= local_temp_class_time.date()
    ]
    if len(active_memberships) == 0:
        return None, ResponseStatusEnum.NON_ACTIVE_MEMBERSHIP

    # Does the membership have an eligible plan for the session
    if active_memberships[0].location.class_access_group:
        active_cags = [cag for cag in clazz.class_access_groups if cag.active == 1]
        class_plans = list({plan.id for group in active_cags for plan in group.plans})
    else:
        class_plans = [plan.id for plan in clazz.plans]
    eligible_memberships = []
    for mem in active_memberships:
        # Make sure the class time is not beyond the plan_end_date of the membership and not auto-renew. Auto-renew plans are eligible
        is_valid_plan = mem.plan.id in class_plans
        is_before_end_date = local_temp_class_time.date() <= mem.plan_end_date
        has_auto_renewal = mem.auto_renewal
        if is_valid_plan and (is_before_end_date or has_auto_renewal):
            eligible_memberships.append(mem)

    if len(eligible_memberships) == 0:
        return None, ResponseStatusEnum.INVALID_MEMBERSHIP

    # Let's check for session limits
    eligible_memberships_2 = []
    for mem in eligible_memberships:
        # force_register flag used to allow webapp to register members even if session registration limits are exceeded.
        # when it's true it skips the have_session_limits_exhausted check.
        if not body.force_register and have_session_limits_exhausted(mem, body):
            pass
        else:
            eligible_memberships_2.append(mem)

    if len(eligible_memberships_2) == 0:
        return None, ResponseStatusEnum.PERIOD_LIMIT_REACHED

    # Sort the memberships to allow registrations on unlimited plans first, next comes the session limit plans
    eligible_memberships_2.sort(key=lambda mem: mem.plan.unlimited, reverse=True)
    return eligible_memberships_2, None

def _get_valid_booking_count(bookings, most_recent_interval_start, most_recent_interval_end):
    booking_count = 0

    for booking in bookings:

        local_date = to_local_for_return_datetime_obj(copy.deepcopy(booking.class_time)).date()

        if booking.member_cancelled_time is not None:
            continue

        # Skip booking if it is outside the interval
        if not (most_recent_interval_start <= local_date <= most_recent_interval_end):
            continue
        # Count the booking if it inside the interval and in future
        elif booking.class_time > utc_now().replace(tzinfo=None):
            booking_count += 1
            continue

        if booking.location.no_show_credit:
            if booking.member_checked_in_time is None:
                continue

        # 1) member_cancelled_time is None
        # 2) local_date is within [most_recent_interval_start, most_recent_interval_end]
        # 3) if no_show_credit is True, member_checked_in_time is not None
        booking_count += 1

    return booking_count


def have_session_limits_exhausted(membership: Membership, body: BookClassRequest) -> bool:
    temp_class_time = copy.deepcopy(body.class_time)
    local_temp_class_time = to_local_for_return_datetime_obj(temp_class_time)

    all_memberships = [membership]
    current = membership.previous_membership
    while current:
        all_memberships.append(current)
        current = current.previous_membership

    duration_of_membership = (local_temp_class_time.date() - all_memberships[-1].plan_start_date).days
    multiplier = 1
    if membership.plan.sessions_limit_duration_type_id in (
        DurationTypeEnum.WEEK.value,
        DurationTypeEnum.WEEKS.value,
    ):
        multiplier = 7
    elif membership.plan.sessions_limit_duration_type_id in (
        DurationTypeEnum.MONTH.value,
        DurationTypeEnum.MONTHS.value,
    ):
        multiplier = 30.5  # Average of all months in a leap year
    elif membership.plan.sessions_limit_duration_type_id in (
        DurationTypeEnum.YEAR.value,
        DurationTypeEnum.YEARS.value,
    ):
        multiplier = 365
    bookings = [booking for membership in all_memberships for booking in membership.bookings]
    # Calculates session limits based on weekly (Mon-Sun) limits when apply_weekly_registration_limits is true.
    if membership.plan.apply_weekly_registration_limits:
        # Changed Monday to Sunday session limit format
        days_to_monday = (local_temp_class_time.date().weekday() - 0) % 7
        most_recent_interval_start = local_temp_class_time.date() - timedelta(days=days_to_monday)
        most_recent_interval_end = most_recent_interval_start + timedelta(days=6)
        booking_count = _get_valid_booking_count(bookings, most_recent_interval_start, most_recent_interval_end)
        if booking_count >= membership.plan.weekly_limit_times:
            return True

    elif membership.plan.sessions_limit_every is not None:
        interval_length = multiplier * membership.plan.sessions_limit_every
        num_of_intervals = duration_of_membership // interval_length
        most_recent_interval_start = all_memberships[-1].plan_start_date + relativedelta(
            days=(num_of_intervals * interval_length)
        )
        most_recent_interval_end = most_recent_interval_start + relativedelta(days=interval_length)
        booking_count = _get_valid_booking_count(bookings, most_recent_interval_start, most_recent_interval_end)
        if booking_count >= membership.plan.sessions_limit_times:
            return True
    return False


def get_eligible_memberships_minus_session_packs(memberships: List[Membership]):
    eligible_memberships_no_session_packs = []
    for membership in memberships:
        if membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
            continue
        else:
            eligible_memberships_no_session_packs.append(membership)
    return eligible_memberships_no_session_packs


def get_eligible_session_pack(memberships: List[Membership], clazz: Class):
    if len(memberships) == 0:
        return None

    if memberships[0].location.class_access_group:
        active_cags = [cag for cag in clazz.class_access_groups if cag.active == 1]
        class_plans = list({plan for group in active_cags for plan in group.plans})
    else:
        class_plans = [plan for plan in clazz.plans]

    session_pack_plans = [
        plan.id for plan in class_plans if plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
    ]
    session_pack_memberships = [
        membership
        for membership in memberships
        if (
            membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
            and membership.membership_status_type_id == MembershipStatusEnum.ACTIVE.value
            and membership.plan.id in session_pack_plans
        )
    ]

    if len(session_pack_memberships) == 0:
        return None

    for session_pack_membership in session_pack_memberships:
        if session_pack_membership.sessions_count > 0:
            memberships.remove(session_pack_membership)
            return session_pack_membership

    return None


def is_class_full(clazz: Class, body: BookClassRequest):
    bookings: List[MemberClass] = MemberClass.find_by_class_and_class_time(clazz.location_id, clazz.id, body.class_time)
    active_bookings = [booking for booking in bookings if booking.member_cancelled_time is None]
    if len(active_bookings) >= clazz.attendance_cap:
        return True
    return False


def make_new_booking(
    member: MemberProfile,
    clazz: Class,
    eligible_membership: Membership,
    class_time: datetime,
    is_limit_reached: bool = False,
    direct_check_in: bool = False,
):
    current_waitlist = 0
    if is_limit_reached and clazz.waitlist and not direct_check_in:
        current_waitlist = MemberClass.get_current_waitlist(member.location_id, clazz.id, class_time)
    new_booking = MemberClass(
        location_id=member.location_id,
        class_id=clazz.id,
        membership_id=eligible_membership.id,
        user_id=member.user_id,
        class_time=class_time,
        member_waitlist=current_waitlist + 1 if is_limit_reached and not direct_check_in else 0,
    )
    if direct_check_in:
        new_booking.member_registered_time = utc_now()
        new_booking.member_checked_in_time = utc_now()
        new_booking.member_waitlist = 0
    new_booking.save_and_commit()
    if eligible_membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        eligible_membership.sessions_count = eligible_membership.sessions_count - 1
        eligible_membership.save_and_commit()
    return new_booking


def cancel_bookings(old: Class, new: Class, changed_attrs: List, action: int):
    bookings = []
    try:
        if (
            "recurrence_end_date",
            SessionChangeTypeEnum.SUBTRACT.value,
        ) in changed_attrs:
            bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
                old.location_id,
                old.id,
                new.recurrence_end_date,
                datetime.strptime("2030-01-01", "%Y-%m-%d"),
            )
            process_cancellations(bookings)

        if ("start_time", SessionChangeTypeEnum.UPDATE.value) in changed_attrs or (
            "end_time",
            SessionChangeTypeEnum.UPDATE.value,
        ) in changed_attrs:
            if old.recurring:
                end_time = (
                    old.recurrence_end_date
                    if old.recurrence_end_date is not None
                    else datetime.strptime("2030-01-01", "%Y-%m-%d")
                )
            else:
                end_time = new.start_time.date()
            bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
                old.location_id, old.id, new.start_time.date(), end_time
            )
            process_cancellations(bookings)

        if ("by_weekday", SessionChangeTypeEnum.SUBTRACT.value) in changed_attrs:
            classes_list = _get_by_weekday_classes(old, new)
            if len(classes_list) > 0:
                bookings: List[MemberClass] = MemberClass.find_by_class_and_class_list(
                    old.location_id, old.id, classes_list
                )
            process_cancellations(bookings)

        if ("start_date", SessionChangeTypeEnum.UPDATE.value) in changed_attrs:
            bookings: List[MemberClass] = MemberClass.find_by_class_and_class_time(
                old.location_id, old.id, old.start_time
            )
            process_cancellations(bookings)

        if ("waitlist", SessionChangeTypeEnum.UPDATE.value) in changed_attrs:
            if old.waitlist is True and new.waitlist is False:
                if action == SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value:
                    if old.recurring:
                        end_time = (
                            old.recurrence_end_date
                            if old.recurrence_end_date is not None
                            else datetime.strptime("2030-01-01", "%Y-%m-%d")
                        )
                    else:
                        end_time = new.start_time.date()
                    bookings: List[MemberClass] = MemberClass.find_waitlisted_members_by_class_and_date_range(
                        old.location_id, old.id, new.start_time.date(), end_time
                    )
                elif action in (
                    SessionActionTypeEnum.UPDATE.value,
                    SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
                ):
                    bookings: List[MemberClass] = MemberClass.find_waitlisted_bookings_by_class_and_time(
                        old.location_id, old.id, new.start_time
                    )
                process_cancellations(bookings)

    except Exception:
        return "Failed to cancel bookings"

    return None


def rebook_bookings_pt(old: Class, new: Class, body: UpdateClassRequest):
    bookings = []

    try:
        if body.update_type == ClassUpdateTypeEnum.ONLY_ONE_EVENT.value:
            if old.recurring is False:
                # Remove old booking(s) for this single class and rebook just
                bookings = MemberClass.find_all(old.location_id, old.id)
                for booking in bookings:
                    booking.member_cancelled_time = utc_now()
                MemberClass.bulk_update(bookings)
                create_pt_bookings(old, body.member_id)
            else:
                # Remove the one booking for the event that was split from the recurrence
                bookings = MemberClass.find_by_class_and_class_time(
                    old.location_id,
                    old.id,
                    datetime.combine(body.start_time.date(), old.start_time.time()),
                    cancelled=False,
                )
                for booking in bookings:
                    booking.member_cancelled_time = utc_now()
                MemberClass.bulk_update(bookings)
                create_pt_bookings(new, body.member_id)
        elif body.update_type == ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value:
            # Remove all old bookings and recreate for the new class
            # Sometimes, there is no new class (in the case where the event being edited is the first one in a recurrence)
            new_session = new if new.id is not None else old
            bookings = MemberClass.find_by_class_and_date_range(
                old.location_id,
                old.id,
                body.end_time,
                datetime.strptime("2030-01-01", "%Y-%m-%d"),
            )
            for booking in bookings:
                booking.member_cancelled_time = utc_now()
            MemberClass.bulk_update(bookings)
            create_pt_bookings(new_session, body.member_id)

    except Exception:
        return "Failed to rebook bookings"

    return None


def rebook_bookings_group(old: Class, new: Class, action):
    bookings = []
    try:
        # Get the bookings for this single session and update the id to the new id
        if action == SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value:
            bookings = MemberClass.find_by_class_and_class_time(
                old.location_id, old.id, new.start_time, cancelled=False
            )
        elif action == SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value:
            include_waitlist = False if new.waitlist is False else True
            bookings = MemberClass.find_by_class_and_date_range(
                old.location_id,
                old.id,
                new.start_time,
                end_time=datetime(2030, 1, 1),
                include_waitlist=include_waitlist,
            )
        for booking in bookings:
            booking.class_id = new.id
        MemberClass.bulk_update(bookings)
    except Exception:
        raise "Failed to rebook group bookings"


# TODO: Consolidate all cancellations (PT and Group) into one method
def process_cancellations(bookings: List[MemberClass]):
    for booking in bookings:
        booking.member_cancelled_time = datetime.utcnow()
        if booking.membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
            booking.membership.sessions_count = booking.membership.sessions_count + 1
            booking.no_show_credited = True
    MemberClass.bulk_update(bookings)


def _get_by_weekday_classes(old: Class, new: Class):
    # Figure which weekdays we need to filter out
    weekday = ",".join([x for x in old.by_weekday.split(",") if x not in new.by_weekday.split(",")])

    # TODO: Have all this logic in one place. Make the session.events_list method able to handle this and clean this up
    # Convert UTC times to local
    start_time = datetime.combine(new.start_time.date(), old.start_time.time())
    end_time = (
        old.recurrence_end_date if old.recurrence_end_date is not None else old.start_time + relativedelta(months=3)
    )
    start, end = (
        datetime.strptime(to_local(start_time), "%Y-%m-%d %H:%M"),
        datetime.strptime(to_local(end_time), "%Y-%m-%d %H:%M"),
    )
    rule = f"FREQ={ClassFrequencyEnum(new.frequency).name};BYDAY={weekday}"
    rr = rrulestr(rule, dtstart=start)
    rr._until = end
    class_list = [clazz for clazz in list(rr)]
    # Make sure we exclude the dates from exdate
    exdates = old.exdate.split(",") if old.exdate is not None else []
    local_exdates = [to_local(datetime.combine(datetime.strptime(y, "%Y-%m-%d"), old.sess_start_time)) for y in exdates]
    local_exdates = [datetime.strptime(x, "%Y-%m-%d %H:%M") for x in local_exdates]

    # We are done generating recurrence events, convert local back to UTC
    event_list = sorted(list(set(class_list) - set(local_exdates)))
    event_list = [to_utc(event).strftime("%Y-%m-%d %H:%M:%S") for event in event_list]
    return tuple(event_list)


# TODO: Consolidate all email sending (PT and Group) into one method
def send_emails_group(old, new, email_action, changed_attrs):
    bookings = []
    try:
        if (
            "recurrence_end_date",
            SessionChangeTypeEnum.SUBTRACT.value,
        ) in changed_attrs:
            bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
                old.location_id,
                old.id,
                new.recurrence_end_date,
                datetime.strptime("2030-01-01", "%Y-%m-%d"),
            )
            process_emails_group(old, new, email_action, bookings)

        if ("start_time", SessionChangeTypeEnum.UPDATE.value) in changed_attrs or (
            "end_time",
            SessionChangeTypeEnum.UPDATE.value,
        ) in changed_attrs:
            if old.recurring:
                end_time = (
                    old.recurrence_end_date
                    if old.recurrence_end_date is not None
                    else datetime.strptime("2030-01-01", "%Y-%m-%d")
                )
            else:
                end_time = new.start_time.date()
            bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
                old.location_id, old.id, new.start_time.date(), end_time
            )
            process_emails_group(old, new, email_action, bookings)

        if ("by_weekday", SessionChangeTypeEnum.SUBTRACT.value) in changed_attrs:
            classes_list = _get_by_weekday_classes(old, new)
            if len(classes_list) > 0:
                bookings: List[MemberClass] = MemberClass.find_by_class_and_class_list(
                    old.location_id, old.id, classes_list
                )
            process_emails_group(old, new, email_action, bookings)

        if ("start_date", SessionChangeTypeEnum.UPDATE.value) in changed_attrs:
            bookings: List[MemberClass] = MemberClass.find_by_class_and_class_time(
                old.location_id, old.id, old.start_time
            )
            process_emails_group(old, new, email_action, bookings)
    except Exception:
        return "Failed to send emails"

    return None


def send_emails_pt(old, new, email_action, changed_attrs):
    bookings = []
    try:
        if (
            "recurrence_end_date",
            SessionChangeTypeEnum.SUBTRACT.value,
        ) in changed_attrs:
            bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
                old.location_id,
                old.id,
                new.recurrence_end_date,
                datetime.strptime("2030-01-01", "%Y-%m-%d"),
            )
            process_edit_emails_pt(old, new, bookings)

        if ("start_time", SessionChangeTypeEnum.UPDATE.value) in changed_attrs or (
            "end_time",
            SessionChangeTypeEnum.UPDATE.value,
        ) in changed_attrs:
            if old.recurring:
                end_time = (
                    old.recurrence_end_date
                    if old.recurrence_end_date is not None
                    else datetime.strptime("2030-01-01", "%Y-%m-%d")
                )
            else:
                end_time = new.start_time.date()
            bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
                old.location_id, old.id, new.start_time.date(), end_time
            )
            process_edit_emails_pt(old, new, bookings)

        if ("by_weekday", SessionChangeTypeEnum.SUBTRACT.value) in changed_attrs:
            classes_list = _get_by_weekday_classes(old, new)
            if len(classes_list) > 0:
                bookings: List[MemberClass] = MemberClass.find_by_class_and_class_list(
                    old.location_id, old.id, classes_list
                )
            process_edit_emails_pt(old, new, bookings)

        if ("start_date", SessionChangeTypeEnum.UPDATE.value) in changed_attrs:
            bookings: List[MemberClass] = MemberClass.find_by_class_and_class_time(
                old.location_id, old.id, old.start_time
            )
            process_edit_emails_pt(old, new, bookings)
    except Exception:
        return "Failed to send emails"

    return None


# TODO: Consolidate all email sending (PT and Group) into one method
def process_emails_group(old: Class, new: Class, email_action: int, bookings: List[MemberClass]):
    for booking in bookings:
        # If email sent earlier for this booking, don't spam them again
        if booking.cancel_rebook_email_time is not None:
            continue
        if email_action == SessionChangeEmailTypeEnum.REBOOK.value:
            data = {
                "member_name": f"{booking.member.user.user_profile.first_name} {booking.member.user.user_profile.last_name}",
                "class_time": to_local_format(booking.class_time, "YYYY-mm-dd"),
                "session_name": booking.clazz.name,
                "session_start_time": to_local_format(old.start_time, "HH:MM", True),
                "new_class_time": to_local_format(new.start_time, "YYYY-mm-dd"),
                "new_session_start_time": to_local_format(new.start_time, "HH:MM", True),
                "gym_name": booking.location.gym.name,
                "location_name": booking.location.name,
                "location_email": booking.location.cs_email,
                "location_phone": booking.location.cs_phone,
            }
            celery.send_task("updated_session_email", (booking.member.user.email, data))
        # If session is in the past, don't send an email
        elif email_action == SessionChangeEmailTypeEnum.CANCEL.value and booking.class_time >= utc_now().replace(
            tzinfo=None
        ):
            data = {
                "member_name": f"{booking.member.user.user_profile.first_name} {booking.member.user.user_profile.last_name}",
                "session_name": booking.clazz.name,
                "class_time": to_local_format(booking.class_time, "YYYY-mm-dd HH:MM", True),
                "location_name": booking.location.name,
                "gym_name": booking.location.gym.name,
                "location_email": booking.location.cs_email,
                "location_phone": booking.location.cs_phone,
            }
            celery.send_task("booking_cancellation_email", (booking.member.user.email, data))
        booking.cancel_rebook_email_time = datetime.utcnow()
    MemberClass.bulk_update(bookings)


def process_edit_emails_pt(old: Class, new: Class, bookings: List[MemberClass]):
    first_booking, email_type = None, None

    # Figure out which email template
    if old.recurring:
        email_type = "updated_recurring_session_pt_email"
    else:
        email_type = "updated_single_session_pt_email"

    for booking in bookings:
        # If email sent earlier for this booking, don't spam them again
        if booking.cancel_rebook_email_time is not None:
            continue
        booking.cancel_rebook_email_time = utc_now()

    first_booking = bookings[0] if len(bookings) != 0 else None
    # If class start time is in the past, don't send an email
    if first_booking is not None and new.start_time >= utc_now().replace(tzinfo=None):
        data = {
            "member_name": f"{first_booking.member.user.user_profile.first_name} {first_booking.member.user.user_profile.last_name}",
            "class_time": to_local_format(first_booking.class_time, "YYYY-mm-dd HH:MM", True),
            "session_start_date": to_local_format(first_booking.clazz.start_time, "YYYY-mm-dd"),
            "session_start_time": to_local_format(first_booking.clazz.start_time, "HH:MM", am_pm=True),
            "new_session_start_date": to_local_format(new.start_time, "YYYY-mm-dd"),
            "new_session_start_time": to_local_format(new.start_time, "HH:MM", am_pm=True),
            "new_recurrence_end_date": to_local_format(new.recurrence_end_date, "YYYY-mm-dd")
            if new.recurrence_end_date is not None
            else None,
            "location_name": first_booking.member.location.name,
            "weekday": new.by_weekday,
            "gym_name": first_booking.member.location.gym.name,
            "session_name": first_booking.clazz.name,
            "coach_name": f"{first_booking.clazz.main_coach.user_profile.first_name} {first_booking.clazz.main_coach.user_profile.last_name}",
        }

        # We just want to send one email for all the future booking cancellations
        celery.send_task(email_type, (first_booking.member.user.email, data))
    MemberClass.bulk_update(bookings)


def process_cancel_emails_pt(location_id: int, bookings: List[MemberClass]):
    first_booking, email_type = None, None

    # Figure out which email template
    email_type = "session_cancellation_pt_member_email"
    location = Location.find_by_id(location_id)
    for booking in bookings:
        booking.member_cancelled_time = utc_now()
        # If email sent earlier for this booking, don't spam them again
        if booking.membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
            booking.membership.sessions_count = booking.membership.sessions_count + 1
            booking.no_show_credited = True
        if booking.cancel_rebook_email_time is not None:
            continue
        booking.cancel_rebook_email_time = utc_now()

    first_booking = bookings[0] if len(bookings) != 0 else None
    # If session is in the past, don't send an email
    if first_booking is not None and first_booking.clazz.start_time >= utc_now().replace(tzinfo=None):
        data = {
            "member_name": f"{first_booking.member.user.user_profile.first_name} {first_booking.member.user.user_profile.last_name}",
            "class_time": to_local_format(first_booking.class_time, "YYYY-mm-dd HH:MM", True),
            "location_name": first_booking.member.location.name,
            "gym_name": first_booking.member.location.gym.name,
            "session_name": first_booking.clazz.name,
            "coach_name": f"{first_booking.clazz.main_coach.user_profile.first_name} {first_booking.clazz.main_coach.user_profile.last_name}",
        }

        # We just want to send one email for all the future booking cancellations
        celery.send_task(email_type, (first_booking.member.user.email, data))
    MemberClass.bulk_update(bookings)


def perform_actions(old, new, action, changed_attrs):
    try:
        if action == SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value:
            (
                new.recurring,
                new.frequency,
                new.by_weekday,
                new.recurrence_end_date,
                new.exdate,
            ) = (
                False,
                None,
                None,
                None,
                None,
            )
            new.start_time = datetime.combine(new.start_time.date(), new.sess_start_time)
            new.end_time = new.start_time + timedelta(seconds=new.duration)
            new.recurring = False
            new.save_and_commit()
            old.add_exdate(new.start_time)
            old.save_and_commit()
            # Special case if changed_attrs are coach or assistant coach
            # TODO: Move this special case a level above and change the rule processing so that we know if rebooking or cancel
            if not old.private_training and (x in ["main_coach_id", "waitlist"] for x in [y[0] for y in changed_attrs]):
                rebook_bookings_group(old, new, action)
        elif action == SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value:
            # Change all events going forward of a recurring session
            # Make adjustments to figure out the right recurrence_end_date due to date changes
            if (
                datetime.strptime(
                    to_local(datetime.combine(new.start_time.date(), old.start_time.time())),
                    "%Y-%m-%d %H:%M",
                ).date()
                < datetime.strptime(to_local(new.start_time), "%Y-%m-%d %H:%M").date()
            ):
                start = new.start_time + relativedelta(days=+1)
            elif (
                datetime.strptime(
                    to_local(datetime.combine(new.start_time.date(), old.start_time.time())),
                    "%Y-%m-%d %H:%M",
                ).date()
                > datetime.strptime(to_local(new.start_time), "%Y-%m-%d %H:%M").date()
            ):
                start = new.start_time + relativedelta(days=-1)
            else:
                start = new.start_time
            old_events = _previous_events_of_recurrence(old, start)
            if len(old_events) > 0:
                # Only create new event if it is not the only event being modified
                old.recurrence_end_date = old_events[-1]
                new.exdate = old.exdate
                new.save_and_commit()
            else:
                copy_model_to_model(new, old, exclude=["plans", "id", "class_access_groups"])
                old.plans = new.plans
                old.class_access_groups = new.class_access_groups

            old.save_and_commit()
            # Special case if changed_attrs are coach or assistant coach
            # TODO: Move this special case a level above and change the rule processing so that we know if rebooking or cancel
            if (
                not old.private_training
                and new.id
                and (x in ["main_coach_id", "waitlist"] for x in [y[0] for y in changed_attrs])
            ):
                rebook_bookings_group(old, new if new else old, action)
        elif action == SessionActionTypeEnum.UPDATE.value:
            # Can't change from group to private_training or vice-versa
            fill_model(new, old, exclude=["plans", "private_training", "class_access_groups"], ignore_nulls=False)
            old.plans = new.plans
            old.class_access_groups = new.class_access_groups
            old.save_and_commit()
    except Exception:
        return new, old, "Failed to process updates"

    return new, old, None


def _previous_events_of_recurrence(old, start):
    start_time = datetime.combine(start.date(), old.start_time.time())
    old_events = old.events_list((start_time - timedelta(weeks=1)), start_time)
    events_to_remove = []
    for event in old_events:
        if start_time <= normalize_local_times(event, start_time):
            events_to_remove.append(event)
    old_events = [event for event in old_events if event not in events_to_remove]
    return old_events


# TODO: Consolidate all cancellations (PT and Group) into one method
def cancel_group(
    location_id: int,
    class_id: int,
    class_time: datetime,
    start_time: datetime = None,
    end_time: datetime = None,
):
    if end_time is None:
        end_time = datetime.strptime("2030-01-01", "%Y-%m-%d")
    bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
        location_id, class_id, start_time=start_time, end_time=end_time
    )
    location = Location.find_by_id(location_id)
    for booking in bookings:
        if (
            booking.membership is not None
            and booking.membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
        ):
            booking.membership.sessions_count = booking.membership.sessions_count + 1
            booking.no_show_credited = True
        booking.member_cancelled_time = utc_now()
    MemberClass.bulk_update(bookings)

    process_emails_group(None, None, SessionChangeEmailTypeEnum.CANCEL.value, bookings)


# TODO: Consolidate all cancellations (PT and Group) into one method
def cancel_pt(
    location_id: int,
    class_id: int,
    class_time: datetime,
    start_time: datetime = None,
    end_time: datetime = None,
):
    if end_time is None:
        end_time = datetime.strptime("2030-01-01", "%Y-%m-%d")
    bookings: List[MemberClass] = MemberClass.find_by_class_and_date_range(
        location_id, class_id, start_time=start_time, end_time=end_time
    )
    process_cancel_emails_pt(location_id, bookings)


def create_pt_bookings(session: Class, member_id: int):
    member = MemberProfile.find_by_id(session.location_id, member_id)

    # Get the membership corresponding to the plan selected for session
    selected_membership = None
    for membership in member.memberships:
        if membership.plan_id == session.plans[0].id and membership.membership_status_type_id == MembershipStatusEnum.ACTIVE.value:
            selected_membership = membership
            break
    if session.recurring:
        end_time = (
            datetime.combine(session.recurrence_end_date, session.end_time.time())
            if session.recurrence_end_date is not None
            else datetime.combine(selected_membership.plan_end_date, session.end_time.time())
        )
    else:
        end_time = session.end_time

    # Get list of events for this session to auto-book member until recurrence_end_date or plan_end_date if infinite recurrence
    events = session.events_list(session.start_time, end_time)

    if selected_membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
        available_sessions_count = selected_membership.sessions_count
        if len(events) > available_sessions_count:
            no_of_events = (
                len(events) if not session.recurring or session.recurrence_end_date is not None else "Unlimited"
            )
            member_name = f"{member.user.user_profile.first_name} {member.user.user_profile.last_name}"
            sessions_needed = no_of_events - available_sessions_count if no_of_events != "Unlimited" else "Unlimited"
            return (
                f"""The number of Private Training sessions exceeds the session credits <strong>{member_name}</strong> has on their account<br/><br/>
            Private Training sessions: <strong>{no_of_events}</strong> Sessions Remaining: <strong>{available_sessions_count}</strong><br/><br/>
            Decrease the number of recurrences for the Private Training session or add <strong>
            {sessions_needed}</strong> session pack{"" if sessions_needed == 1 else "s"}  to <strong>{member_name}'s</strong> account""",
                None,
            )

    bookings = []
    # Only create a class if above criteria is a pass
    session.save_and_commit()

    for event in events:
        new_booking = MemberClass(
            location_id=session.location_id,
            class_id=session.id,
            membership_id=selected_membership.id,
            user_id=member.user_id,
            class_time=event,
            member_waitlist=False,
        )
        new_booking.member_registered_time = utc_now()
        bookings.append(new_booking)

    try:
        db.session.add_all(bookings)
        db.session.commit()
        if selected_membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
            selected_membership.sessions_count -= len(bookings)
            selected_membership.save_and_commit()
    except Exception:
        return "Error creating bookings", None

    return None, member
