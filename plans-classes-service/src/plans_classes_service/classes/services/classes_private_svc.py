import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List

from flask import Response

from gmsshared import celery
from gmsshared.src.models.member_class import MemberClass
from gmsshared.src.models.plan import Plan
from gmsshared.src.models.session import Class
from gmsshared.src.models.location import Location
from gmsshared.src.models.membership import Membership
from gmsshared.src.models._ref_plan_type import _RefPlanType
from gmsshared.src.models.class_access_group import ClassAccessGroup
from gmsshared.src.util.validators import to_local
from gmsshared.src.util.enums import (
    ResponseStatusEnum,
    BillingTypeEnum,
    ClassUpdateTypeEnum,
    PlanTypeEnum,
)
from gmsshared.src.util.misc import fill_model
from gmsshared.src.web.fastapi_glue import fastapi_create_response as create_response
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.member_opengym import MemberOpenGym
from gmsshared.src.models.door_access_door import DoorAccessDoor
from gmsshared.src.models import class_access_group
from plans_classes_service.classes.dtos.classes_requests import (
    AccessTimes,
    CreateClassRequest,
    SessionFilter,
    BookClassRequest,
    UpdateClassRequest,
    ClassPath,
    MemberClassFilter,
    UpdateBookingRequest,
    DeleteClassQuery,
    ClassFilter,
    CreateClassAccessGroupRequest,
    UpdateClassAccessGroupRequest
)
from plans_classes_service.classes.dtos.classes_responses import (
    SessionResponse,
    BookingResponse,
    ClassAccessGroupResponse,
    ClassAccessGroupList
)
from plans_classes_service.classes.services.rules import (
    match_rules,
    get_msgs,
    get_action,
    get_changed_attr,
    get_booking_action,
    get_email_action,
)
from plans_classes_service.classes.services.rules_processor import (
    has_member_booked_this_class,
    is_booking_time_valid,
    is_class_full,
    get_eligible_session_pack,
    make_new_booking,
    cancel_group,
    send_emails_group,
    perform_actions,
    _previous_events_of_recurrence,
    get_eligible_memberships,
    is_booking_too_late,
    is_booking_too_early,
    send_emails_pt,
    cancel_pt,
    create_pt_bookings,
    get_eligible_memberships_minus_session_packs,
    cancel_bookings,
    rebook_bookings_pt,
    has_member_checked_in,
    does_member_have_valid_and_active_plans,
    does_member_have_outstanding_balance
)
from gmsshared.src.util.datetime_util import utc_now, to_local_format
from gmsshared.src.util.enums import PlanTypeEnum, RoleEnum, BookingRejectionReasonEnum
from gmsshared.src.util.enums import ClassAccessGroupChangeTypeEnum


def get_class_list(location_id: int, query: SessionFilter) -> Response:
    if query.end_date is None:
        query.end_date = query.start_date + timedelta(days=14)

    sessions: List[Class] = Class.find_by_location_and_date(location_id, start=query.start_date, end=query.end_date)
    if sessions is not None and len(sessions) == 0:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No classes found",
        )
    class_list = []
    for session in sessions:
        events = session.events_list(query.start_date, query.end_date)
        for event in events:
            class_copy = Class()
            fill_model(
                session,
                class_copy,
                exclude=["query", "query_class", "registry", "metadata"],
                ignore_nulls=False,
            )
            class_copy.start_time = event
            class_copy.create_datetime = session.create_datetime
            class_copy.end_time = class_copy.start_time + timedelta(seconds=session.duration)
            class_copy.plans = session.plans.copy()
            class_copy.class_access_groups = session.class_access_groups.copy()
            class_list.append(class_copy)

    attendance_list = MemberClass.find_attendance_by_class_time_and_date_range(
        location_id=location_id, start_time=query.start_date, end_time=query.end_date
    )
    attendance_dict = {}
    for attendance in attendance_list:
        attendance_dict[f"{attendance.class_id}_{attendance.class_time.strftime('%Y-%m-%d %H:%M:%S')}"] = (
            attendance.attendance_count,
            attendance.attendee_list,
        )
        attendance_dict[f"{attendance.class_id}_{attendance.class_time.strftime('%Y-%m-%d %H:%M:%S')}_waitlist"] = (
            attendance.waitlist_count
        )
    for clazz in class_list:
        key = f"{clazz.id}_{clazz.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        waitlist_key = f"{clazz.id}_{clazz.start_time.strftime('%Y-%m-%d %H:%M:%S')}_waitlist"
        clazz.current_attendance = attendance_dict[key][0] if key in attendance_dict else 0
        clazz.attendees = (
            list(set(attendance_dict[key][1].split(",")))
            if key in attendance_dict else []
        )
        clazz.current_waitlist = attendance_dict[waitlist_key] if key in attendance_dict else 0
    class_list.sort(key=lambda x: x.start_time)
    if query.member_id:
        class_list = _get_classes_for_member(location_id, query, class_list)
    class_list = [SessionResponse.model_validate(session).model_dump() for session in class_list]
    classes = {"classes": class_list}

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Classes found",
        data=classes,
    )


