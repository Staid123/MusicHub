from celery import Celery
import smtplib
import logging
from config import settings
from email.message import EmailMessage


celery_app = Celery('notifications', broker='redis://localhost:6379/0')


def get_email_template_dashboard(username, email):
    email_message = EmailMessage()
    email_message['Subject'] = "Welcome!"
    email_message['From'] = settings.smtp.user
    email_message['TO'] = email

    email_message.set_content(
        f'''
        <div>
            <h1 style="color: blue;">Hello, {username},</h1>
            <p>Thank you for registering with us.</p>
        </div>
        ''',
        subtype='html'
    )
    return email_message


@celery_app.task
def send_email_message_after_register_or_login(username, email):
    # Логика отправки письма
    email_message = get_email_template_dashboard(username, email)
    with smtplib.SMTP_SSL(settings.smtp.host, settings.smtp.port) as server:
        server.login(settings.smtp.user, settings.smtp.password)
        server.send_message(email_message)
    logging.info(f"Sending email to {email}")








