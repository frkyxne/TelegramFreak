import bothoster
import constants
import messageshandler
import logwriter
import time


def infinite_handling():
    first_loop = True

    while True:
        unread_messages = bot_host.get_unread_messages()

        for unread_message in unread_messages:
            log_writer.add_line(f'{unread_message.from_user.first_name} (id{unread_message.from_user.id}): '
                                f'{unread_message.text}')

            if unread_message.text == kill_code and not first_loop:
                bot_host.send_message(message=bothoster.BotMessage(user=unread_message.from_user,
                                                                   text=constants.BotHost.BOT_KILLING_NOTIFICATION))
                log_writer.add_line(constants.BotHost.BOT_KILLING_NOTIFICATION)
                log_writer.save_log()
                exit()

            response = messages_handler.get_response_to_message(unread_message)

            for message in response.messages:
                if message.count('\n') > 0:
                    log_text = (f'telegram freak: {message[0:20] + "..." + message[-21:-1]} '
                                f'-> {response.user.first_name}(id{response.user.id})').replace("\n", " ")
                else:
                    log_text = f'telegram freak: {message} -> {response.user.first_name}(id{response.user.id})\n'

                log_writer.add_line(log_text)

                if message == response.messages[-1] and response.reply_keyboard is not None:
                    # Message is last and response has reply keyboard, showing it
                    bot_host.send_message(message=bothoster.BotMessage(user=response.user, text=message,
                                                                       reply_keyboard=response.reply_keyboard))
                else:
                    bot_host.send_message(message=bothoster.BotMessage(user=response.user, text=message))

        time.sleep(1)
        first_loop = False


# Hosting a bot
log_writer = logwriter.LogWriter()

try:
    bot_host = bothoster.BotHoster()
    kill_code = open(constants.KILL_CODE_PATH).readline()
    log_writer.add_line(constants.BotHost.BOT_HOST_SUCCESS_NOTIFICATION)
except Exception as error:
    log_writer.add_line(constants.BotHost.BOT_HOST_FAILURE_NOTIFICATION)
    log_writer.add_line(str(error))
    log_writer.save_log()
    exit()

messages_handler = messageshandler.MessagesHandler()
infinite_handling()
