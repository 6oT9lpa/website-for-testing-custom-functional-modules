import json
from flask import Blueprint, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from __init__ import Role, db, FunctionUser, FunctionExecution, User
from sqlalchemy.exc import SQLAlchemyError

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/roles', methods=['GET'])
@login_required
def get_all_roles():
    """Get all roles with their details."""
    roles = Role.query.all()
    return jsonify([{
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'is_admin': role.is_admin,
    } for role in roles])

@api_bp.route('/api/role/<int:role_id>', methods=['GET'])
@login_required
def update_role(role_id):
    """Get role details including associated functions."""
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))

    role = Role.query.get_or_404(role_id)

    return jsonify({
        'id': role.id,
        'name': role.name,
        'is_admin': role.is_admin,
        'permissions': role.permissions or [],
        'description': role.description,
        'functions': [{
            'id': f.id,
            'name': f.name,
            'approved': f.approved
        } for f in role.functions]
    })

@api_bp.route('/api/role/<int:role_ids>', methods=['DELETE'])
@login_required
def delete_role(role_ids):
    """Delete a role and reassign users to default role."""
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if not any(role.is_admin for role in current_user.roles):
        return jsonify({'error': 'У вас нет доступа для удаления роли!'}), 403

    role = Role.query.get_or_404(role_ids)
    if role.name == 'user':
        return jsonify({'error': 'Вы не можете удалить default роль!'}), 403

    users = User.query.filter(User.roles.any(id=role_ids)).all()
    default_role = Role.query.filter_by(name='user').first()
    for user in users:
        if default_role and default_role not in user.roles:
            user.roles.append(default_role)
        user.roles.remove(role)

    db.session.delete(role)
    db.session.commit()

    return jsonify({'status': 'success'})

@api_bp.route('/api/role', methods=['POST'])
@api_bp.route('/api/role/<int:role_id>', methods=['PUT'])
@login_required
def handle_role(role_id=None):
    """Create or update a role."""
    data = request.json
    if role_id:
        role = Role.query.get_or_404(role_id)
        role.name = data['name']
        role.is_admin = data['is_admin']
    else:
        role = Role(
            name=data['name'],
            is_admin=data['is_admin'],
            permissions=[]
        )

    function_ids = [int(fid) for fid in data.get('functions', [])]
    role.permissions = function_ids

    if role_id:
        role.functions.clear()

    for fid in function_ids:
        func = FunctionUser.query.get(fid)
        if func:
            role.functions.append(func)

    db.session.add(role)
    db.session.commit()
    return jsonify(success=True)

@api_bp.route('/api/function/execution', methods=['POST'])
@login_required
def save_function_execution():
    """Save function execution record."""
    data = request.json
    func_id = data.get('function_id')
    args = data.get('arguments')
    result = data.get('result')
    is_success = data.get('success', False)

    if not func_id or not args:
        return jsonify({"success": False, "error": "Недостаточно данных"}), 400

    execution = FunctionExecution(
        function_id=func_id,
        user_id=current_user.id,
        arguments=args,
        result=str(result),
        success=is_success
    )

    db.session.add(execution)
    db.session.commit()

    return jsonify({"success": True})

@api_bp.route('/api/function/executions', methods=['GET'])
@login_required
def get_function_executions():
    """Get user's recent function executions."""
    executions = (db.session.query(FunctionExecution, FunctionUser)
                .join(FunctionUser, FunctionExecution.function_id == FunctionUser.id)
                .filter(FunctionExecution.user_id == current_user.id)
                .order_by(FunctionExecution.timestamp.desc())
                .limit(20)
                .all())

    result = []
    for execution, func in executions:
        try:
            parsed_result = json.loads(execution.result)
            display_result = parsed_result.get('message', str(parsed_result))
        except:
            display_result = execution.result

        result.append({
            'id': execution.id,
            'function': {
                'id': func.id,
                'name': func.name
            },
            'arguments': execution.arguments,
            'result': display_result,
            'success': execution.success,
            'timestamp': execution.timestamp.isoformat()
        })

    return jsonify({
        "success": True,
        "executions": result
    })