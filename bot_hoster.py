import telebot
import messages_handler
import constants


class BotMessage:
    def __init__(self, user_id: int, text: str):
        self.__user_id = user_id
        self.__text = text

    @property
    def user_id(self):
        return self.__user_id

    @property
    def text(self):
        return self.__text


class Bot:
    def __init__(self):
        self.bot: telebot.TeleBot = None

    def host(self):
        try:
            bot = telebot.TeleBot(open(constants.TOKEN_PATH).readline())
            print(constants.BotHost.BOT_HOST_SUCCESS_NOTIFICATION)
            self.bot = bot
        except Exception as error:
            print(constants.BotHost.BOT_HOST_FAILURE_NOTIFICATION)
            print(error)

    def send_message(self, message: BotMessage):
        self.bot.send_message(chat_id=message.user_id, text=message.text)
        print(f'Message with text "{message.text}" was sent to {message.user_id}')

    def infinite_polling(self):
        bot = self.bot

        @bot.message_handler()
        def handle_message(message: telebot.types.Message):
            response = messages_handler.get_response(message)

            for message in response.messages:
                # On last message add reply keyboard
                if message is response.messages[-1] and response.reply_keyboard is not None:
                    bot.send_message(chat_id=response.chat_id, text=message,
                                                    reply_markup=response.reply_keyboard)
                else:
                    bot.send_message(chat_id=response.chat_id, text=message)

        bot.infinity_polling()
