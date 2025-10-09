import os
import json
import traceback
from flask import render_template, Blueprint, jsonify, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import FunctionUser, db, Role
from __init__ import app
from utils.code_execution import safe_exec, allowed_file

functions_bp = Blueprint('functions', __name__)

@functions_bp.route('/function/<int:func_id>/edit')
@login_required
def edit_function_page(func_id):
    """Page for editing a function."""
    function = FunctionUser.query.get_or_404(func_id)
    filepath = os.path.join(app.config['FUNCTION_MODELS_FOLDER'], function.code)
    with open(filepath, 'r', encoding='utf-8') as f:
        code_content = f.read()

    return render_template('function_editor.html', func=function, code_content=code_content)

@functions_bp.route('/function/<int:func_id>')
@login_required
def view_function(func_id):
    """View function details."""
    func = FunctionUser.query.get_or_404(func_id)
    return render_template('function_editor.html', function=func, view_only=True)

@functions_bp.route('/api/function', methods=['POST'])
@login_required
def create_function():
    """Create a new function."""
    try:
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        function_type = request.form.get('function_type')
        test_cases_str = request.form.get('test_cases', '')
        test_cases = json.loads(test_cases_str) if test_cases_str else []

        if not description:
            return jsonify({"success": False, "error": "Описание функции отсутствует"}), 400

        if function_type not in ["text/code", "image", "link"]:
            return jsonify({"success": False, "error": "Тип функции не соответсвует"}), 400

        os.makedirs(app.config['FUNCTION_MODELS_FOLDER'], exist_ok=True)

        existing_files = os.listdir(app.config['FUNCTION_MODELS_FOLDER'])
        file_number = len(existing_files) + 1
        filename = f"func_model{file_number:02d}.py"
        filepath = os.path.join(app.config['FUNCTION_MODELS_FOLDER'], filename)

        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.py'):
                code = file.read().decode('utf-8')
                code = code.replace('\r\n', '\n').replace('\r', '\n')
                name = name or file.filename[:-3]

        if not name or not code:
            return jsonify({'error': 'Name and code are required'}), 400

        exec_globals = {}
        exec_locals = {}
        try:
            safe_exec(code, exec_globals, exec_locals)
        except SyntaxError as e:
            return jsonify({
                "success": False,
                "error": f"Синтаксическая ошибка: {str(e)}",
                "line": e.lineno,
                "offset": e.offset
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Ошибка выполнения: {str(e)}",
                "traceback": traceback.format_exc()
            }), 400

        Function = exec_globals.get('Function') or exec_locals.get('Function')

        if not Function:
            return jsonify({
                "success": False,
                "error": "Не найден класс Function",
                "required": "class Function:\n    def interactionUser(self): ..."
            }), 400

        if not hasattr(Function, 'interactionUser') or not callable(Function.interactionUser):
            return jsonify({
                "success": False,
                "error": "Класс Function должен содержать метод interactionUser(self)",
                "example": "class Function:\n    def interactionUser(self):\n        return args"
            }), 400

        if not hasattr(Function, 'execute') or not callable(Function.execute):
            return jsonify({
                "success": False,
                "error": "Класс Function должен содержать метод execute(self, args)",
                "example": "class Function:\n    def execute(self, args):\n        return result"
            }), 400

        try:
            interaction_info = Function().interactionUser()
            if not isinstance(interaction_info, dict):
                return jsonify({"success": False, "error": "Метод interactionUser должен возвращать словарь"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": f"Ошибка выполнения interactionUser: {str(e)}"}), 400

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        func = FunctionUser(
            name=name,
            code=filename,
            user_id=current_user.id,
            approved=False,
            description=description,
            function_type=function_type,
            test_cases=test_cases
        )
        db.session.add(func)
        db.session.commit()

        return jsonify({'success': True, 'id': func.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@functions_bp.route('/api/function/<int:func_id>', methods=['DELETE'])
@login_required
def delete_function(func_id):
    """Delete a function."""
    func = FunctionUser.query.get_or_404(func_id)

    roles = Role.query.filter(Role.functions.any(id=func_id)).all()
    for role in roles:
        role.functions.remove(func)

    db.session.delete(func)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Функция удалена"
    })

@functions_bp.route('/api/function/<int:func_id>', methods=['PUT'])
@login_required
def update_function(func_id):
    """Update function code and description."""
    func = FunctionUser.query.get_or_404(func_id)
    data = request.json
    new_code = data['code']

    if 'description' in data:
        func.description = data['description']

    try:
        if 'code' in data:
            exec_globals = {}
            exec_locals = {}
            safe_exec(new_code, exec_globals, exec_locals)

            Function = exec_globals.get('Function') or exec_locals.get('Function')
            if not Function:
                return jsonify({"success": False, "error": "Не найден класс Function"}), 400

            if not hasattr(Function, 'interactionUser') or not callable(Function.interactionUser):
                return jsonify({"success": False, "error": "Класс Function должен содержать метод interactionUser"}), 400

            if not hasattr(Function, 'execute') or not callable(Function.execute):
                return jsonify({"success": False, "error": "Класс Function должен содержать метод execute"}), 400

            interaction_info = Function().interactionUser()
            if not isinstance(interaction_info, dict):
                return jsonify({"success": False, "error": "Метод interactionUser должен возвращать словарь"}), 400

            filename = func.code
            filepath = os.path.join(app.config['FUNCTION_MODELS_FOLDER'], filename)

            try:
                with open(filepath, 'w+', encoding='utf-8') as f:
                    f.write(new_code)
            except Exception as e:
                return jsonify({"success": False, "error": f"Ошибка записи в файл: {str(e)}"}), 500

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 400

@functions_bp.route('/api/function/<int:func_id>/toggle', methods=['POST'])
@login_required
def toggle_function_status(func_id):
    """Toggle function approval status."""
    func = FunctionUser.query.get_or_404(func_id)
    func.approved = not func.approved
    db.session.commit()

    return jsonify({
        "success": True,
        "new_status": func.approved
    })

@functions_bp.route('/api/function/test', methods=['POST'])
@login_required
def test_function():
    """Test function with provided test cases."""
    try:
        data = request.json
        code = data.get('code')
        test_cases = data.get('test_case', [])

        if not code:
            return jsonify({"success": False, "error": "Код функции отсутствует"}), 400

        exec_globals = {}
        exec_locals = {}

        try:
            safe_exec(code, exec_globals, exec_locals)
        except SyntaxError as e:
            return jsonify({
                "success": False,
                "error": f"Синтаксическая ошибка: {str(e)}",
                "line": e.lineno,
                "offset": e.offset
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Ошибка выполнения: {str(e)}",
                "traceback": traceback.format_exc()
            }), 400

        Function = exec_globals.get('Function') or exec_locals.get('Function')

        if not Function:
            return jsonify({
                "success": False,
                "error": "Не найден класс Function",
                "required": "class Function:\n    def execute(self, args): ..."
            }), 400

        if not hasattr(Function, 'execute') or not callable(Function.execute):
            return jsonify({
                "success": False,
                "error": "Класс Function должен содержать метод execute(self, args)",
                "example": "class Function:\n    def execute(self, args):\n        return args"
            }), 400

        results = []
        for test_case in test_cases:
            instance = Function()
            input_data = test_case.get('input', {})
            expected = test_case.get('expected')
            try:
                result = instance.execute(input_data)

                passed = (expected is None) or (str(result) == str(expected))

                results.append({
                    "input": json.dumps(input_data),
                    "output": json.dumps(result),
                    "expected": json.dumps(expected) if expected else "None",
                    "passed": passed,
                    "error": None
                })

            except Exception as e:
                results.append({
                    "input": input_data,
                    "output": None,
                    "expected": expected,
                    "passed": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        return jsonify({
            "success": True,
            "results": results,
            "stats": {
                "total": len(results),
                "passed": sum(1 for r in results if r['passed']),
                "failed": sum(1 for r in results if not r['passed'])
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Внутренняя ошибка сервера: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@functions_bp.route('/api/function/<int:func_id>/interaction', methods=['GET'])
@login_required
def get_function_interaction(func_id):
    """Get function interaction info."""
    func= FunctionUser.query.get_or_404(func_id)
    filepath = os.path.join(app.config['FUNCTION_MODELS_FOLDER'], func.code)
    with open(filepath, 'r', encoding='utf-8') as f:
        code_content = f.read()

    if not func.approved:
        return jsonify({"success": False, "error": "Функция не одобрена"}), 403

    exec_globals = {}
    exec_locals = {}
    try:
        safe_exec(code_content, exec_globals, exec_locals)
    except SyntaxError as e:
        return jsonify({
            "success": False,
            "error": f"Синтаксическая ошибка: {str(e)}",
            "line": e.lineno,
            "offset": e.offset
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Ошибка выполнения: {str(e)}",
            "traceback": traceback.format_exc()
        }), 400

    Function = exec_globals.get('Function') or exec_locals.get('Function')

    if not Function:
        return jsonify({"success": False, "error": "Некорректный формат функции"}), 400

    interaction_info = Function().interactionUser()
    return jsonify({
        "success": True,
        "id": func_id,
        "name": func.name,
        "interaction": interaction_info
    })

@functions_bp.route('/api/function/<int:func_id>/execute', methods=['POST'])
@login_required
def execute_function(func_id):
    """Execute a function with provided arguments."""
    func = FunctionUser.query.get_or_404(func_id)

    if not func.approved:
        return jsonify({"success": False, "error": "Функция не одобрена"}), 403

    if not current_user.has_access_to_function(func_id):
        return jsonify({"success": False, "error": "Нет доступа к этой функции"}), 403

    try:
        files = request.files.getlist('files')
        args = {}

        uploaded_files = []
        if files and files[0].filename != '':
            args = json.loads(request.form.get('arguments', '{}'))

            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'yolo_detect')
            os.makedirs(upload_folder, exist_ok=True)

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    try:
                        file.save(filepath)
                        uploaded_files.append(filepath)
                    except Exception as e:
                        return jsonify({"success": False, "error": f"Ошибка сохранения файла: {str(e)}"}), 500
                elif file:
                    return jsonify({"success": False, "error": f"Недопустимый тип файла: {file.filename}"}), 400
        else:
            args = request.get_json().get('arguments', {})

        print(args)

        if uploaded_files:
            args['img_paths'] = uploaded_files

        filepath = os.path.join(app.config['FUNCTION_MODELS_FOLDER'], func.code)

        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        exec_globals = {}
        exec_locals = {}
        safe_exec(code, exec_globals, exec_locals)

        Function = exec_globals.get('Function') or exec_locals.get('Function')
        if not Function:
            raise Exception("Не найден класс Function")

        if not hasattr(Function, 'execute'):
            raise Exception("Класс Function должен содержать метод execute")

        instance = Function()
        result = instance.execute(args)

        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, str) and app.config['UPLOAD_FOLDER'] in value:
                    result[key] = value.replace(app.config['UPLOAD_FOLDER'], 'uploads').replace('\\', '/')
                elif isinstance(value, list):
                    result[key] = [item.replace(app.config['UPLOAD_FOLDER'], 'uploads').replace('\\', '/') if isinstance(item, str) and app.config['UPLOAD_FOLDER'] in item else item for item in value]

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 400

@functions_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)