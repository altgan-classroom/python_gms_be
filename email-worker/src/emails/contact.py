from emails.utils import get_template, send_email
from gmsshared.src.config import get_config
from .. import worker_service


@worker_service.task(name="owner_verification_email", task_acks_late=True, ignore_result=True)
def owner_verification_email(to_email, data):
    body = get_template("contact/owner_verification.j2", data)
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, "Verify your email", body)


@worker_service.task(name="staff_account_verification_email", task_acks_late=True, ignore_result=True)
def staff_account_verification_email(to_email, data):
    body = get_template("contact/staff_account_verification.j2", data)
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, "Complete Your Staff Account Setup at GymOwners.com", body)


@worker_service.task(name="staff_password_reset_email", task_acks_late=True, ignore_result=True)
def staff_password_verification_email(to_email, data):
    body = get_template("contact/staff_password_reset.j2", data)
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, "Complete Your Password Reset at GymOwners.com", body)


@worker_service.task(name="contact_app_download_link_email", task_acks_late=True, ignore_result=True)
def contact_app_download_link_email(to_email, data):
    body = get_template("contact/contact_application_download.j2", data)
    subject = f"Welcome to {data['location_name']}! Your Fitness Journey Starts Here"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="contact_app_verification_code_email", task_acks_late=True, ignore_result=True)
def contact_app_verification_code_email(to_email, data):
    body = get_template("contact/contact_account_creation_confirmation.j2", data)
    subject = "Fitness Fun Awaits, Let's Verify Your Email!"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="contact_app_forgotten_password_code_email", task_acks_late=True, ignore_result=True)
def contact_app_forgotten_password_code_email(to_email, data):
    body = get_template("contact/contact_forgotten_password_reset.j2", data)
    subject = "Complete Your Password Reset"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)


@worker_service.task(name="profile_setup_email", task_acks_late=True, ignore_result=True)
def profile_setup_email(to_email, data):
    body = get_template("contact/profile_setup.j2", data)
    subject = "Quick Update: Add a Payment Method to Your Profile"
    send_email(get_config().EMAIL_FROM_ADDRESS, to_email, subject, body)
