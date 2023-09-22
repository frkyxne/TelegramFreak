import datetime
import os
from enum import Enum
import constants


class Reminder:
    class Status(Enum):
        SETTING_DATE = 0
        SETTING_TIME = 1
        SETTING_TEXT = 2
        WAITING_TIME = 3
        NOTIFIED = 4

    def __init__(self, user_id: int, date: datetime.date = None, time: datetime.time = None, text: str = None,
                 status: Status = None):
        self.__user_id = user_id
        self.__reminder_date = date
        self.__reminder_time = time
        self.__reminder_text = text
        self.__status = self.Status.SETTING_DATE if status is None else status

    def __eq__(self, other) -> bool:
        if type(other) != self.__class__:
            return False

        if other.user_id != self.__user_id or other.reminder_date != self.__reminder_date:
            return False

        if other.reminder_time != self.__reminder_time or other.reminder_text != self.__reminder_text:
            return False

        return True

    @property
    def user_id(self):
        return self.__user_id

    @property
    def reminder_date(self):
        return self.__reminder_date

    @reminder_date.setter
    def reminder_date(self, date: datetime.date):
        self.__reminder_date = date
        self.__status = self.Status.SETTING_TIME

    @property
    def reminder_time(self):
        return self.__reminder_time

    @reminder_time.setter
    def reminder_time(self, time: datetime.time):
        self.__reminder_time = time
        self.__status = self.Status.SETTING_TEXT

    @property
    def reminder_text(self):
        return self.__reminder_text

    @reminder_text.setter
    def reminder_text(self, text: str):
        self.__reminder_text = text
        self.__status = self.Status.WAITING_TIME

    @property
    def status(self):
        return self.__status

    def to_string(self) -> str:
        return (f'{self.__user_id}/{str(self.__reminder_date).replace("-", ".")}'
                f'/{str(self.__reminder_time)[0:-3]}/{self.__reminder_text}/{self.__status}')

    @staticmethod
    def from_string(reminder_string: str):
        split = reminder_string.split('/')

        try:
            # Get date from split
            date_string = split[1].split('.')
            reminder_date = datetime.date(year=int(date_string[0]), month=int(date_string[1]), day=int(date_string[2]))

            # Get time from split
            time_string = split[2].split(':')
            reminder_time = datetime.time(hour=int(time_string[0]), minute=int(time_string[1]))

            # Get status from split
            reminder_status = next(status for status in Reminder.Status if str(status) == split[-1])

            return Reminder(user_id=int(split[0]), date=reminder_date, time=reminder_time, text=split[3],
                            status=reminder_status)
        except Exception:
            return None


def get_file_name(date: str) -> str:
    return f'{constants.Reminders.REMINDERS_FOLDER}/{date}.txt'


def write_down_reminder(new_reminder: Reminder) -> None:
    reminders_file = open(get_file_name(str(new_reminder.reminder_date)), 'a')
    reminders_file.write(f'\n{new_reminder.to_string()}')
    reminders_file.close()


def write_new_status(reminder: Reminder, new_status: Reminder.Status):
    date_reminders = get_reminders_by_date(reminder.reminder_date)
    correct_one = next(r for r in date_reminders if r == reminder)
    date_reminders.remove(correct_one)
    date_reminders.append(Reminder(user_id=reminder.user_id, date=reminder.reminder_date, time=reminder.reminder_time,
                                   text=reminder.reminder_text, status=new_status))

    os.remove(get_file_name(str(reminder.reminder_date)))

    for r in date_reminders:
        write_down_reminder(r)


def get_reminders_by_date(date: datetime.date) -> [Reminder]:
    try:
        reminders_strings = open(get_file_name(str(date))).readlines()
    except Exception:
        return None

    reminders_strings = [line.replace('\n', '') for line in reminders_strings]

    reminders = [Reminder.from_string(line) for line in reminders_strings]
    return [r for r in reminders if r is not None]


def get_reminders_by_now() -> [Reminder]:
    today_reminders = get_reminders_by_date(date=datetime.date.today())

    if today_reminders is None:
        return []

    # HH:MM
    now_time = str(datetime.datetime.now()).split()[1].split('.')[0][0:-3]
    now_reminders = [reminder for reminder in today_reminders if str(reminder.reminder_time)[0:-3] == now_time]
    now_reminders = [reminder for reminder in now_reminders if reminder.status != Reminder.Status.NOTIFIED]

    return now_reminders


def get_today_overdue_reminders() -> [Reminder]:
    today_reminders = get_reminders_by_date(date=datetime.date.today())

    if today_reminders is None:
        return []

    # HH:MM
    now_time = str(datetime.datetime.now()).split()[1].split('.')[0][0:-3]
    now_split = now_time.split(':')
    now_hour, now_minute = int(now_split[0]), int(now_split[1])
    overdue_reminders = []

    for reminder in today_reminders:
        if reminder.status == Reminder.Status.NOTIFIED:
            continue

        reminder_split = str(reminder.reminder_time)[0:-3].split(':')
        reminder_hour, reminder_minute = int(reminder_split[0]), int(reminder_split[1])

        if reminder_hour < now_hour or (reminder_hour == now_hour and reminder_minute < now_minute):
            overdue_reminders.append(reminder)

    return overdue_reminders


