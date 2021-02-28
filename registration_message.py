"""
Модуль для оповещения о успешной регистрации.

"""

from app import mail, Message

adpess_site = 'http://www.photo-storage.ru'


class Message_info:
    def __init__(self, email):
        try:
            msg = Message(f"Регистрация на сайте  {adpess_site}", recipients=[f'{email}'])
            msg.html = f"<h2>Подтреждение о регистрации на сайте</h2>"
            mail.send(msg)
        except:
            pass
