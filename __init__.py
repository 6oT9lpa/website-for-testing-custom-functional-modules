from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager, current_user
from models import db, User, Role, FunctionUser, FunctionExecution
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    session['login_redirect'] = True
    return redirect(url_for('main.index') + '#login')

@app.before_request
def update_last_activity():
    if current_user.is_authenticated:
        current_user.last_activity = datetime.utcnow()
        db.session.commit()