def _get_classes_for_member(location_id: int, query: SessionFilter, class_list) -> List[Class]:
    all_classes = []
    memberships = Membership.find_by_member_id(location_id, query.member_id)
    for clazz in class_list:
        if not (clazz.start_time >= query.start_date and clazz.end_time <= query.end_date):
            continue
        if clazz.attendance_cap - clazz.current_attendance <= 0 and not clazz.waitlist:
            clazz.booking_allowed = False
            clazz.booking_allowed_reason_type_id = BookingRejectionReasonEnum.SESSION_ATTENDANCE_CAP_REACHED.value
        elif query.member_id in clazz.attendees:
            clazz.booking_allowed = False
            clazz.booking_allowed_reason_type_id = BookingRejectionReasonEnum.ALREADY_REGISTERED.value
        elif not does_member_have_valid_and_active_plans(memberships, clazz):
            clazz.booking_allowed = False
            clazz.booking_allowed_reason_type_id = BookingRejectionReasonEnum.INVALID_MEMBERSHIP.value
        elif does_member_have_outstanding_balance(memberships[0].member):
            clazz.booking_allowed = False
            clazz.booking_allowed_reason_type_id = BookingRejectionReasonEnum.BLOCKED_BY_BALANCE.value
        elif is_booking_too_early(clazz, clazz.start_time, memberships[0].location, RoleEnum.MEMBER.name):
            clazz.booking_allowed = False
            clazz.booking_allowed_reason_type_id = BookingRejectionReasonEnum.REGISTRATION_NOT_OPENED.value
        elif is_booking_too_late(clazz, clazz.start_time, memberships[0].location):
            clazz.booking_allowed = False
            clazz.booking_allowed_reason_type_id = BookingRejectionReasonEnum.REGISTRATION_CLOSED.value
        else:
            clazz.booking_allowed = True
        all_classes.append(clazz)
    return all_classes

def get_class_data(location_id: int, class_id: int, query: ClassFilter) -> Response:
    class_data = Class.find_by_location_and_class(location_id, class_id)
    if not class_data:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No class found",
        )
    class_response = SessionResponse.model_validate(class_data, from_attributes=True)
    if query:
        members_list = MemberClass.find_by_class_and_class_time(location_id, class_id, query.class_time)
        session_response = class_response.model_dump()
        if members_list:
            session_response["current_waitlist"] = len(list(filter(lambda mem: mem.member_waitlist > 0, members_list)))
            session_response["current_attendance"] = len(members_list) - session_response["current_waitlist"]
            session_response["attendees"] = [member.id for member in members_list]
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Class found",
            data=session_response,
        )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Class found",
        data=class_response.model_dump(),
    )


def create_new_class(location_id: int, body: CreateClassRequest) -> Response:
    session = Class()

    session.class_access_groups = [ClassAccessGroup.find_by_id(location_id, class_access_group) for class_access_group in body.class_access_groups]
    session.plans = [Plan.find_by_id(plan_id) for plan_id in body.plans]

    fill_model(body, session, exclude=["plans", "by_weekday", "class_access_groups"], ignore_nulls=True)

    session.by_weekday = str(body.by_weekday)

    # If PT is False, Create a class directly, If it is True, Class creation is handled in create_pt_bookings post session pack validation
    if body.private_training is False:
        session.save_and_commit()

    # Create bookings automatically for the member
    response = None
    if body.private_training:
        response, member = create_pt_bookings(session, body.member_id)
        # If session is in the past, don't send an email
        if response is None and session.start_time >= utc_now().replace(tzinfo=None):
            response = _send_pt_emails(session, body, member)

    if response is None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CREATED,
            logger_name=__name__,
            message="Successfully created class",
        )
    else:
        return create_response(
            status_code=HTTPStatus.EXPECTATION_FAILED,
            status=ResponseStatusEnum.INTERNAL_ERROR,
            logger_name=__name__,
            message=response,
        )


