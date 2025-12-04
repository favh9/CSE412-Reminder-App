import os
from uuid import uuid4
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Reminder, Category, File
from . import db

reminders_bp = Blueprint('reminders', __name__)

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def _save_file(file_storage):
    if not file_storage or file_storage.filename == '':
        return None
    if not _allowed_file(file_storage.filename):
        raise ValueError("Invalid file type. Only png, jpg, jpeg allowed.")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > current_app.config['MAX_CONTENT_LENGTH']:
        raise ValueError("File too large. Max 5MB.")

    filename = secure_filename(file_storage.filename)
    filename = f"{uuid4().hex}_{filename}"
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, filename))
    return filename, file_storage.mimetype, size

def _parse_due_time(due_time_str):
    if not due_time_str:
        return None, None
    try:
        dt = datetime.strptime(due_time_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Invalid due_time format")
    return dt.date(), dt.time()

def _remove_disk_file(filename):
    if not filename:
        return
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)

@reminders_bp.route('/dashboard')
@login_required
def dashboard():
    reminders = Reminder.query.filter_by(user_id=current_user.u_id).order_by(Reminder.r_date, Reminder.r_time).all()
    return render_template('dashboard.html', reminders=reminders)

@reminders_bp.route('/api/reminders', methods=['POST'])
@login_required
def add_reminder():
    if request.is_json:
        data = request.get_json()
        file_payload = None
    else:
        data = request.form
        try:
            saved = _save_file(request.files.get('image'))
            file_payload = saved
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    date_part, time_part = _parse_due_time(data.get('due_time'))
    if not date_part or not time_part:
        return jsonify({"error": "due_time is required"}), 400

    reminder = Reminder(
        r_title=data.get('title'),
        r_description=data.get('description'),
        r_date=date_part,
        r_time=time_part,
        r_status=data.get('status') or 'pending',
        user_id=current_user.u_id
    )
    db.session.add(reminder)
    db.session.flush()

    category_name = data.get('category')
    category_color = data.get('category_color')
    if category_name or category_color:
        cat = Category(c_name=category_name, c_color=category_color, reminder_id=reminder.r_id)
        db.session.add(cat)

    if not request.is_json and file_payload:
        filename, mimetype, size = file_payload
        file_row = File(f_name=filename, f_type=mimetype, f_size=size, reminder_id=reminder.r_id)
        db.session.add(file_row)

    db.session.commit()
    return jsonify({"message": "Reminder added"}), 201

@reminders_bp.route('/api/reminders/<int:id>', methods=['PUT'])
@login_required
def update_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.u_id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.is_json:
        data = request.get_json()
        new_file = None
    else:
        data = request.form
        try:
            new_file = _save_file(request.files.get('image'))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    if 'title' in data:
        reminder.r_title = data.get('title', reminder.r_title)
    if 'description' in data:
        reminder.r_description = data.get('description', reminder.r_description)

    if data.get('due_time'):
        try:
            date_part, time_part = _parse_due_time(data.get('due_time'))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        reminder.r_date = date_part or reminder.r_date
        reminder.r_time = time_part or reminder.r_time

    if 'status' in data:
        reminder.r_status = data.get('status', reminder.r_status)

    category_name = data.get('category')
    category_color = data.get('category_color')
    if category_name is not None or category_color is not None:
        if reminder.category:
            reminder.category.c_name = category_name or reminder.category.c_name
            reminder.category.c_color = category_color or reminder.category.c_color
        elif category_name or category_color:
            db.session.add(Category(c_name=category_name, c_color=category_color, reminder_id=reminder.r_id))

    if new_file:
        # remove existing files and disk copies
        for f in list(reminder.files):
            _remove_disk_file(f.f_name)
            db.session.delete(f)
        filename, mimetype, size = new_file
        db.session.add(File(f_name=filename, f_type=mimetype, f_size=size, reminder_id=reminder.r_id))

    db.session.commit()
    return jsonify({"message": "Reminder updated"})

@reminders_bp.route('/api/reminders/<int:id>', methods=['DELETE'])
@login_required
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    if reminder.user_id != current_user.u_id:
        return jsonify({"error": "Unauthorized"}), 403

    for f in list(reminder.files):
        _remove_disk_file(f.f_name)

    db.session.delete(reminder)
    db.session.commit()
    return jsonify({"message": "Reminder deleted"})

@reminders_bp.route('/uploads/<path:filename>')
@login_required
def get_upload(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
