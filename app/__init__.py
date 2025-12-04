import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app():
    # Point Flask at the project-level templates/static directories
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .auth import auth_bp
    from .reminders import reminders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reminders_bp)

    return app
