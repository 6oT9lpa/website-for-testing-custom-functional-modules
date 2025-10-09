from flask import render_template, redirect, url_for, Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import User, db, Role, FunctionUser

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile')
@login_required
def profile():
    """User profile page. Shows all functions if user has admin role."""
    show_all = any(role.is_admin for role in current_user.roles)
    return render_template('profile.html', show_all_functions=show_all)

@users_bp.route('/admin-panel')
@login_required
def admin_panel():
    """Admin panel for managing users, roles, and functions."""
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))

    users = User.query.options(db.joinedload(User.roles)).all()

    users_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'status': user.status,
            'registered_at': user.registered_at,
            'email': user.email,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
        }
        users_list.append(user_data)

    roles = Role.query.all()
    functions = FunctionUser.query.all()

    return render_template('admin_panel.html', users=users_list, roles=roles, functions=functions)

@users_bp.route('/get-user-data/<int:user_id>', methods=['GET'])
@login_required
def get_user_data(user_id):
    """Get user data including roles and function count."""
    user = User.query.get_or_404(user_id)
    functions_count = FunctionUser.query.filter_by(user_id=user_id).count()

    return jsonify({
        'id': user.id,
        'name': user.username,
        'roles': [role.id for role in user.roles],
        'func': functions_count
    })

@users_bp.route('/update-user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user roles."""
    user = User.query.get(user_id)
    role_ids = request.json.get('roles', [])

    if not user:
        return jsonify({"success": False, "message": "Пользователь не найден"}), 404

    new_roles = Role.query.filter(Role.id.in_(role_ids)).all()
    user.roles = new_roles
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Роли пользователя обновлены"
    })

@users_bp.route('/admin/check-status')
@login_required
def check_status():
    """Check online status of all users."""
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'status': u.status
    } for u in users])