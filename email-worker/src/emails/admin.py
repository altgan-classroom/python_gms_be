from emails.utils import get_template, send_email
from gmsshared.src.config import get_config
from .. import worker_service


@worker_service.task(name="owner_onboard_admin_email", task_acks_late=True, ignore_result=True)
def owner_onboard_admin_email(to_email, data):
    body = get_template("admin/owner_onboard_admin_email.j2", data)
    subject = "Your Upcoming Personal Training Session Schedule!"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)
