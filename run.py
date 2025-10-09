from __init__ import app, db, Role
from main import main
app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Role.query.filter(Role.name.in_(['user', 'admin'])).count():
            user_role = Role(
                name='user',
                is_admin=False,
                description="Стандартная группа пользователей"
            )

            admin_role = Role(
                name='admin',
                is_admin=True,
                description="Группа администрирования сайта"
            )

            db.session.add(user_role)
            db.session.add(admin_role)
            db.session.commit()
            print("Роли успешно созданы!")
        else:
            print("Роли уже существуют в базе")

    app.run(host='0.0.0.0', port=8000, debug=False)