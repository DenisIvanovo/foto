import os
from flask import Flask, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy  # Модуль для подключенния к базе данных.
from flask_login import LoginManager
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import datetime
from form import Aut_form, RegistrationForm, Password_recovery, Update_password  # Импортируем модуль форм.
from User_on import User_online  # Импортируем модуль для работы с пользователями.
import json
from werkzeug.security import check_password_hash

with open('info_mail.json', 'r')as file:  # Получаем данные для работы с почтой.
    info = json.load(file)

# /home/DenisMor/mysite/static/zag/
UPLOAD_FOLDER = './static/'  # Путь по которому загружаем файлы.
ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'gif']  # Формат загружаемых файлов.
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер загружаемого файла.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photo_website.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fgvfhghyhgddfrrghghg'  # Секретный ключ для работы с формами.
app.config['MAIL_SERVER'] = info['SERVER']  # Получаем имя сервера.
app.config['MAIL_PORT'] = info['PORT']  # Получаем порт.
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = info['USERNAME']  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = info['DEFAULT_SENDER']
app.config['MAIL_PASSWORD'] = info['PASSWORD']  # введите пароль
db = SQLAlchemy(app)
mail = Mail(app)


# login_manger = LoginManager(app)


class User(db.Model):
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


@app.route('/', methods=['GET', 'POST'])
def main():
    form = Aut_form()
    if form.validate_on_submit():  # Обрабатываем метод POST
        login = User.query.filter_by(user_nic=form.username.data).first()  # Делаем запрос к базе дыннх.
        if login is None:
            #  Если такого пользователя нет в базе данных
            flash(f'Пользователь {form.username.data} НЕ зарегистрирован на сайте. ')
            return redirect(url_for('main'))
        else:
            if check_password_hash(login.password, form.password.data):
                return redirect(url_for('photo'))
            else:
                flash('Неправильный пароль')
                return redirect(url_for('main'))
    else:
        return render_template('authentication.html', form=form)


@app.route('/append', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file_users = request.files['file']  # Получаем файл через метод POST
        if file_users and allowed_file(file_users.filename):  # Проверяем формат полученого файла.
            # Если поддерживающий формат файла.
            if file_users.filename in new_photo:  # Выполняем проверку на повторную загрузку файла.
                print('Такой файл есть')
                return render_template('images.html', photo=new_photo)
            else:
                app_separator()
                date = datetime.date.today()
                new_photo.append({'name': file_users.filename,
                                  'data': date,
                                  'info': file_users.filename.rsplit('.', 1)[1]})
                print(len(new_photo))
                filename = secure_filename(file_users.filename)
                file_users.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('images.html', photo=new_photo)
    return render_template('images.html')


@app.route('/photo', methods=['GET', 'POST'])
def photo():
    # Главная страница сайта.
    return render_template('main.html')


from new_user import New_user  # Регистрируем нового пользователя.


@app.route('/registration', methods=['GET', 'POST'])
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
            return redirect(url_for('main'))
        else:
            # Если пользователь с таким Email зарегистрирован в базе,тогда сообщаем об этом.
            flash(f'Пользователь с адресом "{new_email}" уже зарегистрирован на сайте.')
            return redirect(url_for('registration'))
    else:
        return render_template('registration.html', form=form)


@app.errorhandler(404)
def mistake(error):
    # В этой функции обрабатываем ошибку 404
    return render_template('404.html'), 404


@app.route('/user', methods=['POST', 'GET'])
def user():
    # Получаем имя пользователя и ник
    if request.method == 'POST':
        info_users = User_online.online(User)
        return render_template('user.html', info=info_users)
    else:
        return render_template('user.html')


from recovery import Recovery  # Импортируем модуль для востановления пароля.


@app.route('/password_recovery', methods=['POST', 'GET'])
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
            Recovery(form, site_user)
            flash(f'Мы отправии инструкцию по восановлению пароля на указаный почтовый адрес.')
            return redirect(url_for('password_recovery'))
    else:
        return render_template('password recovery.html', title='Восстановление пароля ', form=form)


from update_password import Update


@app.route('/update_password/<string:email>', methods=['GET', 'POST'])
def update_password(email):
    Update()
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
