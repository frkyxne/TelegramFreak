import telebot
import messages_handler
import constants


def get_bot() -> telebot.TeleBot:
    try:
        bot = telebot.TeleBot(open('bot_token.txt').readline())
        print(constants.BotHost.BOT_HOST_SUCCESS_NOTIFICATION)
        return bot
    except Exception:
        print(constants.BotHost.BOT_HOST_FAILURE_NOTIFICATION)


telegram_freak = get_bot()


@telegram_freak.message_handler()
def handle_message(message):
    response = messages_handler.get_response(message)

    for message in response.messages:
        # On last message add reply keyboard
        if message is response.messages[-1] and response.reply_keyboard is not None:
            telegram_freak.send_message(chat_id=response.chat_id, text=message, reply_markup=response.reply_keyboard)
        else:
            telegram_freak.send_message(chat_id=response.chat_id, text=message)


telegram_freak.infinity_polling()