def _send_pt_emails(session, body: CreateClassRequest, member: MemberProfile) -> Response:
    data = {
        "member_name": f"{member.user.user_profile.first_name} {member.user.user_profile.last_name}",
        "session_start_date": to_local_format(session.start_time, "YYYY-mm-dd"),
        "session_start_time": to_local_format(session.start_time, "HH:MM", am_pm=True),
        "location_name": member.location.name,
        "weekday": session.by_weekday,
        "gym_name": member.location.gym.name,
        "coach_name": f"{session.main_coach.user_profile.first_name} {session.main_coach.user_profile.last_name}",
    }

    if session.recurring:
        celery.send_task("create_recurring_session_pt_email", (member.user.email, data))
    else:
        celery.send_task("create_single_session_pt_email", (member.user.email, data))


def update_class_info(location_id: int, body: UpdateClassRequest) -> Response:
    old = Class.find_by_location_and_class(body.location_id, body.class_id)
    if not old:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No class found",
        )

    new = Class()
    # Can't change private_training to group or vice-versa
    fill_model(body, new, exclude=["plans", "class_access_groups"], ignore_nulls=True)
    # TODO: Make this more efficient by getting all plans and loop through them rather than call each one separately
    new.plans = [Plan.find_by_id(plan_id) for plan_id in body.plans]
    new.class_access_groups = [ClassAccessGroup.find_by_id(location_id, group) for group in body.class_access_groups]
    new.private_training = old.private_training

    rules = match_rules(old, new)
    action, changed_attrs, booking_action, email_action = (
        get_action(rules),
        get_changed_attr(rules),
        get_booking_action(rules),
        get_email_action(rules),
    )

    response = None
    if old.private_training:
        response = send_emails_pt(old, new, email_action, changed_attrs)
    else:
        response = send_emails_group(old, new, email_action, changed_attrs)

    # Only for group sessions
    if booking_action and not old.private_training:
        response = cancel_bookings(old, new, changed_attrs, action)

    if response is None:
        new, old, response = perform_actions(old, new, action, changed_attrs)

    # Only for PT sessions
    if old.private_training:
        response = rebook_bookings_pt(old, new, body)

    if response is None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.UPDATED,
            logger_name=__name__,
            message="Successfully updated class",
        )
    else:
        return create_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            status=ResponseStatusEnum.INTERNAL_ERROR,
            logger_name=__name__,
            message=response,
        )


def delete_class_info(location_id: int, class_id: int, body: DeleteClassQuery) -> Response:
    old = Class.find_by_location_and_class(location_id, class_id)
    if not old:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No class found",
        )
    if not old.recurring:
        # Single event. Just mark it deleted and email members
        old.class_cancellation_time = (
            body.class_cancellation_time if body.class_cancellation_time else datetime.utcnow()
        )
        old.save_and_commit()
        if old.private_training:
            cancel_pt(
                old.location_id,
                old.id,
                body.class_time,
                start_time=body.class_time,
                end_time=None,
            )
        else:
            cancel_group(
                old.location_id,
                old.id,
                body.class_time,
                start_time=body.class_time,
                end_time=None,
            )
    elif old.recurring and body.update_type == ClassUpdateTypeEnum.ONLY_ONE_EVENT.value:
        # Delete a single event in a recurrence. Add an exdate to the occurence and cancel the single event bookings
        old.add_exdate(body.class_time)
        old.save_and_commit()
        if old.private_training:
            cancel_pt(
                old.location_id,
                old.id,
                body.class_time,
                start_time=body.class_time,
                end_time=body.class_time,
            )
        else:
            cancel_group(
                old.location_id,
                old.id,
                body.class_time,
                start_time=body.class_time,
                end_time=body.class_time,
            )
    elif old.recurring and body.update_type == ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value:
        # Stop the old recurrence at the previous event
        old_events = _previous_events_of_recurrence(old, body.class_time)
        if len(old_events) > 0:
            old.recurrence_end_date = old_events[-1]
        else:
            old.class_cancellation_time = (
                body.class_cancellation_time if body.class_cancellation_time else datetime.utcnow()
            )
        old.save_and_commit()
        if old.private_training:
            cancel_pt(
                old.location_id,
                old.id,
                body.class_time,
                start_time=body.class_time,
                end_time=None,
            )
        else:
            cancel_group(
                old.location_id,
                old.id,
                body.class_time,
                start_time=body.class_time,
                end_time=None,
            )
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Successfully deleted class",
    )


