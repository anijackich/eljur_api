from bs4 import BeautifulSoup
import threading

from config import _DAYS_OF_THE_WEEK, _BASE_DOMAIN, _DIARY


class ElDiary(object):
    def __init__(self, ej):
        self.ej = ej.ej
        self.school = ej.school

    def _parse_day_block(self, day_block):
        def clear(text):
            return text.replace('\n', '').replace('  ', '')

        title = clear(day_block.find('div', {'class': 'dnevnik-day__title'}).text).split(', ')
        day_of_week = title[0]
        date = title[1]

        result = {
            'day_of_week': day_of_week,
            'date': date,
            'lessons': []
        }

        if not day_block.find('div', {'class': 'page-empty'}) is None:
            return result

        lessons_block = day_block.find('div', {'class': 'dnevnik-day__lessons'})
        lessons = lessons_block.find_all('div', {'class': 'dnevnik-lesson'})
        for lesson in lessons:
            number_block = lesson.find('div', {'class': 'dnevnik-lesson__number'})
            if not number_block is None:
                number = int(clear(number_block.text).replace('.', ''))
            else:
                number = 0

            subject_block = lesson.find('span', {'class': 'js-rt_licey-dnevnik-subject'})
            if not subject_block is None:
                subject = subject_block.text
            else:
                subject = ''

            time_block = lesson.find('div', {'class': 'dnevnik-lesson__time'})
            if not time_block is None:
                time = time_block.text
            else:
                time = ''

            mark_blocks = lesson.find_all('div', {'class': 'dnevnik-mark__value'})
            marks = []
            if not mark_blocks is None:
                marks = [
                    {'mark': int(mark_block['value']),
                     'description': mark_block['mcomm'] if 'mcomm' in mark_block else ''
                     }
                    for mark_block in mark_blocks
                ]

            hometask_blocks = lesson.find_all('div', {'class': 'dnevnik-lesson__task'})
            hometask = []
            if not hometask_blocks is None:
                for hometask_block in hometask_blocks:
                    description = clear(hometask_block.find_all(text=True)[1])

                    attachment_block = hometask_block.find('div', {'class': 'dnevnik-lesson__attach'})
                    attachment = []
                    if not attachment_block is None:
                        attachment_block_as = attachment_block.find_all('a', {'class': 'button'})
                        attachment = [{'url': attachment['href'], 'file_name': attachment['title']}
                                      for attachment in attachment_block_as]
                    hometask.append({'description': description, 'attachment': attachment})
            # TODO: ссылки в тексте hometask

            result['lessons'].append({
                'number': number,
                'subject': subject,
                'time': time,
                'marks': marks,
                'hometask': hometask
            })

        return result

    def _get_days_from_diary_page(self, page_url):
        page = self.ej.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        days_block = soup.find('div', {'class': 'dnevnik'})
        days = days_block.find_all('div', {'class': 'dnevnik-day'})

        return days

    def get_day(self, day: str, week: int = 0) -> object:
        """
        Позволяет получить страницу дневника за определенный день

        :param day: День недели (monday..sunday)
        :type day: str
        
        :param week: Неделя.
        По умолчанию - текущая неделя (0)
        n: на n недель вперед
        -n: на n недель назад
        :type week: int
        """

        if day not in _DAYS_OF_THE_WEEK:
            raise RuntimeError('Unknown day of the week')

        days = self._get_days_from_diary_page(f'https://{self.school}.{_BASE_DOMAIN}{_DIARY}/week.{str(-week)}')

        try:
            day_block = days[_DAYS_OF_THE_WEEK.index(day)]
        except IndexError:
            raise RuntimeError(f'There is no {day} in the eljur diary')

        return self._parse_day_block(day_block)

    def get_week(self, week: int = 0) -> list:
        """
        Позволяет получить список дней в дневнике за неделю

        :param week: Неделя.
        По умолчанию - текущая неделя (0)
        n: на n недель вперед
        -n: на n недель назад
        :type week: int
        """

        days = self._get_days_from_diary_page(f'https://{self.school}.{_BASE_DOMAIN}{_DIARY}/week.{str(-week)}')

        week = []

        def parse(day):
            week.append(self._parse_day_block(day))

        thread_pool = []
        for day_block in days:
            thread = threading.Thread(target=parse, args=(day_block,))
            thread_pool.append(thread)
            thread.start()
        for thread in thread_pool:
            thread.join()

        return week
