import smtplib
import json
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

from celery import current_task
from gmsshared.src.config import get_config
from gmsshared.src.models.location import Location
from gmsshared.src.models.user import User
from gmsshared.src.models.update_log import UpdateLog

def get_template(template_file, data):
    # Make sure the path is relative to the working directory of the app / service
    file_loader = FileSystemLoader("email-worker/src/emails/templates")
    env = Environment(loader=file_loader)
    template = env.get_template(template_file)
    return template.render(data)


def send_email(from_addr, to_addrs, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    if isinstance(to_addrs, list):
        msg["To"] = ", ".join(to_addrs)
    else:
        msg["To"] = to_addrs

    to_email = to_addrs.split(",")[0]
    user = User.find_by_email(to_email)
    location = user.locations[0]

    msg.set_content(body)
    try:
        with smtplib.SMTP(get_config().SMTP_SERVER, get_config().SMTP_PORT) as server:
            server.starttls()
            server.login(get_config().SMTP_USER, get_config().SMTP_PASS)
            server.send_message(msg=msg, from_addr=None, to_addrs=None)

            email_dict = {
                "from": msg["From"],
                "to": msg["To"],
                "subject": msg["Subject"],
                "body": msg.get_payload(decode=True).decode()
            }

            # Log the email
            update_log = UpdateLog()
            update_log.location_id = location.id
            update_log.user_id = 0
            update_log.target_user_id = user.id
            update_log.method = "EMAIL"
            update_log.request_url = current_task.name
            update_log.request_body = json.dumps(email_dict)
            update_log.save_and_commit()

    except Exception as ex:
        print(ex)
