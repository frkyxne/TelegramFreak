import telebot
import constants
import io
import remindersmaster
import datetime


class BotResponse:
    def __init__(self, user: telebot.types.User, text: str = None):
        self.user = user
        self.__reply_keyboard = ReplyKeyboardCreator.get_menu_keyboard()

        if text is None:
            self.__messages = []
        else:
            self.__messages = [text]

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
        music_button = telebot.types.KeyboardButton(constants.Commands.MUSIC_COMMAND)
        markup.row(remind_button, music_button)
        return markup

    @staticmethod
    def get_day_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        today_button = telebot.types.KeyboardButton(constants.RemindRequest.TODAY_TEXT)
        tomorrow_button = telebot.types.KeyboardButton(constants.RemindRequest.TOMORROW_TEXT)
        markup.row(today_button, tomorrow_button)
        abort_button = telebot.types.KeyboardButton(constants.Commands.ABORT_COMMAND)
        markup.row(abort_button)
        return markup

    @staticmethod
    def get_abort_keyboard() -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        abort_button = telebot.types.KeyboardButton(constants.Commands.ABORT_COMMAND)
        markup.row(abort_button)
        return markup


class MessagesHandler:
    def __init__(self):
        self.editing_requests = []

    def get_response_to_message(self, message: telebot.types.Message) -> BotResponse:
        message_text = message.text.lower()

        def get_fast_reply(fast_rely_command: str) -> str:
            if fast_rely_command == constants.Commands.START_COMMAND:
                reply = constants.FastRepliesContent.START_REPLY
            elif fast_rely_command == constants.Commands.HELP_COMMAND:
                reply = constants.FastRepliesContent.HELP_REPLY
            elif fast_rely_command == constants.Commands.KILL_COMMAND:
                reply = constants.System.KILL_CODE
            elif fast_rely_command == constants.Commands.MY_BIO_COMMAND:
                # Parse fast reply from user's data
                reply = str(message.from_user)
                reply = reply.replace('{', '').replace('}', '')
                reply = reply.replace("'", '').replace(', ', '\n')
            elif fast_rely_command == constants.Commands.MUSIC_COMMAND:
                reply = 'https://www.youtube.com/watch?v=rUxyKA_-grg'
            else:
                # Quick reply command is not supported
                reply = f'Quick reply for "{message.text}" command is not supported'

            return reply

        def create_request(request_command: str) -> object:
            if request_command == constants.Commands.REMIND_COMMAND:
                return remindersmaster.Reminder(user_id=message.from_user.id)

        def get_response_to_request(created_request, bot_response: BotResponse = None) -> BotResponse:
            if bot_response is None:
                bot_response = BotResponse(user=message.from_user)

            if type(created_request) is remindersmaster.Reminder:

                if created_request.status == remindersmaster.Reminder.Status.SETTING_DATE:

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
                                created_request.reminder_date = today
                            elif message_text == constants.RemindRequest.TOMORROW_TEXT:
                                created_request.reminder_date = today + datetime.timedelta(days=1)

                            bot_response.add_message(constants.RemindRequest.TIME_SELECT)
                            bot_response.reply_keyboard = None
                            return bot_response

                        else:
                            # Wrong syntax, return error
                            bot_response.add_message(constants.WRONG_SYNTAX_EXCEPTION)
                            bot_response.reply_keyboard = ReplyKeyboardCreator.get_day_keyboard()
                            return bot_response

                elif created_request.status == remindersmaster.Reminder.Status.SETTING_TIME:
                    # Try to set time
                    try:
                        hour, minutes = message_text.split(':')
                        hour, minutes = int(hour), int(minutes)
                    except Exception:
                        # Wrong syntax, return error
                        bot_response.add_message(constants.WRONG_SYNTAX_EXCEPTION)
                        bot_response.reply_keyboard = ReplyKeyboardCreator.get_day_keyboard()
                        return bot_response

                    created_request.reminder_time = datetime.time(hour=hour, minute=minutes)
                    bot_response.add_message(constants.RemindRequest.TEXT_SELECT)
                    bot_response.reply_keyboard = None
                    return bot_response

                else:
                    created_request.reminder_text = message.text.replace('/', '|')
                    self.editing_requests.remove(created_request)
                    remindersmaster.write_down_reminder(created_request)
                    bot_response.add_message(f'Alright, I will reminder you '
                                             f'{str(created_request.reminder_date).replace("-", ".")} in '
                                             f'{str(created_request.reminder_time)[0:-3]} oclock about '
                                             f'"{created_request.reminder_text}"')
                    return bot_response
            else:
                return BotResponse(user=message.from_user, text=f'Request type "{created_request}" is not supported')

        def get_response_to_command() -> BotResponse:
            # User command is fast reply, return fast reply.
            if message_text in constants.Commands.FAST_REPLY_COMMANDS:
                return BotResponse(user=message.from_user, text=get_fast_reply(message_text))
            # User is trying to abort not existing request, return error.
            elif message_text == constants.Commands.ABORT_COMMAND:
                return BotResponse(user=message.from_user, text=constants.Commands.NO_EDITING_REQUEST_EXCEPTION)
            # User command is request, creating one.
            elif message_text in constants.Commands.REQUEST_COMMANDS:
                new_request = create_request(message_text)
                self.editing_requests.append(new_request)
                response = BotResponse(user=message.from_user, text=constants.Commands.CREATING_REQUEST)
                return get_response_to_request(bot_response=response, created_request=new_request)
            # Command is not supported, return error.
            else:
                return BotResponse(user=message.from_user, text=f'Command "{message.text}" is not supported')

        # Does user have already created request?
        if len(self.editing_requests) > 0:
            already_created_request = next(request for request in self.editing_requests
                                           if request.user_id == message.from_user.id)
        else:
            already_created_request = None

        if already_created_request is None:
            return get_response_to_command()
        elif message_text == constants.Commands.ABORT_COMMAND:
            # User is aborting already created request
            self.editing_requests.remove(already_created_request)
            return BotResponse(user=message.from_user, text=constants.Commands.DELETING_EDITING_REQUEST)
        else:
            return get_response_to_request(created_request=already_created_request)
