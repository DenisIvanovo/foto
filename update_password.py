from app import User, db
from werkzeug.security import generate_password_hash


class Update:
    # Ищем пользователя в базе данных по email.
    def new_password(form, email):
        user = User.query.filter_by(email=f'{email}').first()  # Делаем запрос к базе дыннх.
        password = generate_password_hash(form.password.data)  # Хэшируем новый пароль.
        user.password = password  # Вставляем новый пароль.
        try:
            db.session.add(user)
            db.session.commit()  # Записываем новый пароль в базу.
            return 'Пароль изменен.'
        except ValueError:
            return 'Ошибка.Пароль НЕ изменен.'
