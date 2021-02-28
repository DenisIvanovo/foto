from app import db, User
import os
from werkzeug.security import generate_password_hash
from registration_message import Message_info

class New_user:
    def __init__(self, form):
        # Получаем данные из формы.
        user_name = form.user_name.data
        user_last_name = form.user_last_name.data
        user_nic = form.user_nic.data
        email = form.email.data
        password = form.password.data
        password_2 = form.password_2.data

        # Хэшируем пароль пользователя.
        password = generate_password_hash(password)
        # Добавляем пользователвля в базу данных.
        user_info = User(name=user_name,
                         last_name=user_last_name,
                         user_nic=user_nic,
                         email=email,
                         password=password)
        try:
            db.session.add(user_info)
            db.session.commit()
            print('Пользователь добавлен в базу')
        except ValueError:
            print('error')
        try:
            # Создаем отдельную папку для загрузки фото
            os.chdir('./static/')  # Переходи в нужную директорию.
            # Создаем папку, для имени папки используем ник и email пользователя.
            # ник и email берем из формы.
            os.mkdir(f"{user_nic}-{email}")
            # Оповещаем пользователя о успешной регистрации.
            Message_info(email)
        except OSError:
            pass
