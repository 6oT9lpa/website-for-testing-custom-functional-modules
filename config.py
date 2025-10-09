import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FUNCTION_MODELS_FOLDER = str(Path(__file__).parent / 'uploads' / 'func_models')
    UPLOAD_FOLDER = str(Path(__file__).parent / 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'txt', 'py', 'json'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024