import bothoster
import messageshandler
import time


def infinite_handling():
    while True:
        unread_messages = bot_host.get_unread_messages()

        for unread_message in unread_messages:
            response = messages_handler.get_response_to_message(unread_message)

            for message in response.messages:
                if message == response.messages[-1] and response.reply_keyboard is not None:
                    bot_host.send_message(message=bothoster.BotMessage(user=response.user, text=message,
                                                                       reply_keyboard=response.reply_keyboard))
                else:
                    bot_host.send_message(message=bothoster.BotMessage(user=response.user, text=message))

        time.sleep(1)


# Hosting a bot
bot_host = bothoster.BotHoster()
messages_handler = messageshandler.MessagesHandler()
infinite_handling()
