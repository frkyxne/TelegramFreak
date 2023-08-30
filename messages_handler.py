import datetime
from datetime import datetime as date_and_time
from datetime import date
from datetime import time
import telebot
import io


class UserRequest:
    user_id: int


class RemindRequest(UserRequest):

    alarm_time: date_and_time
    alarm_text: str

    def __init__(self, user_id: int):
        self.user_id = user_id


class GreetRequest(UserRequest):
    
    def __init__(self, user_id: int):
        self.user_id = user_id


EditingRequests = []


class BotResponse:

    chat_id: int
    text: str
    reply_markup: telebot.types.ReplyKeyboardMarkup

    def __init__(self, chat_id: int, text: str, reply_keyboard: telebot.types.ReplyKeyboardMarkup = None):
        self.chat_id = chat_id
        self.text = text
        self.reply_markup = reply_keyboard


class KeyboardMarkupCreator:
    @staticmethod
    def get_menu_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        help_button = telebot.types.KeyboardButton(HELP_COMMAND)
        bio_button = telebot.types.KeyboardButton(MY_BIO_COMMAND)
        markup.row(help_button, bio_button)
        remind_button = telebot.types.KeyboardButton(REMIND_COMMAND)
        greet_button = telebot.types.KeyboardButton(GREET_COMMAND)
        markup.row(remind_button, greet_button)
        return markup

    @staticmethod
    def get_day_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        today_button = telebot.types.KeyboardButton(TODAY_TEXT)
        tomorrow = telebot.types.KeyboardButton(TOMORROW_TEXT)
        markup.row(today_button, tomorrow)
        return markup


def get_response(message: telebot.types.Message) -> BotResponse:

    # Does user have editing request?

    already_created_request = None

    for editing_request in EditingRequests:
        if editing_request.user_id == message.from_user.id:
            already_created_request = editing_request

    if already_created_request is None:
        return get_command_response(message)
    else:
        supplement_request(already_created_request, message)


START_COMMAND = '/start'
HELP_COMMAND = '/help'
MY_BIO_COMMAND = '/my_bio'

FAST_REPLY_COMMANDS = \
    [
        START_COMMAND,
        HELP_COMMAND,
        MY_BIO_COMMAND
    ]

REMIND_COMMAND = '/remind'
GREET_COMMAND = '/greet'

REQUEST_COMMANDS = \
    [
        REMIND_COMMAND,
        GREET_COMMAND
    ]

TODAY_TEXT = 'today'
TOMORROW_TEXT = 'tomorrow'

DAYS_TEXTS = \
    [
        TODAY_TEXT,
        TOMORROW_TEXT
    ]


def get_wrong_syntax_response(chat_id: int, reply_keyboard: telebot.types.ReplyKeyboardMarkup) -> BotResponse:
    expected_user_response = []

    for button in reply_keyboard.keyboard:
        print(button)

    return BotResponse(chat_id=chat_id,text='Wrong syntax', reply_keyboard=reply_keyboard)


def get_command_response(message: telebot.types.Message) -> BotResponse:
    possible_command = message.text.lower()

    # Check if user is supplementing request

    for editing_request in EditingRequests:
        if editing_request.user_id == message.from_user.id:
            return supplement_request(message=message, editing_request=editing_request)

    # User is not supplementing request, recognise command

    if possible_command in FAST_REPLY_COMMANDS:
        return get_quick_reply(message)
    elif possible_command in REQUEST_COMMANDS:
        new_request = create_request(message)
        
        if new_request is not None:
            EditingRequests.append(new_request)
            return supplement_request(message=message, editing_request=new_request)
    
    return BotResponse(chat_id=message.from_user.id, text=f'Command "{message.text}" is not supported',
                       reply_keyboard=KeyboardMarkupCreator.get_menu_keyboard())


def get_quick_reply(message: telebot.types.Message) -> BotResponse:

    # Get reply text

    command = message.text.lower()

    if command in [START_COMMAND, HELP_COMMAND]:
        reply = io.open(f'Fast Replies/{command}.txt', encoding="utf-8").read()
    elif command == MY_BIO_COMMAND:
        reply = str(message.from_user)
        reply = reply.replace('{', '').replace('}', '')
        reply = reply.replace("'", '').replace(', ','\n')
    else:
        reply = f'Quick reply for "{message.text}" command is not supported'

    return BotResponse(chat_id=message.chat.id, text=reply, reply_keyboard=KeyboardMarkupCreator.get_menu_keyboard())


def create_request(message: telebot.types.Message) -> UserRequest:
    request_command = message.text.lower()
    
    if request_command == REMIND_COMMAND:
        return RemindRequest(message.from_user.id)
    elif request_command == GREET_COMMAND:
        return GreetRequest(message.from_user.id)


def supplement_request(message: telebot.types.Message, editing_request) -> BotResponse:
    if type(editing_request) == RemindRequest:
        message_text = message.text.lower()
        
        if message_text == REMIND_COMMAND:
            return BotResponse(chat_id=message.chat.id, text='When do you want me to remind you?',
                               reply_keyboard=KeyboardMarkupCreator.get_day_keyboard())
        elif message_text in DAYS_TEXTS:

            today = date.today()

            if message_text == TODAY_TEXT:
                editing_request.alarm_time.day = today
                print("today")
            elif message_text == TOMORROW_TEXT:
                editing_request.alarm_time.day = today + datetime.timedelta(days=1)
                print("tomorrow")
            else:
                return get_wrong_syntax_response(message.from_user.id, KeyboardMarkupCreator.get_day_keyboard())

        else:
            return get_wrong_syntax_response(message.from_user.id, KeyboardMarkupCreator.get_day_keyboard())
    else:
        return BotResponse(chat_id=message.chat.id, text=f'"{type(editing_request)}" type is not supported')
