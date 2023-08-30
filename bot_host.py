import telebot
import messages_handler


def get_bot() -> telebot.TeleBot:
    try:
        bot = telebot.TeleBot("6541310747:AAHd6zwcfdOY5izuA5j8e_AlwqXCKx5zezY")
        print("Bot was successfully hosted and now online")
        return bot
    except Exception:
        print("Failed to host bot")


telegram_freak = get_bot()


@telegram_freak.message_handler()
def handle_message(message):
    response = messages_handler.get_response(message)
    telegram_freak.send_message(chat_id=response.chat_id, text=response.text, reply_markup=response.reply_markup)


telegram_freak.infinity_polling()