def return_class_status(path: ClassPath, body: UpdateClassRequest) -> Response:
    old = Class.find_by_location_and_class(body.location_id, body.class_id)
    if old.private_training:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="",
            data=[],
        )

    new = Class()

    fill_model(body, new, exclude=["plans", "class_access_groups"], ignore_nulls=True)
    # TODO: Make this more efficient by getting all plans and loop through them rather than call each one separately
    new.plans = [Plan.find_by_id(plan_id) for plan_id in body.plans]
    new.class_access_groups = [ClassAccessGroup.find_by_id(location_id=body.location_id, id=cag_id) for cag_id in body.class_access_groups]

    rules = match_rules(old, new)
    msgs = get_msgs(rules)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="",
        data=msgs,
    )


def opengym_checkin(location_id: int, body: BookClassRequest) -> Response:
    memberships = Membership.find_all_memberships_by_member_id(location_id, body.member_id)
    opengym_memberships = []
    opengym_session_packs = []
    for membership in memberships:
        if any(plan_type.id == PlanTypeEnum.OPENGYM.value for plan_type in membership.plan.plan_types):
            if membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value:
                opengym_session_packs.append(membership)
            else:
                opengym_memberships.append(membership)
    member = MemberProfile.find_by_id(location_id, body.member_id)
    if does_member_have_outstanding_balance(member):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.BLOCKED_BY_BALANCE,
            logger_name=__name__,
            message="You cannot sign up at this time due to an outstanding balance. "
                    "Please contact your gym or update your payment method"
        )
    if opengym_memberships:
        new_opengym_checkin = MemberOpenGym(
            location_id=location_id,
            user_id=body.member_id,
            membership_id=opengym_memberships[0].id,
            member_checked_in_time=utc_now(),
        )
        new_opengym_checkin.save_and_commit()
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.SUCCESS,
            logger_name=__name__,
            message="Open Gym Checkin Successful",
        )
    if opengym_session_packs:
        for session_pack in opengym_session_packs:
            if (
                session_pack.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
                and session_pack.sessions_count > 0
            ):
                session_pack.sessions_count -= 1
                session_pack.save_and_commit()
                new_opengym_checkin = MemberOpenGym(
                    location_id=location_id,
                    user_id=body.member_id,
                    membership_id=session_pack.id,
                    member_checked_in_time=utc_now(),
                )
                new_opengym_checkin.save_and_commit()
                return create_response(
                    status_code=HTTPStatus.OK,
                    status=ResponseStatusEnum.SUCCESS,
                    logger_name=__name__,
                    message="Open Gym Checkin Successful",
                )
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.PLAN_DOES_NOT_EXIST,
            logger_name=__name__,
            message="The member has reached the session limit for their session plans.",
        )

    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.PLAN_DOES_NOT_EXIST,
            logger_name=__name__,
            message="Member doesn't have any plan of opengym type",
        )


