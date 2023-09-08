import datetime

import constants


class Reminder:
    def __init__(self, user_id: int, date: datetime.date, time: datetime.time, text: str):
        self.__user_id = user_id
        self.__reminder_date = date
        self.__reminder_time = time
        self.__reminder_text = text

    @property
    def user_id(self):
        return self.__user_id

    @property
    def reminder_date(self):
        return self.__reminder_date

    @property
    def reminder_time(self):
        return self.__reminder_time

    @property
    def reminder_text(self):
        return self.__reminder_text

    def to_string(self) -> str:
        return f'{self.__user_id}/{self.__reminder_date}/{self.__reminder_time}/{self.__reminder_text}'

    @staticmethod
    def from_string(reminder_string: str):
        split = reminder_string.split('/')

        try:
            # Get date from split
            date_string = split[1].split('-')
            reminder_date = datetime.date(year=int(date_string[0]), month=int(date_string[1]), day=int(date_string[2]))

            # Get time from split
            time_string = split[2].split(':')
            reminder_time = datetime.time(hour=int(time_string[0]), minute=int(time_string[1]))

            return Reminder(user_id=int(split[0]), date=reminder_date, time=reminder_time, text=split[3])
        except Exception:
            return None


def write_down_reminder(new_reminder: Reminder) -> None:
    reminders_file = open(f'{constants.Reminders.REMINDERS_FOLDER}/{new_reminder.reminder_date}.txt', 'a')
    reminders_file.write(f'\n{new_reminder.to_string()}/{constants.Reminders.WAITING_TIME_STATUS}')
    reminders_file.close()


def get_all_reminders(reminders_date: datetime.date) -> []:
    try:
        reminders_strings = open(f'{constants.Reminders.REMINDERS_FOLDER}/{reminders_date}.txt').readlines()
    except Exception:
        return None

    reminders = []

    for line in reminders_strings:
        reminder = Reminder.from_string(line)

        if reminder is not None:
            reminders.append(reminder)

    return reminders


def set_reminder_status(reminder: Reminder, new_status: str) -> None:
    try:
        reminders_strings = open(f'{constants.Reminders.REMINDERS_FOLDER}/{reminder.reminder_date}.txt').readlines()
    except Exception:
        print(constants.Reminders.FAILED_TO_SET_STATUS_EXCEPTION)
        return None

    new_reminder_strings = []

    for reminders_string in reminders_strings:
        reminders_string_without_status = (
            reminders_string.replace(f'/{constants.Reminders.WAITING_TIME_STATUS}', ''))
        reminders_string_without_status = (
            reminders_string_without_status.replace(f'/{constants.Reminders.NOTIFIED_STATUS}', ''))
        reminders_string_without_status = reminders_string_without_status.replace('\n', '')

        if reminders_string_without_status == reminder.to_string():
            new_reminder_strings.append(f'{reminder.to_string()}/{new_status}\n')
        else:
            new_reminder_strings.append(reminders_string)

    new_reminder_strings_file = open(f'{constants.Reminders.REMINDERS_FOLDER}/{reminder.reminder_date}.txt', 'w+')
    new_reminder_strings_file.writelines(new_reminder_strings)
    new_reminder_strings_file.close()


set_reminder_status(get_all_reminders(datetime.date.today())[1], new_status=constants.Reminders.NOTIFIED_STATUS)

