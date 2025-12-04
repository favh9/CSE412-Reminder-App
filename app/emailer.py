from flask_mail import Message
from flask import current_app
from . import mail

def send_reminder_email(to_email, subject, body):
    msg = Message(subject, recipients=[to_email], sender=current_app.config.get('MAIL_DEFAULT_SENDER'))
    msg.body = body
    with current_app.app_context():
        mail.send(msg)