def create_member_booking(location_id: int, class_id: int, body: BookClassRequest, user_role: str) -> Response:
    clazz = Class.find_by_location_and_class(location_id, class_id)
    member = MemberProfile.find_by_id(location_id, body.member_id)

    if not clazz:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message=f"Session for location {location_id} and session ID {class_id} not found",
        )

    if not member:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Member not found",
        )

    if not body.direct_check_in:
        if not is_booking_time_valid(clazz, body):
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.REGISTRATION_TIME_INVALID,
                logger_name=__name__,
                message="Invalid session time",
            )

        if is_booking_too_late(clazz, body.class_time, member.location):
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.REGISTRATION_CLOSED,
                logger_name=__name__,
                message="Registration for this session is now closed",
            )

        if is_booking_too_early(clazz, body.class_time, member.location, user_role):
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.REGISTRATION_NOT_OPENED,
                logger_name=__name__,
                message="Registration for this session is not open yet",
            )

        if is_class_full(clazz, body) and not clazz.waitlist:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.SESSION_ATTENDANCE_CAP_REACHED,
                logger_name=__name__,
                message="The attendance cap for this session has been reached. \
                                   Please select another session for the client.",
            )

    if member.bookings is not None and has_member_checked_in(member.bookings, clazz, body.class_time):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Member already checked in for this session",
        )

    if member.bookings is not None and has_member_booked_this_class(member.bookings, clazz, body.class_time):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Member already registered for this session",
        )

    eligible_memberships, status = None, None
    if member.memberships is not None:
        eligible_memberships, status = get_eligible_memberships(member.memberships, clazz, body)

    if eligible_memberships is None and status is not None:
        msg = ""
        if status == ResponseStatusEnum.NON_ACTIVE_MEMBERSHIP:
            msg = (
                "The client's membership is not currently active due to it being frozen, cancelled, or not yet started. \
             Please update the membership status or wait until the start date to book this session."
            )
        elif status == ResponseStatusEnum.INVALID_MEMBERSHIP:
            msg = "The client’s membership doesn’t have access to book this session"
        elif status == ResponseStatusEnum.PERIOD_LIMIT_REACHED:
            msg = "The client has reached their limit of sessions allowed for the current period"
        return create_response(
            status_code=HTTPStatus.OK,
            status=status,
            logger_name=__name__,
            message=msg,
        )

    if does_member_have_outstanding_balance(member):
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.BLOCKED_BY_BALANCE,
            logger_name=__name__,
            message="You cannot sign up at this time due to an outstanding balance. "
                    "Please contact your gym or update your payment method"
        )

    eligible_session_pack, eligible_memberships_no_session_packs, status = (
        None,
        None,
        None,
    )
    if len(eligible_memberships) > 0:
        eligible_session_pack = get_eligible_session_pack(eligible_memberships, clazz)
        eligible_memberships_no_session_packs = get_eligible_memberships_minus_session_packs(eligible_memberships)

    # Use the first of the eligible membership. If session limits exceeded then use the first session pack membership
    is_limit_reached = is_class_full(clazz, body)
    if len(eligible_memberships_no_session_packs) > 0:
        booking = make_new_booking(
            member,
            clazz,
            eligible_memberships_no_session_packs[0],
            body.class_time,
            is_limit_reached,
            direct_check_in=body.direct_check_in,
        )
        if body.direct_check_in:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.SUCCESS,
                logger_name=__name__,
                data={"booking_id": booking.id},
                message="Check-in successful!",
            )

        if booking.member_waitlist > 0:
            try:
                data = {
                    "member_name": f"{booking.member.user.user_profile.first_name} {booking.member.user.user_profile.last_name}",
                    "location_name": booking.location.name,
                    "location_email": booking.location.cs_email,
                    "location_phone": booking.location.cs_phone,
                    "session_name": booking.clazz.name,
                    "gym_name": booking.member.location.gym.name,
                }
                celery.send_task("add_to_waitlist_email", (booking.member.user.email, data))
            except Exception:
                pass
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.SUCCESS,
                logger_name=__name__,
                data={"booking_id": booking.id},
                message="Client successfully added to the waitlist! \
                           They will see their session in their mobile app.",
            )
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.SUCCESS,
            logger_name=__name__,
            data={"booking_id": booking.id},
            message="Booking successful! \
                           The client will see their session in their mobile app.",
        )
    elif eligible_session_pack is not None:
        booking = make_new_booking(
            member,
            clazz,
            eligible_session_pack,
            body.class_time,
            is_limit_reached,
            direct_check_in=body.direct_check_in,
        )
        if booking.member_waitlist > 0:
            try:
                data = {
                    "member_name": f"{booking.member.user.user_profile.first_name} {booking.member.user.user_profile.last_name}",
                    "location_name": booking.location.name,
                    "location_email": booking.location.cs_email,
                    "location_phone": booking.location.cs_phone,
                    "session_name": booking.clazz.name,
                    "gym_name": booking.member.location.gym.name,
                }
                celery.send_task("add_to_waitlist_email", (booking.member.user.email, data))
            except Exception:
                pass
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.SUCCESS,
                logger_name=__name__,
                data={"booking_id": booking.id},
                message="Client successfully added to the waitlist! \
                           They will see their session in their mobile app.",
            )
        if body.direct_check_in:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.SUCCESS,
                logger_name=__name__,
                data={"booking_id": booking.id},
                message="Check-in successful!",
            )

        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.SUCCESS,
            logger_name=__name__,
            data={"booking_id": booking.id},
            message=f"Session successfully booked for the client. \
                                       They have {booking.membership.sessions_count} remaining",
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.TOTAL_LIMIT_REACHED,
            logger_name=__name__,
            message="The client has reached their limit of sessions or session packs",
        )


