from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    u_id = db.Column(db.Integer, primary_key=True)
    u_first_name = db.Column(db.Text)
    u_last_name = db.Column(db.Text)
    u_email = db.Column(db.Text, unique=True, nullable=False)
    u_password = db.Column(db.Text, nullable=False)

    reminders = db.relationship('Reminder', backref='user', lazy=True, cascade="all, delete-orphan")

    def get_id(self):
        return str(self.u_id)

class Reminder(db.Model):
    __tablename__ = 'reminder'
    r_id = db.Column(db.Integer, primary_key=True)
    r_title = db.Column(db.Text)
    r_description = db.Column(db.Text)
    r_date = db.Column(db.Date)
    r_time = db.Column(db.Time)
    r_status = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)
    notified = db.Column(db.Boolean, default=False)

    category = db.relationship('Category', backref='reminder', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='reminder', lazy=True, cascade="all, delete-orphan")
    files = db.relationship('File', backref='reminder', lazy=True, cascade="all, delete-orphan")

class Category(db.Model):
    __tablename__ = 'category'
    c_id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.Text)
    c_color = db.Column(db.Text)
    reminder_id = db.Column(db.Integer, db.ForeignKey('reminder.r_id'), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notification'
    n_id = db.Column(db.Integer, primary_key=True)
    n_description = db.Column(db.Text)
    n_send_time = db.Column(db.DateTime, nullable=False)
    reminder_id = db.Column(db.Integer, db.ForeignKey('reminder.r_id'), nullable=False)

class File(db.Model):
    __tablename__ = 'file'
    f_id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.Text)
    f_type = db.Column(db.Text)
    f_size = db.Column(db.Integer)
    reminder_id = db.Column(db.Integer, db.ForeignKey('reminder.r_id'), nullable=False)
