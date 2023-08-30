import datetime
import telebot
import io
import constants


class UserRequest:
    user_id: int


class RemindRequest(UserRequest):
    alarm_day: datetime.datetime.date
    alarm_time: datetime.datetime.time
    alarm_text: str

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.alarm_time = datetime.datetime.today()
        self.alarm_text = 'default alarm text'


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
        help_button = telebot.types.KeyboardButton(constants.HELP_COMMAND)
        bio_button = telebot.types.KeyboardButton(constants.MY_BIO_COMMAND)
        markup.row(help_button, bio_button)
        remind_button = telebot.types.KeyboardButton(constants.REMIND_COMMAND)
        greet_button = telebot.types.KeyboardButton(constants.GREET_COMMAND)
        markup.row(remind_button, greet_button)
        return markup

    @staticmethod
    def get_day_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        today_button = telebot.types.KeyboardButton(constants.TODAY_TEXT)
        tomorrow = telebot.types.KeyboardButton(constants.TOMORROW_TEXT)
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
        return supplement_request(message=message, editing_request=already_created_request)


def get_command_response(message: telebot.types.Message) -> BotResponse:
    command = message.text.lower()

    # User is not supplementing request, recognise command

    if command in constants.FAST_REPLY_COMMANDS:
        return get_quick_reply(message)
    elif command in constants.REQUEST_COMMANDS:
        new_request = create_request(message)

        if new_request is not None:
            EditingRequests.append(new_request)
            return supplement_request(message=message, editing_request=new_request)

    return BotResponse(chat_id=message.from_user.id, text=f'Command "{message.text}" is not supported',
                       reply_keyboard=KeyboardMarkupCreator.get_menu_keyboard())


def get_quick_reply(message: telebot.types.Message) -> BotResponse:
    # Get reply text

    command = message.text.lower()

    if command in [constants.START_COMMAND, constants.HELP_COMMAND]:
        reply = io.open(f'Fast Replies/{command}.txt', encoding="utf-8").read()
    elif command == constants.MY_BIO_COMMAND:
        reply = str(message.from_user)
        reply = reply.replace('{', '').replace('}', '')
        reply = reply.replace("'", '').replace(', ', '\n')
    else:
        reply = f'Quick reply for "{message.text}" command is not supported'

    return BotResponse(chat_id=message.chat.id, text=reply, reply_keyboard=KeyboardMarkupCreator.get_menu_keyboard())


def create_request(message: telebot.types.Message) -> UserRequest:
    request_command = message.text.lower()

    if request_command == constants.REMIND_COMMAND:
        return RemindRequest(message.from_user.id)
    elif request_command == constants.GREET_COMMAND:
        return GreetRequest(message.from_user.id)


def supplement_request(message: telebot.types.Message, editing_request) -> BotResponse:
    def handle_remind_request() -> BotResponse:
        message_text = message.text.lower()

        if message_text == constants.REMIND_COMMAND:
            return BotResponse(chat_id=message.chat.id, text=constants.REMINDER_DAY_SELECT,
                               reply_keyboard=KeyboardMarkupCreator.get_day_keyboard())
        elif message_text in constants.DAYS_TEXTS:

            today = datetime.date.today()

            if message_text == constants.TODAY_TEXT:
                editing_request.alarm_day = today
                print("today")
            elif message_text == constants.TOMORROW_TEXT:
                editing_request.alarm_day = today + datetime.timedelta(days=1)
                print("tomorrow")
            else:
                return BotResponse(chat_id=message.from_user.id, text=constants.WRONG_SYNTAX_ERROR,
                                   reply_keyboard=KeyboardMarkupCreator.get_day_keyboard())

        else:
            return BotResponse(chat_id=message.from_user.id, text=constants.WRONG_SYNTAX_ERROR,
                               reply_keyboard=KeyboardMarkupCreator.get_day_keyboard())

    if type(editing_request) == RemindRequest:
        return handle_remind_request()
    else:
        return BotResponse(chat_id=message.chat.id, text=f'"{type(editing_request)}" type is not supported')
