import telebot
import config
import constants
from utilclasses import UserRequest, BotMessage, BotReply


class TelegramFreak:
    def __init__(self):
        self.__bot = telebot.TeleBot(config.BOT_TOKEN)
        self.send_to_groups(constants.BOT_NOTIFICATION_ACTIVATION)

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

        :param value: Array of supported commands. Commands must start with "/" and not have whitespace.
        """
        self.__supported_commands = value

    def send_message(self, message_data: BotMessage):
        """
        Sends message to specific chat.

        :param message_data: Data of message to send.
        """
        if message_data is None:
            raise Exception(f'{constants.CONSOLE_PREFIX} send_message() was called with NoneType.')

        try:
            self.__bot.send_message(text=message_data.message_text, chat_id=message_data.message_chat.id)
            self.__print_message(bot_message=message_data)
        except Exception as exception:
            print(f'{constants.CONSOLE_PREFIX} failed to send message. {exception}')

    def send_to_groups(self, message_text: str):
        """
        Sends message to all groups in config.
        """
        for group_id in config.BOT_GROUP_IDS:
            target_chat = telebot.types.Chat(id(group_id), type='group')
            self.send_message(message_data=BotMessage(message_text=message_text, target_chat=target_chat))

    def reply_to_message(self, reply_data: BotReply):
        """
        Sends a reply to user message with given text.

        :param reply_data: Reply message data. It must have replying message, otherwise exception will be raised.
        """
        if reply_data is None:
            raise Exception(f'{constants.CONSOLE_PREFIX} reply_to_message() was called with NoneType.')

        if reply_data.replying_message.chat.type == 'private':
            self.send_message(message_data=BotMessage(message_text=reply_data.reply_text,
                                                      target_chat=reply_data.replying_message.chat))
        else:
            try:
                self.__bot.reply_to(message=reply_data.replying_message, text=reply_data.reply_text)
            except Exception as exception:
                print(f'{constants.CONSOLE_PREFIX} failed to reply message. {exception}')

            self.__print_message(bot_reply=reply_data)

    def get_unserviced_requests(self) -> [UserRequest]:
        """
        Gets and prints telegram user's unserviced commands.

        If bot mod is private, method does not return commands from users which are not in whitelist. To these users
        bot sends a message with denial of access. If user's command is not supported, replies with error.
        :returns: Array of UserRequest only with supported commands.
        """
        user_requests = []

        unread_messages = self.__get_unread_messages()

        if unread_messages is None:
            return []

        for message in unread_messages:
            user_requests.append(self.__get_user_request_from_message(user_message=message))

        supported_user_requests = []

        for user_request in user_requests:
            user_id = user_request.message.from_user.id
            refusal_reply_text = None

            if config.BOT_MOD == constants.BOT_MOD_PRIVATE and user_id not in config.WHITE_LIST_IDS:
                refusal_reply_text = 'This bot is private. You are not in whitelist.'
            elif user_request.command is None and user_request.message.chat.type == 'private':
                refusal_reply_text = 'Command was not recognized.'
            elif user_request.command not in self.__supported_commands:
                refusal_reply_text = f'Command "{user_request.command}" is not supported'

            self.__print_message(user_request=user_request)

            if refusal_reply_text is None:
                supported_user_requests.append(user_request)
            else:
                self.reply_to_message(BotReply(reply_text=refusal_reply_text, replying_message=user_request.message,
                                               reply_variants=[]))

        return supported_user_requests

    def deactivate(self):
        """
        Sends notification of deactivation to groups, stops bot.
        """
        self.send_to_groups(constants.BOT_NOTIFICATION_DEACTIVATION)
        self.__bot.stop_bot()

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

        command_args = None if command is None else user_message.text.replace(command, '').split()
        return UserRequest(message=user_message, command=command, command_args=command_args)

    @staticmethod
    def __print_message(user_request: UserRequest = None, bot_message: BotMessage = None, bot_reply: BotReply = None):
        """
        Prints received or sent telegram message into console. Should have one set parameter.

        :param user_request: Received user request.
        :param bot_message: Sent bot message.
        :param bot_reply: Sent bot reply.
        :returns: None
        """
        if user_request:
            message_text = user_request.message.text
            user_data = user_request.message.from_user
            chat_data = user_request.message.chat
            is_receiving = True
        elif bot_message:
            message_text = bot_message.message_text
            user_data = None
            chat_data = bot_message.message_chat
            is_receiving = False
        elif bot_reply:
            message_text = bot_reply.reply_text
            user_data = bot_reply.replying_message.from_user
            chat_data = bot_reply.replying_message.chat
            is_receiving = False
        else:
            raise Exception(f'{constants.CONSOLE_PREFIX} __print_message() was called with NoneType.')

        max_length = constants.CONSOLE_MESSAGE_MAX_LENGTH

        message_text = message_text.replace('\n', '')

        if len(message_text) > max_length:
            message_text = f'{message_text[0:max_length // 2]} "..." {message_text[-max_length // 2 - 1:-1]}'

        bot_name = 'telegramfreak'

        if user_data:
            user_repr = f'{user_data.username}(id{user_data.id})'
        else:
            user_repr = None

        if chat_data:
            chat_repr = f'{chat_data.username}(id{chat_data.id}, type {chat_data.type})'
        else:
            chat_repr = None

        sender_data = user_repr if is_receiving else bot_name
        receiver_data = bot_name if is_receiving else user_repr

        print_message = f'{constants.CONSOLE_PREFIX} {sender_data} '

        if chat_repr:
            print_message += f'in {chat_repr} '

        print_message += f'-> {receiver_data}: {message_text}'
        print(print_message)

    @staticmethod
    def __get_keyboard_from_commands(commands: [str]):
        """
        Parses commands array into ReplyKeyBoardMarkup.

        :param commands: Commands to parse.
        :returns: Parsed ReplyKeyBoardMarkup or None.
        """

        if commands is None or len(commands) == 0:
            return None

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_count = len(commands) // constants.REPLY_KEYBOARD_BUTTONS_IN_ROW

        if len(commands) % constants.REPLY_KEYBOARD_BUTTONS_IN_ROW != 0:
            row_count += 1

        for row_index in range(row_count):
            row_buttons = []

            for column_index in range(constants.REPLY_KEYBOARD_BUTTONS_IN_ROW - 1):
                command_index = row_index * constants.REPLY_KEYBOARD_BUTTONS_IN_ROW + column_index
                row_buttons.append(telebot.types.KeyboardButton(commands[command_index]))

            keyboard.row(*row_buttons)

        return keyboard


if __name__ == '__main__':
    bot = TelegramFreak()
    bot.menu_commands = ['/test_command']
    bot.supported_commands = ['/test_command', 'qwe']

    while True:
        unserviced_requests = bot.get_unserviced_requests()

        for unserviced_request in unserviced_requests:
            reply_text = f'command: {unserviced_request.command}\nargs: {unserviced_request.commands_args}'
            request_reply_data = BotReply(reply_text=reply_text, replying_message=unserviced_request.message,
                                          reply_variants=bot.supported_commands)
            bot.reply_to_message(reply_data=request_reply_data)
