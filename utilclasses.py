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


class BotReply:
    def __init__(self, reply_text: str, replying_message: teletypes.Message, reply_variants: [str]):
        self.__reply_text = reply_text
        self.__replying_message = replying_message
        self.__reply_variants = reply_variants

    @property
    def reply_text(self):
        return self.__reply_text

    @property
    def replying_message(self):
        return self.__replying_message

    @property
    def reply_variants(self):
        return self.__reply_variants


class BotMessage:
    def __init__(self, message_text: str, target_chat: teletypes.Chat):
        self.__message_text = message_text
        self.__message_chat = target_chat

    @property
    def message_text(self):
        return self.__message_text

    @property
    def message_chat(self):
        return self.__message_chat
