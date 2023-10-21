import telebot
from config import TelegramBot as BotConfig


class BotMessage:
    def __init__(self, text: str, user_id: int = None, username: str = None,
                 replying_message: telebot.types.Message = None,
                 reply_keyboard: telebot.types.ReplyKeyboardMarkup = None):
        self.__text = text
        self.__user_id = user_id
        self.__username = username
        self.__replying_message = replying_message
        self.__reply_keyboard = reply_keyboard

    @property
    def replying_message(self):
        return self.__replying_message

    @property
    def text(self):
        return self.__text

    @property
    def reply_keyboard(self):
        return self.__reply_keyboard

    @property
    def user_id(self):
        return self.__user_id

    @property
    def username(self):
        return self.__username


class BotHoster:
    def __init__(self):
        bot = telebot.TeleBot(BotConfig.BOT_TOKEN)
        self.bot = bot
        self.__update_offset = None

    def send_message(self, message: BotMessage):
        if message.replying_message is not None:

            if message.replying_message.chat.id == BotConfig.BOT_GROUP_ID:
                self.bot.reply_to(message=message.replying_message, text=message.text)
            else:
                self.bot.send_message(chat_id=message.replying_message.from_user.id,
                                      text=message.text,
                                      reply_markup=message.reply_keyboard)

            self.__print_message(text=message.text, user_id=message.replying_message.from_user.id,
                                 is_receiving=False,
                                 username=message.replying_message.from_user.username)
        else:
            self.bot.send_message(text=message.text, chat_id=message.user_id,
                                  reply_markup=message.reply_keyboard)
            self.__print_message(text=message.text, user_id=message.user_id, is_receiving=False,
                                 username=message.username)

    def send_to_group(self, text: str):
        self.send_message(message=BotMessage(text=text, user_id=BotConfig.BOT_GROUP_ID, username='Bot group chat'))

    def get_unread_messages(self) -> [telebot.types.Message]:
        try:
            updates = self.bot.get_updates(offset=self.__update_offset, timeout=1, allowed_updates=['message'])
        except Exception:
            return

        unread_messages = []

        for update in updates:
            message = update.message

            if message.text is None:
                continue

            unread_messages.append(message)
            self.__print_message(text=message.text, user_id=message.from_user.id, is_receiving=True,
                                 username=message.from_user.first_name)

            self.__update_offset = update.update_id + 1

        return unread_messages

    @staticmethod
    def __print_message(text: str, user_id: int, is_receiving: bool, username: str = None):
        if text.count('\n') > 0 or len(text) > 40:
            text = f'{text[0:20]} "..." {text[-21:-1]}'.replace('\n', ' ')

        user_data = str(user_id) if username is None else f'{username}(id{str(user_id)})'

        if is_receiving:
            print(f'{user_data}: {text} -> bot.')
        else:
            print(f'Bot: {text} -> {user_data}.')
