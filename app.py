import os
from flask import Flask, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy  # Модуль для подключенния к базе данных.
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import datetime
from form import Aut_form, RegistrationForm, Password_recovery, Update_password  # Импортируем модуль форм.
from User_on import User_online  # Импортируем модуль для работы с пользователями.
import json
from werkzeug.security import check_password_hash

with open('info_mail.json', 'r')as file:  # Получаем данные для работы с почтой.
    info = json.load(file)

UPLOAD_FOLDER = './static/'  # Путь по которому загружаем файлы.
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']  # Формат загружаемых файлов.
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер загружаемого файла.
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photo_website.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = 'fgvfhghyhgddfrrghghg'  # Секретный ключ для передачи сообщений.
application.config['MAIL_SERVER'] = info['SERVER']  # Получаем имя сервера.
application.config['MAIL_PORT'] = info['PORT']  # Получаем порт.
application.config['MAIL_USE_TLS'] = False
application.config['MAIL_USE_SSL'] = True
application.config['MAIL_USERNAME'] = info['USERNAME']  # введите свой адрес электронной почты здесь
application.config['MAIL_DEFAULT_SENDER'] = ('bot-photo-storage.ru ', info['DEFAULT_SENDER'])
application.config['MAIL_PASSWORD'] = info['PASSWORD']  # введите пароль
db = SQLAlchemy(application)
mail = Mail(application)
login_manager = LoginManager()
login_manager.init_app(application)
# Если пользователь НЕ авторизован перекидываем его на страничку авторизации.
login_manager.login_view = 'main'
authorization_attempt = 3  # Попытки авторизоваться.


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    # Создаем колонки в базе данных.
    # Вводим данные зарегистрированных пользователей.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(20), nullable=True)
    user_nic = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.id


def allowed_file(filename):
    # Проверяем какого формата загружаемый файл.
    print(filename)
    print(filename.rsplit('.', 1)[1])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


new_photo = []  # Список загружаемых файллов.


def app_separator():
    # Встовляем разделитель,для перехода на новую стоку в таблице html
    sep = '#'
    list_of_values_list = [3, 7, 11]  # Указываем после какого кличества вставляем разделитель.
    if len(new_photo) in list_of_values_list:  # Если Количечество объектов в списке равна хотябы одному из списка,
        # Тогда добавляем разделитель в список
        new_photo.append(sep)
    else:
        pass


@application.route('/', methods=['GET', 'POST'])
def main():
    global authorization_attempt
    form = Aut_form()
    # Если user авторизовался НЕ удачно 3 раза.
    # Блокируем user на 1 час по причине подозрения подбора пароля и логина.
    if authorization_attempt == 0:
        # Перекидываем user на страницу блокировки.
        return redirect(url_for('lockdown'))
    else:
        if form.validate_on_submit():  # Обрабатываем метод POST
            login = User.query.filter_by(user_nic=form.username.data).first()  # Делаем запрос к базе дыннх.
            if login is None:
                #  Если такого пользователя нет в базе данных
                authorization_attempt -= 1  # Уменьшаем количество авторизации.
                print(authorization_attempt)
                flash(f'Пользователь {form.username.data} НЕ зарегистрирован на сайте. ')
                return redirect(url_for('main'))
            else:
                if check_password_hash(login.password, form.password.data):
                    login_user(login)
                    return redirect(url_for('stub'))
                else:
                    flash('Неправильный пароль')
                    authorization_attempt -= 1  # Уменьшаем количество авторизации.
                    print(authorization_attempt)
                    return redirect(url_for('main'))
        else:
            return render_template('authentication.html', form=form)


@application.route('/append', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file_users = request.files['file']  # Получаем файл через метод POST
        if file_users and allowed_file(file_users.filename):  # Проверяем формат полученого файла.
            # Если поддерживающий формат файла.
            if file_users.filename in new_photo:  # Выполняем проверку на повторную загрузку файла.
                flash('Такой файл есть')
                return render_template('images.html', photo=new_photo, info_user=current_user)
            else:
                app_separator()
                date = datetime.date.today()
                new_photo.append(file_users.filename)  # Добавляем имя файла в список.
                print(len(new_photo))
                filename = secure_filename(file_users.filename)
                file_users.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))  # Сохраняем полученый файл
                return render_template('images.html', photo=new_photo, info_user=current_user)
    return render_template('images.html', info_user=current_user)


