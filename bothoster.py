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
        try:
            bot = telebot.TeleBot(open(constants.TOKEN_PATH).readline())
            print(constants.BotHost.BOT_HOST_SUCCESS_NOTIFICATION)
            self.bot = bot
        except Exception as error:
            print(constants.BotHost.BOT_HOST_FAILURE_NOTIFICATION)
            print(error)

        self.__update_offset = 1

    def send_message(self, message: BotMessage):
        self.bot.send_message(chat_id=message.user.id, text=message.text, reply_markup=message.reply_keyboard)

        if message.text.count('\n') > 0:
            print(f'telegram freak: {message.text[0:20] + "..." + message.text[-21:-1]}'
                  f'-> {message.user.first_name}(id{message.user.id})'.replace("\n", " "))
        else:
            print(f'telegram freak: {message.text} -> {message.user.first_name}(id{message.user.id})\n')

    def get_unread_messages(self) -> [telebot.types.Message]:
        updates = self.bot.get_updates(offset=self.__update_offset, timeout=1, allowed_updates=['message'])
        unread_messages = []

        for update in updates:
            print(f'{update.message.from_user.first_name} (id{update.message.from_user.id}): {update.message.text}')
            unread_messages.append(update.message)
            self.__update_offset = update.update_id + 1

        return unread_messages
