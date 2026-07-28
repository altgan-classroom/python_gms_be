from emails.utils import get_template, send_email
from gmsshared.src.config import get_config
from .. import worker_service


@worker_service.task(name="booking_cancellation_email", task_acks_late=True, ignore_result=True)
def booking_cancellation_email(to_email, data):
    subject = "Session Cancelled"
    body = get_template("session/group/cancel_session_group.j2", data)
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="add_to_waitlist_email", task_acks_late=True, ignore_result=True)
def add_to_waitlist_email(to_email, data):
    subject = f"You’re On The Waitlist for {data.get('session_name')}"
    body = get_template("session/group/added_to_waitlist.j2", data)
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="promote_waitlist_to_registered_email", task_acks_late=True, ignore_result=True)
def promote_waitlist_to_registered_email(to_email, data):
    subject = f"You’re Now Booked For {data.get('session_name')}!"
    body = get_template("session/group/promote_waitlist_to_registered.j2", data)
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="updated_session_email", task_acks_late=True, ignore_result=True)
def updated_session_email(to_email, data):
    body = get_template("session/group/updated_session_group.j2", data)
    subject = f"Important: Updated Booked Session at {data.get('location_name')}"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="create_single_session_pt_email", task_acks_late=True, ignore_result=True)
def create_single_session_pt_email(to_email, data):
    body = get_template("session/pt/create_single_session_pt.j2", data)
    subject = f"Your Upcoming Personal Training Session At {data['location_name']}"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="create_recurring_session_pt_email", task_acks_late=True, ignore_result=True)
def create_recurring_session_pt_email(to_email, data):
    body = get_template("session/pt/create_recurring_session_pt.j2", data)
    subject = f"Your Upcoming Personal Training Sessions At {data['location_name']}"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="updated_single_session_pt_email", task_acks_late=True, ignore_result=True)
def updated_single_session_pt_email(to_email, data):
    body = get_template("session/pt/updated_single_session_pt.j2", data)
    subject = f"Update To Your Upcoming Personal Training Session At {data['location_name']}"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="updated_recurring_session_pt_email", task_acks_late=True, ignore_result=True)
def updated_recurring_session_pt_email(to_email, data):
    body = get_template("session/pt/updated_recurring_session_pt.j2", data)
    subject = f"Update To Your Upcoming Personal Training Sessions At {data['location_name']}"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="session_cancellation_pt_coach_email", task_acks_late=True, ignore_result=True)
def session_cancellation_pt_coach_email(to_email, data):
    body = get_template("session/pt/cancel_session_pt_coach.j2", data)
    subject = f"Your Upcoming Personal Training Session With {data['member_name']} Was Canceled!"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="session_cancellation_pt_member_email", task_acks_late=True, ignore_result=True)
def session_cancellation_pt_member_email(to_email, data):
    body = get_template("session/pt/cancel_session_pt_member.j2", data)
    subject = f"{data['location_name']} Session Cancellation"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)
