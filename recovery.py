"""
Модуль для востановления пароля пользователя.
Отправляем сообщение на электроную почту ссылку для внесения нового пароля.

"""

from app import mail, Message

adpess_site = 'http://www.photo-storage.ru'


class Recovery:
    def __init__(self, form):
        try:
            msg = Message("Пароль от аккаунта", recipients=[f'{form.address.data}'])
            msg.html = f"<h2>Для изменения пароля на сайте {adpess_site}\n" \
                       f"передите по ссылке и введите новый пароль \n" \
                       f"<a href='{adpess_site}/update_password/{form.address.data}'>Изменить пароль" \
                       f"</a></h2>\n<p></p>"
            mail.send(msg)
        except :
            pass

