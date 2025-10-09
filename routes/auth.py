from flask import render_template, redirect, url_for, request, Blueprint, session, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user, login_required, logout_user, current_user
from models import User, db, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Main page route. Redirects authenticated users to profile, shows login modal for others."""
    if current_user.is_authenticated and not session.pop('login_redirect', False):
        return redirect(url_for('main.profile'))

    return render_template('index.html', show_login_modal=session.pop('login_redirect', False))

@auth_bp.route('/auth', methods=['GET'])
def auth():
    """Authentication page route. Redirects authenticated users to profile."""
    if current_user.is_authenticated:
        next_url = request.args.get('next') or url_for('main.profile')
        return redirect(next_url)

    return render_template('auth.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login via POST request."""
    if current_user.is_authenticated:
        next_url = request.args.get('next') or url_for('main.profile')
        return redirect(next_url)

    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Неверные данные для входа."
        })

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        next_url = url_for('main.profile')
        print(next_url)
        return jsonify({
            "success": True,
            "message": "Вы успешно вошли в аккаунт.",
            "next": next_url
        })
    else:
        return jsonify({
            "success": False,
            "message": "Неверные данные для входа."
        })

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration via POST request."""
    try:
        if current_user.is_authenticated:
            next_url = request.args.get('next') or url_for('main.profile')
            return redirect(next_url)

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Отсутствуют данные запроса."
            }), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        c_password = data.get('c_password', '')

        # Validation
        if not username or not email or not password or not c_password:
            return jsonify({
                "success": False,
                "message": "Все поля обязательны для заполнения."
            }), 400

        if len(username) < 3:
            return jsonify({
                "success": False,
                "message": "Имя пользователя должно содержать минимум 3 символа."
            }), 400

        if len(password) < 6:
            return jsonify({
                "success": False,
                "message": "Пароль должен содержать минимум 6 символов."
            }), 400

        if password != c_password:
            return jsonify({
                "success": False,
                "message": "Пароли не совпадают."
            }), 400

        # Check existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                "success": False,
                "message": "Пользователь с таким именем уже существует."
            }), 400

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({
                "success": False,
                "message": "Пользователь с такой почтой уже существует."
            }), 400

        try:
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                user_role = Role(
                    name='user',
                    is_admin=False,
                    description="Стандартная группа пользователей"
                )
                db.session.add(user_role)
                db.session.commit()

            new_user = User(
                username=username,
                email=email
            )
            new_user.set_password(password)
            new_user.roles.append(user_role)

            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Вы успешно зарегистрировались."
            })

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Ошибка при создании пользователя: {str(e)}')
            return jsonify({
                "success": False,
                "message": f"Ошибка базы данных: {str(e)}"
            }), 500

    except Exception as e:
        print(f"Общая ошибка при регистрации: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Внутренняя ошибка сервера при регистрации."
        }), 500

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return jsonify({
            "success": True,
            "message": f"Вы вышли с аккаунта.",
        }), 200