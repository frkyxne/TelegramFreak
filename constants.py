class BotHost:
    BOT_HOST_SUCCESS_NOTIFICATION = 'Bot was successfully hosted and now online.'
    BOT_HOST_FAILURE_NOTIFICATION = 'Failed to host bot.'


class Commands:
    CREATING_REQUEST = 'Creating new request.'
    DELETING_EDITING_REQUEST = 'Closing not created request.'
    NO_EDITING_REQUEST_ERROR = 'There is no editing requests by your id.'

    # Fast reply commands
    START_COMMAND = '/start'
    HELP_COMMAND = '/help'
    MY_BIO_COMMAND = '/my_bio'

    FAST_REPLY_COMMANDS = \
        [
            START_COMMAND,
            HELP_COMMAND,
            MY_BIO_COMMAND
        ]

    # System commands
    ABORT_COMMAND = '/abort'

    # Request commands
    REMIND_COMMAND = '/remind'
    GREET_COMMAND = '/greet'

    REQUEST_COMMANDS = \
        [
            REMIND_COMMAND,
            GREET_COMMAND
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


WRONG_SYNTAX_ERROR = 'Wrong syntax.'
