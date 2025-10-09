"""
Main application routes and blueprint registration.
This module organizes all route blueprints for the Flask application.
"""

from flask import Blueprint
from routes.auth import auth_bp
from routes.users import users_bp
from routes.functions import functions_bp
from routes.api import api_bp

# Main blueprint that combines all route blueprints
main = Blueprint('main', __name__)

# Register sub-blueprints with URL prefixes
main.register_blueprint(auth_bp)
main.register_blueprint(users_bp)
main.register_blueprint(functions_bp)
main.register_blueprint(api_bp)