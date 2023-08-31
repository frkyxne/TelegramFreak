import datetime
import telebot
import io
import constants


class RemindRequest:
    def __init__(self, user_id: int):
        self.__user_id = user_id
        self.__reminder_date = datetime.date
        self.__reminder_time = datetime.time
        self.__reminder_text = ''
        self.__date_is_set = False
        self.__time_is_set = False

    @property
    def user_id(self):
        return self.__user_id

    @property
    def reminder_date(self):
        return self.__reminder_date

    @reminder_date.setter
    def reminder_date(self, date: datetime.datetime.date):
        self.__reminder_date = date
        self.__date_is_set = True

    @property
    def reminder_time(self):
        return self.__reminder_time

    @reminder_time.setter
    def reminder_time(self, time: datetime.datetime.time):
        self.__reminder_time = time
        self.__time_is_set = True

    @property
    def reminder_text(self):
        return self.__reminder_text

    @reminder_text.setter
    def reminder_text(self, text: str):
        self.__reminder_text = text

    @property
    def date_is_set(self):
        return self.__date_is_set

    @property
    def time_is_set(self):
        return self.__time_is_set


class GreetRequest:
    def __init__(self, user_id: int):
        self.user_id = user_id


EditingRequests = []


class BotResponse:
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.__messages = []
        self.__reply_keyboard = ReplyKeyboardCreator.get_menu_keyboard()

    @property
    def messages(self):
        return self.__messages

    @property
    def reply_keyboard(self):
        return self.__reply_keyboard

    @reply_keyboard.setter
    def reply_keyboard(self, reply_keyboard: telebot.types.ReplyKeyboardMarkup):
        self.__reply_keyboard = reply_keyboard

    def add_message(self, text: str):
        self.messages.append(text)


class ReplyKeyboardCreator:
    @staticmethod
    def get_menu_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        help_button = telebot.types.KeyboardButton(constants.Commands.HELP_COMMAND)
        bio_button = telebot.types.KeyboardButton(constants.Commands.MY_BIO_COMMAND)
        markup.row(help_button, bio_button)
        remind_button = telebot.types.KeyboardButton(constants.Commands.REMIND_COMMAND)
        greet_button = telebot.types.KeyboardButton(constants.Commands.GREET_COMMAND)
        markup.row(remind_button, greet_button)
        return markup

    @staticmethod
    def get_day_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        today_button = telebot.types.KeyboardButton(constants.RemindRequest.TODAY_TEXT)
        tomorrow = telebot.types.KeyboardButton(constants.RemindRequest.TOMORROW_TEXT)
        markup.row(today_button, tomorrow)
        return markup


def get_response(message: telebot.types.Message) -> BotResponse:
    # Does user have editing request?
    already_created_request = None
    command = message.text.lower()
    response = BotResponse(message.from_user.id)

    # Does user have editing request?
    for editing_request in EditingRequests:
        if editing_request.user_id == message.from_user.id:
            already_created_request = editing_request

    # User does not have editing request
    if already_created_request is None:

        if command in constants.Commands.FAST_REPLY_COMMANDS:
            # User command is fast reply
            return get_quick_reply(message, response)
        elif command == constants.Commands.ABORT_COMMAND:
            response.add_message(constants.Commands.NO_EDITING_REQUEST_ERROR)
            return response
        elif command in constants.Commands.REQUEST_COMMANDS:
            # User command is request
            new_request = create_request(message)
            EditingRequests.append(new_request)
            response.add_message(constants.Commands.CREATING_REQUEST)
            return supplement_request(message=message, bot_response=response, editing_request=new_request)
        else:
            # Command is not supported, return error
            response.add_message(f'Command "{message.text}" is not supported')
            response.reply_keyboard = ReplyKeyboardCreator.get_menu_keyboard()
            return response

    # User has editing request
    else:
        if command == constants.Commands.ABORT_COMMAND:
            EditingRequests.remove(already_created_request)
            response.add_message(constants.Commands.DELETING_EDITING_REQUEST)
            return response
        else:
            return supplement_request(message=message, editing_request=already_created_request, bot_response=response)


