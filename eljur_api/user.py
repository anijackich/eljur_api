from config import _USER_INFO, _BASE_DOMAIN
from bs4 import BeautifulSoup


class ElUser(object):
    def __init__(self, ej):
        self.ej = ej.ej
        self.school = ej.school

    def get_personal_info(self):
        page = self.ej.get(f'https://{self.school}.{_BASE_DOMAIN}{_USER_INFO}')
        soup = BeautifulSoup(page.content, 'html.parser')

        return {'surname': soup.find('label', {'for': 'lastname'}).find_next('span').text,
                'name': soup.find('label', {'for': 'firstname'}).find_next('span').text,
                'middle_name': soup.find('label', {'for': 'middlename'}).find_next('span').text,
                'sex': soup.find('label', {'for': 'sex'}).find_next('span').text,
                'birthday': soup.find('label', {'for': 'birthday'}).find_next('span').text,
                'snils': soup.find('label', {'for': 'lastname'}).find_next('input')['value'],
                'email': soup.find('label', {'for': 'email'}).find_next('input')['value'],
                'phone': soup.find('label', {'for': 'phone'}).find_next('input')['value'],
                }