def delete_member_booking(location_id: int, class_id: int, booking_id: int, user_id: int) -> Response:
    booking = MemberClass.find_by_class_and_booking_id(
        location_id=location_id, class_id=class_id, booking_id=booking_id
    )
    if not booking:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Booking not found for member",
        )

    if booking.member_cancelled_time is not None:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.INVALID_REQUEST,
            logger_name=__name__,
            message="Booking previously cancelled",
        )

    booking.member_cancelled_time = datetime.utcnow()
    booking.cancelled_by = user_id
    # Checking if cancelled booking is of a registered member or a waitlist member
    if not booking.member_waitlist:
        next_booking = MemberClass.fetch_member_from_waitlist(location_id, class_id, booking.class_time)
        if next_booking:
            next_booking.member_waitlist = 0
            next_booking.save_and_commit()
            try:
                data = {
                    "member_name": f"{next_booking.member.user.user_profile.first_name} {next_booking.member.user.user_profile.last_name}",
                    "location_name": next_booking.location.name,
                    "location_email": next_booking.location.cs_email,
                    "location_phone": next_booking.location.cs_phone,
                    "date_time": to_local_format(next_booking.clazz.start_time, "YYYY-mm-dd HH:MM", am_pm=True),
                    "session_name": next_booking.clazz.name,
                    "gym_name": next_booking.member.location.gym.name,
                }
                celery.send_task(
                    "promote_waitlist_to_registered_email",
                    (next_booking.member.user.email, data),
                )
            except Exception:
                pass

    member_in_waitlist = True if booking.member_waitlist else False
    booking.member_waitlist = 0
    location = Location.find_by_id(location_id)

    if (
        booking.membership is not None
        and booking.membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
        and booking.no_show_credited is False
    ):
        booking.membership.sessions_count = booking.membership.sessions_count + 1
        booking.no_show_credited = True
    booking.save_and_commit()

    if member_in_waitlist:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.SUCCESS,
            logger_name=__name__,
            message="Client successfully removed from the waitlist! They will see this change reflected in their mobile app.",
        )
    else:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.SUCCESS,
            logger_name=__name__,
            message="Booking cancelled",
        )


def get_booking(location_id: int, class_id: int, booking_id: int) -> Response:
    booking = MemberClass.find_by_id(location_id, class_id, booking_id)
    if not booking:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No booking found",
        )

    booking_response = BookingResponse.model_validate(booking, from_attributes=True)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Bookings found",
        data=booking_response.model_dump(),
    )


def get_booking_info(location_id: int, class_id: int, query: MemberClassFilter) -> Response:
    member_classes_list = []
    if query.member_id:
        member_classes_list = MemberClass.find_by_class_and_member_id(location_id, class_id, query.member_id)
    elif query.class_time:
        member_classes_list = MemberClass.find_by_class_and_class_time(
            location_id, class_id, query.class_time, cancelled=True
        )
    else:
        member_classes_list = MemberClass.find_all(location_id, class_id)

    if len(member_classes_list) == 0:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No bookings found",
        )
    bookings_list = []
    for booking in member_classes_list:
        booking_response = BookingResponse.model_validate(booking, from_attributes=True).model_dump()
        booking_response["first_name"] = booking.member.user.user_profile.first_name
        booking_response["last_name"] = booking.member.user.user_profile.last_name
        bookings_list.append(booking_response)
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Bookings found",
        data=bookings_list,
    )


def get_booking_info_for_location(location_id: int, query: MemberClassFilter) -> Response:
    member_classes_list = MemberClass.find_by_date_range_and_member_id(
        location_id, query.member_id, query.start_date, query.end_date
    )

    if len(member_classes_list) == 0:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No bookings found",
        )
    bookings_list = []
    for booking in member_classes_list:
        booking_response = BookingResponse.model_validate(booking, from_attributes=True).model_dump()
        booking_response["first_name"] = booking.member.user.user_profile.first_name
        booking_response["last_name"] = booking.member.user.user_profile.last_name
        bookings_list.append(booking_response)

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Bookings found",
        data=bookings_list,
    )


