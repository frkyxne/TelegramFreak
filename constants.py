class BotHost:
    BOT_HOST_SUCCESS_NOTIFICATION = f'Bot was successfully hosted and now online.\n{"=" * 52}'
    BOT_HOST_FAILURE_NOTIFICATION = 'Failed to host bot.'
    BOT_KILLING_NOTIFICATION = f'\n{"=" * 12}\nKilling bot.'


class Commands:
    CREATING_REQUEST = 'Creating new request.'
    DELETING_EDITING_REQUEST = 'Closing not created request.'
    NO_EDITING_REQUEST_EXCEPTION = 'There is no editing requests by your id.'

    # Fast reply commands
    START_COMMAND = '/start'
    HELP_COMMAND = '/help'
    MY_BIO_COMMAND = '/my_bio'
    MUSIC_COMMAND = '/music'

    FAST_REPLY_COMMANDS = \
        [
            START_COMMAND,
            HELP_COMMAND,
            MY_BIO_COMMAND,
            MUSIC_COMMAND
        ]

    # System commands
    ABORT_COMMAND = '/abort'

    # Request commands
    REMIND_COMMAND = '/remind'

    REQUEST_COMMANDS = \
        [
            REMIND_COMMAND,
        ]


class RemindRequest:
    TODAY_TEXT = 'today'
    TOMORROW_TEXT = 'tomorrow'

    DAYS_TEXTS = \
        [
            TODAY_TEXT,
            TOMORROW_TEXT
        ]

    DAY_SELECT = 'When do you want me to remind you?'
    TIME_SELECT = 'Ok, now write time in HH:MM format.'
    TEXT_SELECT = 'Write text of reminder.'


class Reminders:
    REMINDERS_FOLDER = 'F:/Code/GitHubRepositories/TelegramFreak/Reminders'
    WAITING_TIME_STATUS = 'Waiting time'
    NOTIFIED_STATUS = 'Notified'

    FAILED_TO_SET_STATUS_EXCEPTION = 'Failed to set status of reminder'


WRONG_SYNTAX_EXCEPTION = 'Wrong syntax.'
TOKEN_PATH = 'F:/Code/GitHubRepositories/TelegramFreak/Fast Replies/bot_token.txt'
KILL_CODE_PATH = 'F:/Code/GitHubRepositories/TelegramFreak/Fast Replies/kill_code.txt'
LOGS_FOLDER = 'F:/Code/GitHubRepositories/TelegramFreak/Logs'
