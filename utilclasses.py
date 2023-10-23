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
    def __init__(self, message_text: str, chat_id: str = None, replying_message: teletypes.Message = None,
                 reply_markup: [str] = None):
        self.__message_text = message_text
        self.__user_message = replying_message
        self.__reply_markup = reply_markup
        self.__chat_id = chat_id

    @property
    def message_text(self):
        return self.__message_text

    @property
    def replying_message(self):
        return self.__user_message

    @property
    def reply_variants(self):
        return self.__reply_markup

    @property
    def chat_id(self):
        return self.__chat_id