def update_booking(location_id: int, class_id: int, booking_id: int, body: UpdateBookingRequest) -> Response:
    booking = MemberClass.find_by_id(location_id, class_id, booking_id)
    if not booking:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="No booking found",
        )

    # Probably a delete operation from mobile. Not ideal way to delete but only clean way to pass a payload (cancel_reason) while deleting an event
    if body.member_cancelled_time is not None and body.cancel_reason is not None:
        if (
            booking.membership is not None
            and booking.membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
            and not booking.no_show_credited
        ):
            booking.membership.sessions_count = booking.membership.sessions_count + 1
            booking.no_show_credited = True


        if booking.clazz.recurring:
            # Add the classtime to exdates of the session to remove it from the web calendar
            booking.clazz.add_exdate(booking.class_time)
        else:
            # Delete the session
            booking.clazz.class_cancellation_time = body.member_cancelled_time

        booking.member_cancelled_time = body.member_cancelled_time
        booking.cancel_reason = body.cancel_reason
        booking.member_checked_in_time = None

        data = {
            "member_name": f"{booking.member.user.user_profile.first_name} {booking.member.user.user_profile.last_name}",
            "session_start_date": to_local_format(booking.clazz.start_time, "YYYY-mm-dd"),
            "session_start_time": to_local_format(booking.clazz.start_time, "HH:MM", am_pm=True),
            "location_name": booking.member.location.name,
            "cancel_reason": body.cancel_reason,
            "gym_name": booking.member.location.gym.name,
            "coach_name": f"{booking.clazz.main_coach.user_profile.first_name} {booking.clazz.main_coach.user_profile.last_name}",
        }
        try:
            celery.send_task(
                "session_cancellation_pt_coach_email",
                (booking.clazz.main_coach.email, data),
            )

        except Exception:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.INTERNAL_ERROR,
                logger_name=__name__,
                message="Error sending email to coach",
            )

    # Removing member from the checked-in list
    elif body.member_checked_in_time is None and booking.member_checked_in_time is not None:
        booking.member_checked_in_time = None

    else:
        # Most likely updating via web
        if booking.member_checked_in_time is not None:
            return create_response(
                status_code=HTTPStatus.OK,
                status=ResponseStatusEnum.UPDATED,
                logger_name=__name__,
                message="Member has already checked-in",
            )
        booking.member_checked_in_time = body.member_checked_in_time
        booking.member_cancelled_time = None
        booking.cancel_reason = None
        booking.member_waitlist = 0

    booking.save_and_commit()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Booking updated",
    )

def create_new_class_access_group(location_id: int, body: CreateClassAccessGroupRequest):
    cag = ClassAccessGroup.find_door_by_location_and_name(location_id, body.name)
    if cag:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.CONFLICT,
            logger_name=__name__,
            message="Session access already exists. Please modify your entry to ensure uniqueness",
        )
    class_access_group = ClassAccessGroup(location_id=location_id, name=body.name, active=body.active)
    class_access_group.class_access_group_formats = [_RefPlanType.find_by_id(plan_type_id) for plan_type_id in body.plan_formats]
    class_access_group.class_access_group_doors = [DoorAccessDoor.find_by_id(location_id, door_id) for door_id in body.doors]
    class_access_group.door_access_access_times_flag = body.door_access_access_times_flag

    if class_access_group.door_access_access_times_flag:
        class_access_group.door_access_access_times = [AccessTimes.model_validate(act).model_dump() for act in body.door_access_access_times]
    class_access_group.save_and_commit()

    if class_access_group.location.door_access and class_access_group.class_access_group_doors:
        celery.send_task("update_group", (location_id, class_access_group.location.door_access_vendor_id, class_access_group.id, None,))

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.CREATED,
        logger_name=__name__,
        message="Class Access Created",
    )

