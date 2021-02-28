from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Length, Email, EqualTo


# noinspection PyDeprecation
class Aut_form(FlaskForm):
    """Создаем класс формы авторизации на сайте."""
    username = StringField('логин', validators=[Required()])
    password = PasswordField('Пароль', validators=[Required()])
    submit = SubmitField('Войти')


# noinspection PyDeprecation
class RegistrationForm(FlaskForm):
    # Создаем класс формы регистрации нового пользователя.
    user_name = StringField(label='Имя', validators=[Required(),
                                                     Length(3, message='Имя неможет состоять '
                                                                       'менее чем 3 буквы')])
    user_last_name = StringField(label='Фамилия', validators=[Required(),
                                                              Length(5, message='Фамилия неможет'
                                                                                'состоять менее'
                                                                                'чем 5 букв')])
    user_nic = StringField(label='Ник', validators=[Required()])
    email = StringField(label='Email', validators=[Email()])
    password = PasswordField(label='Пароль', validators=[Required(),
                                                         Length(8, 20, message='Минимальная длина\n'
                                                                               'пароля 8, максимальное'
                                                                               '20')])
    password_2 = PasswordField(label='Повторите пароль', validators=[Required(),
                                                                     EqualTo('password', message='Пароли\n'
                                                                                                 'несовподают')])

    submit = SubmitField('Зарегистрироваться')


class Password_recovery(FlaskForm):
    # Создаем класс для восстановления пароля.
    address = StringField(label='Email           ', validators=[Email()])
    submit = SubmitField('Восстановить пароль')


# noinspection PyDeprecation
class Update_password(FlaskForm):
    # Создаем класс для изменения пароля от аккаунта пользователя.
    password = PasswordField(label='Новый пароль', validators=[Required(),
                                                               Length(8, 20, message='Минимальная длина\n'
                                                                                     'пароля 8, максимальное'
                                                                                     '20')])
    password_2 = PasswordField(label='Повторите пароль', validators=[Required(),
                                                                     EqualTo('password', message='Пароли\n'
                                                                                                 'несовподают')])
    submit = SubmitField('Записать пароль')