import time
from datetime import datetime, time as dtime
from app import create_app, db
from app.models import Reminder, User
from app.emailer import send_reminder_email

app = create_app()

CHECK_INTERVAL = 60  # in seconds

def check_and_send_reminders():
    with app.app_context():
        now = datetime.utcnow()
        today = now.date()
        current_time = now.time()

        due_reminders = Reminder.query.filter(
            Reminder.r_date <= today,
            Reminder.notified == False
        ).all()

        for reminder in due_reminders:
            reminder_time = reminder.r_time or dtime(0, 0)
            if reminder.r_date == today and reminder_time > current_time:
                continue

            user = db.session.get(User, reminder.user_id)
            if user:
                subject = f"Reminder: {reminder.r_title}"
                due_str = f"{reminder.r_date} {reminder_time}"
                body = f"Hi,\n\nThis is your reminder:\n\n{reminder.r_title}\n{reminder.r_description}\nDue: {due_str}\n\nReminder App"
                send_reminder_email(user.u_email, subject, body)
                reminder.notified = True
                db.session.commit()

if __name__ == '__main__':
    print("Starting reminder scheduler...")
    while True:
        check_and_send_reminders()
        time.sleep(CHECK_INTERVAL)
