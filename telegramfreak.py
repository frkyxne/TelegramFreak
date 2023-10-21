import telebot
import config
import constants
from utilclasses import UserRequest, BotMessageData


class TelegramFreak:
    def __init__(self):
        self.__bot = telebot.TeleBot(config.BOT_TOKEN)
        self.__update_offset = None
        self.__supported_commands = []

    @property
    def supported_commands(self) -> [str]:
        """
        :returns: Array of supported commands texts.
        """
        return self.__supported_commands

    @supported_commands.setter
    def supported_commands(self, value: [str]):
        """
        Sets supported commands.

        :param value: Array of supported commands texts starting with "/".
        """
        self.__supported_commands = value

    def send_to_group(self, BotMessageData):

    def reply_to_message(self, reply_data: BotMessageData):
        """
        Sends a reply to user message with given text.

        :param reply_data: Reply message data. It must have replying message, otherwise exception will be raised.
        """
        if reply_data.reply_message is None:
            raise Exception(f'{constants.CONSOLE_PREFIX} reply_to_message() was called with empty reply message.')

        if reply_data.reply_message.chat.type == 'private':
            self.__bot.send_message(chat_id=reply_data.reply_message.chat.id, text=reply_data.reply_text,
                                    reply_markup=self.__get_keyboard_from_commands(reply_data.reply_variants))
        else:
            self.__bot.reply_to(message=reply_data.reply_message, text=reply_data.reply_text)

    def get_unserviced_commands(self) -> [UserRequest]:
        """
        Gets and prints telegram user's unserviced commands.

        If bot mod is private, method does not return commands from users which are not in whitelist. To these users
        bot sends a message with denial of access. If user's command is not supported, replies with error.
        :returns: Array of UserRequest only with supported commands.
        """
        user_requests = []

        unread_messages = self.__get_unread_messages()

        if unread_messages is None:
            return

        for message in unread_messages:
            user_requests.append(self.__get_user_request_from_message(user_message=message))

        supported_user_requests = []

        for user_request in user_requests:
            user_id = user_request.message.from_user.id

            if config.BOT_MOD == constants.BOT_MOD_PRIVATE and user_id not in config.WHITE_LIST_IDS:
                self.reply_to_message(BotMessageData(reply_text='This bot is private. You are not in whitelist.',
                                                     replying_message=user_request.message))
            elif user_request.command is None and user_request.message.chat.type == 'private':
                self.reply_to_message(BotMessageData(reply_text=f'Command was not recognized.',
                                                     replying_message=user_request.message))
            elif user_request.command not in self.__supported_commands:
                self.reply_to_message(BotMessageData(reply_text=f'Command "{user_request.command}" is not supported',
                                                     replying_message=user_request.message))
            else:
                supported_user_requests.append(user_request)

        return user_requests

    def __get_unread_messages(self) -> [telebot.types.Message]:
        """
        Gets and prints telegram unread messages.

        :returns: Array of messages or None, if exception occurred.
        """
        try:
            updates = self.__bot.get_updates(offset=self.__update_offset, timeout=1, allowed_updates=['message'])
        except Exception as exception:
            print(f'{constants.CONSOLE_PREFIX} During getting update exception occurred: {exception}')
            return None

        unread_messages = []

        for update in updates:
            unread_messages.append(update.message)
            TelegramFreak.__print_message(message=update.message, is_receiving=True)
            self.__update_offset = update.update_id + 1

        return unread_messages

    @staticmethod
    def __get_user_request_from_message(user_message: telebot.types.Message) -> UserRequest:
        """
        Parses user's message to UserRequest.

        :param user_message: Message to parse to UserRequest.
        :returns: UserRequest.
        """
        if user_message.text is None:
            return UserRequest(message=user_message)

        command = None if user_message.text[0] != '/' else user_message.text.split()[0]
        command_args = None if command is None else user_message.text.replace(f'{command} ', '').split()
        return UserRequest(message=user_message, command=command, command_args=command_args)

    @staticmethod
    def __print_message(message: telebot.types.Message, is_receiving: False):
        """
        Prints received or sent telegram message into console.

        :param message: message to print.
        :param is_receiving: does bot receive or send message?
        :returns: None
        """
        message_text = '{content}' if message.text is None else message.text.replace('\n', '')

        if len(message_text) > 40:
            message_text = f'{message_text[0:20]} "..." {message_text[-21:-1]}'

        user_name = f'{message.from_user.username}(id{message.from_user.id})'
        bot_name = 'telegramfreak'
        sender_data = user_name if is_receiving else bot_name
        receiver_data = bot_name if is_receiving else user_name

        print(f'{constants.CONSOLE_PREFIX} {sender_data}: "{message_text}" -> {receiver_data}')

    @staticmethod
    def __get_keyboard_from_commands(commands: [str]) -> telebot.types.ReplyKeyboardMarkup:
        """
        Parses commands array into ReplyKeyBoardMarkup.

        :param commands: Commands to parse.
        :returns: Parsed ReplyKeyBoardMarkup
        """

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_count = len(commands) // constants.REPLY_KEYBOARD_BUTTONS_IN_ROW

        if len(commands) % constants.REPLY_KEYBOARD_BUTTONS_IN_ROW != 0:
            row_count += 1

        for row_index in range(row_count):
            row_buttons = []

            for column_index in range(constants.REPLY_KEYBOARD_BUTTONS_IN_ROW):
                command_index = row_index * constants.REPLY_KEYBOARD_BUTTONS_IN_ROW + column_index
                row_buttons.append(telebot.types.KeyboardButton(commands[command_index]))

            keyboard.row(*row_buttons)

        return keyboard


if __name__ == '__main__':
    bot = TelegramFreak()
    bot.menu_commands = ['/seks']
    bot.supported_commands = ['/seks', 'qwe']
    while True:
        bot.get_unserviced_commands()