@application.route('/photo', methods=['GET', 'POST'])
@login_required
def photo():
    # Главная страница сайта.
    return render_template('main.html', info_user=current_user)


from new_user import New_user  # Регистрируем нового пользователя.


@application.route('/registration', methods=['GET', 'POST'])
# Регистрируем на сайте нового пользователя.
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():  # Обрабатываем метод POST
        # Выполняем проверку на уникальность параметра 'Email' перед записью в базу данных.
        new_email = form.email.data  # Получаем введеный пользователем email
        email = User.query.filter_by(email=new_email).first()  # Делаем запрос к базе дыннх.
        # Если пользователь с таком Email нет в базе данных,регистрируем его
        if email is None:
            New_user(form)  # Данны с формы отправляем в другой модуль,для записи в db
            flash('Регистрация прошла успешно.\n'
                  'Пожалуйста, перейдите по ссылке, чтобы подтвердить свою регистрацию.\n'
                  'Мы отправили электронное письмо на указанный почтовый адрес.')
            return redirect(url_for('main'))
        else:
            # Если пользователь с таким Email зарегистрирован в базе,тогда сообщаем об этом.
            flash(f'Пользователь с адресом "{new_email}" уже зарегистрирован на сайте.')
            return redirect(url_for('registration'))
    else:
        return render_template('registration.html', form=form)


@application.route('/user', methods=['POST', 'GET'])
@login_required
def user():
    # Получаем имя пользователя и ник
    if request.method == 'POST':
        info_users = User_online.online(User)
        render_template('user.html', info=info_users)
    else:
        return render_template('user.html')


from recovery import Recovery  # Импортируем модуль для востановления пароля.


@application.route('/password_recovery', methods=['POST', 'GET'])
def password_recovery():
    # Восстанавливаем пароль пользователя.
    form = Password_recovery()
    if form.validate_on_submit():  # Обрабатываем метод POST
        site_user = User.query.filter_by(email=form.address.data).first()  # Делаем запрос к базе дыннх.
        # Если такого email адреса НЕзарегистрировано в базе,сообщаем об этом.
        if site_user is None:
            # Сообщаем об ошибке.
            flash('Введенный адрес электронной почты не зарегистрирован.')
            return redirect(url_for('password_recovery'))
        else:
            Recovery(form)
            flash(f'Мы отправии инструкцию по восановлению пароля на указаный почтовый адрес.')
            return redirect(url_for('password_recovery'))
    else:
        return render_template('password recovery.html', title='Восстановление пароля ', form=form)


from update_password import Update


@application.route('/update_password/<string:email>', methods=['GET', 'POST'])
def update_password(email):
    # Записываем новый пароль в базу данных.
    form = Update_password()
    if form.validate_on_submit():  # Обрабатываем метод POST
        result = Update.new_password(form, email)  # Передаем новый пароль,email в другой модуль.
        flash(result)  # Передаем результат функции.
        return redirect(url_for('main'))  # Перенапровяем на главную страницу.
    else:
        return render_template('new_password.html', form=form)


@application.route('/contacts')
def contacts():
    # Страничка контакты,обратная форма связи.
    return render_template('feedback_form.html')

@application.route('/logout')
def logout():
    # Выход из системы.
    logout_user()
    return redirect(url_for('main'))  # Перенаправляем пользователя н аглавную страницу.


@application.errorhandler(404)
def mistake(error):
    # В этой функции обрабатываем ошибку 404
    return render_template('404.html'), 404


@application.errorhandler(500)
def mistake_500(error):
    # Обрабатываем ошибку 500
    return render_template('500.html')


@application.route('/loc')
# Страница блогировки пользователя.
def lockdown():
    return render_template('lockdown.html')


@application.route('/stub')
# Страница заглушка(пока иду изменения станицы)
def stub():
    return render_template('stub.html', info_user=current_user)


if __name__ == "__main__":
    application.run(host='0.0.0.0')
