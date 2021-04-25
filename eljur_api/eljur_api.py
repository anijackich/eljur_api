import requests

from diary import ElDiary
from journal import ElJournal
from messages import ElMessages
from user import ElUser

from config import _BASE_DOMAIN, _AUTH


class EljurApi(object):
    def __init__(self, school=None, login=None, password=None):
        self.ej = requests.session()
        self.login = login
        self.password = password
        self.school = school

        self.auth()

    def auth(self):
        """
        Авторизация пользователя
        """

        status = self.ej.post(f'https://{self.school}.{_BASE_DOMAIN}{_AUTH}', {
            'username': self.login,
            'password': self.password
        }).status_code

        if not status == 200:
            self._pass_security_check()

    def _pass_security_check(self):
        """
        Обход блокировки запроса для авторизации
        """

        status = self.ej.post(f'https://{self.school}.{_BASE_DOMAIN}{_AUTH}', {
            'username': self.login,
            'password': self.password
        }, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'
        }).status_code

        if not status == 200:
            raise RuntimeError('Authorization failed. Check your username and password.')

    def get_api(self):
        """
        Позволяет получить доступ к Api
        """

        return EljurApiMethod(self)


class EljurApiMethod(object):
    """
    Позволяет обращаться к функциям Api
    """

    def __init__(self, ej):
        self.ej = ej

        self.diary = ElDiary(self.ej)
        self.journal = ElJournal(self.ej)
        self.messages = ElMessages(self.ej)
        self.user = ElUser(self.ej)
