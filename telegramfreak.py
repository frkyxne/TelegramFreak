import telebot.types

import bothoster
import constants
import messageshandler
import remindersmaster
import logwriter
import time


def infinite_handling():
    def send_response(response: messageshandler.BotResponse):
        for message in response.messages:
            log_sent_content(text=message, user=response.user)

            if message == response.messages[-1] and response.reply_keyboard is not None:
                # Message is last and response has reply keyboard, showing it
                bot_host.send_message(message=bothoster.BotMessage(user_id=response.user.id, text=message,
                                                                   reply_keyboard=response.reply_keyboard))
            else:
                bot_host.send_message(message=bothoster.BotMessage(user_id=response.user.id, text=message))

    def send_message(message: bothoster.BotMessage):
        log_sent_content(text=message.text, user_id=message.user_id)
        bot_host.send_message(message=bothoster.BotMessage(user_id=message.user_id, text=message.text,
                                                           reply_keyboard=message.reply_keyboard))

    def log_sent_content(text: str, user: telebot.types.User = None, user_id: int = None):
        if user is not None:
            if text.count('\n') > 0:
                log_text = (f'telegram freak: {text[0:20] + "..." + text[-21:-1]} '
                            f'-> {user.first_name}(id{user.id})').replace("\n", " ")
            else:
                log_text = f'telegram freak: {text} -> {user.first_name}(id{user.id})\n'
        else:
            if text.count('\n') > 0:
                log_text = (f'telegram freak: {text[0:20] + "..." + text[-21:-1]} '
                            f'-> id{user_id}').replace("\n", " ")
            else:
                log_text = f'telegram freak: {text} -> id{user_id}\n'

        log_writer.add_line(log_text)

    def log_received_message(message: telebot.types.Message):
        log_writer.add_line(f'{message.from_user.first_name} (id{message.from_user.id}): {message.text}')

        if message.text == kill_code and not first_loop:
            # Kill code received, killing bot
            bot_host.send_message(message=bothoster.BotMessage(user_id=message.from_user.id,
                                                               text=constants.BotHost.BOT_KILLING_NOTIFICATION))
            log_writer.add_line(constants.BotHost.BOT_KILLING_NOTIFICATION)
            log_writer.save_log()
            exit()

    def response_to_messages():
        unread_messages = bot_host.get_unread_messages()

        for unread_message in unread_messages:
            log_received_message(unread_message)
            send_response(messages_handler.get_response_to_message(unread_message))

    def manage_reminders():
        reminders_to_notify = remindersmaster.get_reminders_by_now()

        for reminder in reminders_to_notify:
            if reminder.status == remindersmaster.Reminder.Status.NOTIFIED:
                continue

            send_message(message=bothoster.BotMessage(user_id=reminder.user_id, text=f'Automated notification: "'
                                                                                     f'{reminder.reminder_text}"'))
            remindersmaster.set_reminder_status(reminder=reminder, new_status=remindersmaster.Reminder.Status.NOTIFIED)

    first_loop = True

    while True:
        response_to_messages()
        manage_reminders()
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
