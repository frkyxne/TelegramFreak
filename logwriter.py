import constants
import datetime


class LogWriter:
    def __init__(self):
        self.__log = ''

    @property
    def log(self):
        return self.__log

    def add_line(self, line: str):
        line = f'{str(datetime.datetime.now())[11:-7]} {line}'
        print(line)
        self.__log += f'{line}\n'

    def add_lines(self, lines: [str]):
        for line in lines:
            self.add_line(line)

    def save_log(self):
        reminders_file = open(f'{constants.LOGS_FOLDER}/{datetime.date.today()}.txt', 'a')
        reminders_file.write(f'\n{self.__log}')
        reminders_file.close()