def get_quick_reply(message: telebot.types.Message, bot_response: BotResponse) -> BotResponse:
    command = message.text.lower()

    if command in [constants.Commands.START_COMMAND, constants.Commands.HELP_COMMAND]:
        # Read fast reply from file
        reply = io.open(f'Fast Replies/{command}.txt', encoding="utf-8").read()
    elif command == constants.Commands.MY_BIO_COMMAND:
        # Parse fast reply from user's data
        reply = str(message.from_user)
        reply = reply.replace('{', '').replace('}', '')
        reply = reply.replace("'", '').replace(', ', '\n')
    else:
        # Quick reply command is not supported
        reply = f'Quick reply for "{message.text}" command is not supported'

    bot_response.add_message(reply)
    bot_response.reply_keyboard = ReplyKeyboardCreator.get_menu_keyboard()
    return bot_response


def create_request(message: telebot.types.Message):
    request_command = message.text.lower()

    if request_command == constants.Commands.REMIND_COMMAND:
        return RemindRequest(message.from_user.id)
    elif request_command == constants.Commands.GREET_COMMAND:
        return GreetRequest(message.from_user.id)


def supplement_request(message: telebot.types.Message, editing_request, bot_response: BotResponse) -> BotResponse:
    def handle_remind_request() -> BotResponse:
        message_text = message.text.lower()

        if editing_request.date_is_set is False and editing_request.time_is_set is False:

            if message_text == constants.Commands.REMIND_COMMAND:
                # Ask user to select day
                bot_response.add_message(constants.RemindRequest.DAY_SELECT)
                bot_response.reply_keyboard = ReplyKeyboardCreator.get_day_keyboard()
                return bot_response
            else:
                # Try to set date
                if message_text in constants.RemindRequest.DAYS_TEXTS:
                    today = datetime.date.today()

                    # Write down day
                    if message_text == constants.RemindRequest.TODAY_TEXT:
                        editing_request.reminder_date = today
                    elif message_text == constants.RemindRequest.TOMORROW_TEXT:
                        editing_request.reminder_date = today + datetime.timedelta(days=1)

                    bot_response.add_message(constants.RemindRequest.TIME_SELECT)
                    bot_response.reply_keyboard = None
                    return bot_response

                else:
                    # Wrong syntax, return error
                    bot_response.add_message(constants.WRONG_SYNTAX_ERROR)
                    bot_response.reply_keyboard = ReplyKeyboardCreator.get_day_keyboard()
                    return bot_response

        elif editing_request.date_is_set is True and editing_request.time_is_set is False:
            # Try to set time
            try:
                hour, minutes = message_text.split(':')
                hour = int(hour)
                minutes = int(minutes)
            except Exception:
                # Wrong syntax, return error
                bot_response.add_message(constants.WRONG_SYNTAX_ERROR)
                bot_response.reply_keyboard = ReplyKeyboardCreator.get_day_keyboard()
                return bot_response

            editing_request.reminder_time = datetime.time(hour=hour, minute=minutes)
            bot_response.add_message(constants.RemindRequest.TEXT_SELECT)
            bot_response.reply_keyboard = None
            return bot_response

        else:
            editing_request.reminder_text = message.text
            EditingRequests.remove(editing_request)
            bot_response.add_message(f'Alright, I will reminder you {editing_request.reminder_date} in '
                                     f'{str(editing_request.reminder_time)[0:-3]} oclock about '
                                     f'"{editing_request.reminder_text}"')
            return bot_response

    if type(editing_request) == RemindRequest:
        return handle_remind_request()
    else:
        bot_response.add_message(f'"{type(editing_request)}" type is not supported')
        return bot_response
