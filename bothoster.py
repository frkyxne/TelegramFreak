import telebot
import constants


class BotMessage:
    def __init__(self, user: telebot.types.User, text: str, reply_keyboard: telebot.types.ReplyKeyboardMarkup = None):
        self.__user = user
        self.__text = text
        self.__reply_keyboard = reply_keyboard

    @property
    def user(self):
        return self.__user

    @property
    def text(self):
        return self.__text

    @property
    def reply_keyboard(self):
        return self.__reply_keyboard


class BotHoster:
    def __init__(self):
        bot = telebot.TeleBot(open(constants.TOKEN_PATH).readline())
        self.bot = bot
        self.__update_offset = 1

    def send_message(self, message: BotMessage):
        self.bot.send_message(chat_id=message.user.id, text=message.text, reply_markup=message.reply_keyboard)

    def get_unread_messages(self) -> [telebot.types.Message]:
        updates = self.bot.get_updates(offset=self.__update_offset, timeout=1, allowed_updates=['message'])
        unread_messages = []

        for update in updates:
            unread_messages.append(update.message)
            self.__update_offset = update.update_id + 1

        return unread_messages