def _get_class_access_group_diff(cag: ClassAccessGroup, body: UpdateClassAccessGroupRequest):
    diff = []

    # Check for change in doors
    existing_doors = {door.id for door in cag.class_access_group_doors}
    new_doors = set(body.doors or [])
    if (existing_doors != new_doors) or bool(cag.active ^ body.active):
        diff.append(ClassAccessGroupChangeTypeEnum.DOORS.value)

    # Check for change in access times
    door_access_times_flag_changed = bool(cag.door_access_access_times_flag ^ body.door_access_access_times_flag)
    existing_access_times = (
        json.loads(json.dumps(cag.door_access_access_times))
        if cag.door_access_access_times else []
    )
    new_access_times = [
        AccessTimes.model_validate(act).model_dump()
        for act in (body.door_access_access_times or [])
    ]
    sort_key = lambda x: (x['weekday'], x['start_time'], x['end_time'])
    access_times_changed = (
        sorted(existing_access_times, key=sort_key)
        != sorted(new_access_times, key=sort_key)
        if new_access_times else False
    )
    if door_access_times_flag_changed or access_times_changed:
        diff.append(ClassAccessGroupChangeTypeEnum.ACCESS_TIMES.value)

    # Check for change in cag properties
    if cag.name != body.name:
        diff.append(ClassAccessGroupChangeTypeEnum.GROUP.value)

    return diff


def update_class_access_group(location_id: int, body: UpdateClassAccessGroupRequest):
    class_access_group = ClassAccessGroup.find_by_id(location_id, body.id)
    location = class_access_group.location
    if not class_access_group:
        return create_response(
            status_code=HTTPStatus.NOT_FOUND,
            status=ResponseStatusEnum.NOT_FOUND,
            logger_name=__name__,
            message="Class Access Not Found",
        )

    cag_diff = _get_class_access_group_diff(class_access_group, body)

    fill_model(body, class_access_group, exclude=["plans", "classes", "class_access_group_formats"], ignore_nulls=False)
    class_access_group.class_access_group_formats = [_RefPlanType.find_by_id(plan_type_id) for plan_type_id in body.plan_formats]
    class_access_group.class_access_group_doors = [DoorAccessDoor.find_by_id(location_id, door_id) for door_id in body.doors]
    class_access_group.door_access_access_times_flag = body.door_access_access_times_flag

    if class_access_group.door_access_access_times_flag:
        class_access_group.door_access_access_times = [AccessTimes.model_validate(act).model_dump() for act in body.door_access_access_times]
    class_access_group.save_and_commit()


    if class_access_group.location.door_access:
        celery.send_task("update_group", (location_id, location.door_access_vendor_id, class_access_group.id, cag_diff,))

    if class_access_group.location.door_access:
        celery.send_task("update_members_to_group", (location_id, [class_access_group.id], None,))

    class_access_group_resp = ClassAccessGroupResponse.model_validate(class_access_group, from_attributes=True).model_dump()
    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.UPDATED,
        logger_name=__name__,
        message="Session access updated",
        data=class_access_group_resp
    )

def get_class_access_groups_info(location_id: int):
    class_access_groups = ClassAccessGroup.find_by_location_id(location_id)
    if not class_access_groups:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Class access not found",
        )

    class_access_groups_info = [ClassAccessGroupResponse.model_validate(class_access, from_attributes=True).model_dump() for class_access in class_access_groups]
    for cag in class_access_groups_info:  # FE needed an empty array and not null
        if not cag["door_access_access_times"]:
            cag["door_access_access_times"] = []

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Class accesses found",
        data = class_access_groups_info,
    )

def get_class_access_group_info(location_id: int, class_access_group_id: int):
    class_access_group = ClassAccessGroup.find_by_id(location_id, class_access_group_id)
    if not class_access_group:
        return create_response(
            status_code=HTTPStatus.OK,
            status=ResponseStatusEnum.FOUND,
            logger_name=__name__,
            message="Class access not found",
        )

    # Get classes > today() and return the id and name
    valid_classes = []
    for clazz in class_access_group.classes:
        if clazz.recurring:
            if clazz.recurrence_end_date is None or clazz.recurrence_end_date.date() > utc_now().date():
                valid_classes.append(clazz)
        elif clazz.start_time.date() >= utc_now().date():
            valid_classes.append(clazz)
    class_access_group.classes = valid_classes
    cag_info = ClassAccessGroupResponse.model_validate(class_access_group, from_attributes=True).model_dump()
    classes = [{"id": clazz.id, "name": clazz.name} for clazz in valid_classes]
    cag_info["classes"] = classes

    if not cag_info["door_access_access_times"]:
        cag_info["door_access_access_times"] = []

    return create_response(
        status_code=HTTPStatus.OK,
        status=ResponseStatusEnum.FOUND,
        logger_name=__name__,
        message="Class access found",
        data = cag_info,
)