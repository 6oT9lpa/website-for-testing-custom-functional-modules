"""
Database models for the application.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin
import pytz
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

db = SQLAlchemy()

moscow_tz = pytz.timezone('Europe/Moscow')

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def status(self):
        if not self.last_activity:
            return False
        return datetime.utcnow() - self.last_activity < timedelta(minutes=5)

    functions = db.relationship('FunctionUser', backref='author', lazy=True)
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_available_functions(self, visible=False):
        functions = []
        seen_ids = set()

        for role in self.roles:
            if role.is_admin:
                for func in FunctionUser.query.all():
                    if func.id not in seen_ids:
                        seen_ids.add(func.id)
                        functions.append(func)
                continue

            for func in role.functions:
                if func.id not in seen_ids:
                    if visible or func.approved:
                        seen_ids.add(func.id)
                        functions.append(func)

        return functions

    def has_access_to_function(self, func_id):
        if any(role.is_admin for role in self.roles):
            return True

        return any(func.id == func_id for role in self.roles for func in role.functions)

class FunctionUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    code = db.Column(db.String(100))
    function_type = db.Column(db.String(20))
    approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(moscow_tz))
    test_cases = db.Column(db.JSON)

class FunctionExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    function_id = db.Column(db.Integer, db.ForeignKey('function_user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    arguments = db.Column(db.JSON)
    result = db.Column(db.Text)
    success = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.now(moscow_tz))

    function = db.relationship('FunctionUser', backref='executions')
    user = db.relationship('User', backref='function_executions')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default='user', unique=True)
    description = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.JSON, default=list)

    functions = db.relationship('FunctionUser', secondary='role_function', backref='roles')
    users = db.relationship('User', secondary=user_roles, back_populates='roles')

role_function = db.Table('role_function',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('function_id', db.Integer, db.ForeignKey('function_user.id'))
)