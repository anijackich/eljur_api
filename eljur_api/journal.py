from bs4 import BeautifulSoup

from config import _BASE_DOMAIN, _JOURNAL, _RESULTS, _QUARTER, _QUARTERS


class ElJournal(object):
    def __init__(self, ej):
        self.ej = ej.ej
        self.school = ej.school

    def _get_blocks(self, page_url):
        page = self.ej.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        subjects = soup.find('div', id='g0_fio').find_all('div', {'class': 'cell'})
        marks = soup.find('div', id='g0_marks')
        avgs = soup.find('div', id='g0_avg')

        return subjects, marks, avgs

    def _parse_to_avg(self, subject, avg_block):

        print(str(avg_block))

        avg = avg_block.find('div', {'class': 'cell', 'name': subject})

        return avg.text

    def _parse_to_marks(self, subject, subject_block, marks_block):

        subjects = [subject.text for subject in subject_block]

        if subject not in subjects:
            raise RuntimeError(f'There is no {subject} in eljur journal')

        subject_index = subjects.index(subject)

        result = []
        s = 0
        while True:
            try:
                mark = marks_block.find_all('div', {'class': 'cells_marks'})[s].find_all('div', {'class': 'cell-data'})[subject_index].text
            except IndexError:
                break
            if not mark == u'\xa0':
                result.append(mark)
            else:
                break
            s += 1

        return result

    def get_subject_marks(self, subject, quarter: int = 0) -> object:
        """
        Позволяет получить текущие оценки по указанному предмету

        :param subject: Предмет (как указан в журнале, учитывая регистр)
        :type subject: str

        :param quarter: Четверть
        Принимает номер четверти от 1 до 4
        По умолчанию - текущая четверть (0)
        :type quarter: int
        """

        if quarter not in range(0, 5):
            raise RuntimeError(f'Wrong quarter {quarter}')

        if quarter != 0:
            quarter = _QUARTERS[quarter-1]
        else:
            quarter = ''

        subjects_block, marks_block, avg_block = self._get_blocks(
            f'https://{self.school}.{_BASE_DOMAIN}{_JOURNAL}{_QUARTER.format(quarter)}')

        return {'subject': subject,
                'quarter': quarter,
                'marks': self._parse_to_marks(subject, subjects_block, marks_block)
                # 'average_mark': self._parse_to_avg(subject, avg_block)
                }

    def get_subject_results(self, subject) -> object:
        """
        Позволяет получить итоговые оценки

        :param subject: Предмет (как указан в журнале, учитывая регистр)
        :type subject: str
        """

        subjects_block, marks_block, avg_block = self._get_blocks(
            f'https://{self.school}.{_BASE_DOMAIN}{_RESULTS}')
        marks = self._parse_to_marks(subject, subjects_block, marks_block)

        return {'subject': subject,
                'marks': marks[:-1],
                'final_mark': marks[-1]
                }
