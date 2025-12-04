from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db, bcrypt, login_manager

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if User.query.filter_by(u_email=email).first():
            flash("Email already registered")
            return redirect(url_for('auth.register'))

        new_user = User(u_email=email, u_password=password, u_first_name=first_name, u_last_name=last_name)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(u_email=email).first()

        if user and bcrypt.check_password_hash(user.u_password, password):
            login_user(user)
            return redirect(url_for('reminders.dashboard'))
        else:
            flash("Invalid email or password")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        user = User.query.filter_by(
            u_first_name=first_name,
            u_last_name=last_name,
            u_email=email
        ).first()

        if not user:
            flash("No matching user found. Please check your details.")
            return redirect(url_for('auth.reset_password_request'))

        return redirect(url_for('auth.reset_password', user_id=user.u_id))

    return render_template('reset_password_request.html')

@auth_bp.route('/reset-password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash("Please fill in all fields.")
            return redirect(url_for('auth.reset_password', user_id=user_id))

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('auth.reset_password', user_id=user_id))

        hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.u_password = hashed_pw
        db.session.commit()
        flash("Password reset successful. Please log in.")
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', user_id=user_id)
