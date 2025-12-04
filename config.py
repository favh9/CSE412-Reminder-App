import os
from pathlib import Path

# Load environment variables from .env if python-dotenv is installed.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / '.env')
except ImportError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devkey123'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://favh:password@localhost:8888/favh'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')  # set this in your .env
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # set this in your .env
    MAIL_DEFAULT_SENDER = MAIL_USERNAME  # required by Flask-Mail

    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
