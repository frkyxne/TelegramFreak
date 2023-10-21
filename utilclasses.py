import telebot.types as teletypes


class UserRequest:
    def __init__(self, message: teletypes.Message, command: str = None, command_args: [str] = None):
        self.__command = command
        self.__command_args = command_args
        self.__message = message

    @property
    def command(self):
        return self.__command

    @property
    def commands_args(self):
        return self.__command_args

    @property
    def message(self):
        return self.__message


class BotMessageData:
    def __init__(self, reply_text: str, replying_message: teletypes.Message = None,
                 reply_markup: [str] = None):
        self.__reply_text = reply_text
        self.__user_message = replying_message
        self.__reply_markup = reply_markup

    @property
    def reply_text(self):
        return self.__reply_text

    @property
    def reply_message(self):
        return self.__user_message

    @property
    def reply_variants(self):
        return self.__reply_markup
