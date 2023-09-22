import telebot.types
import datetime
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
            bot_host.send_message(message=bothoster.BotMessage(user_id=response.user.id, text=message,
                                                               reply_keyboard=response.reply_keyboard))

    def send_message(message: bothoster.BotMessage):
        log_sent_content(text=message.text, user_id=message.user_id)
        bot_host.send_message(message=bothoster.BotMessage(user_id=message.user_id, text=message.text,
                                                           reply_keyboard=message.reply_keyboard))

    def log_sent_content(text: str, user: telebot.types.User = None, user_id: int = None):
        # If text has several lines, log only 40 chars.
        if text.count('\n') > 0:
            content_text = f'{text[0:20]} "..." {text[-21:-1]}'.replace('\n', ' ')
        else:
            content_text = text

        user_name = f'{user.first_name}(id{user.id})' if user is not None else f'id{user_id}'
        log_text = f'telegram freak: {content_text} -> {user_name}'
        log_writer.add_line(log_text)

    def handle_system_commands(response: messageshandler.BotResponse):
        command = response.messages[0]

        if command == constants.System.KILL_CODE and first_loop:
            bot_host.send_message(message=bothoster.BotMessage(user_id=response.user.id,
                                                               text=constants.BotHost.BOT_KILLING_NOTIFICATION))
            log_writer.add_line(constants.BotHost.BOT_KILLING_NOTIFICATION)
            log_writer.save_log()
            exit()
        elif command == constants.System.SAY_CODE:
            send_message(message=bothoster.BotMessage(user_id=response.user.id, text=response.messages[0]))

    def log_received_message(message: telebot.types.Message):
        log_writer.add_line(f'{message.from_user.first_name} (id{message.from_user.id}): {message.text}')

    def response_to_messages():
        unread_messages = bot_host.get_unread_messages()

        if unread_messages is None:
            return

        for unread_message in unread_messages:
            log_received_message(unread_message)

            # Check for system commands
            response = messages_handler.get_response_to_message(unread_message)
            if response.messages[0] not in constants.System.SYSTEM_COMMANDS:
                send_response(response=response)
            else:
                handle_system_commands(response=response)

    def manage_reminders():
        for reminder in remindersmaster.get_reminders_by_now():
            send_message(message=bothoster.BotMessage(user_id=reminder.user_id, text=f'Automated notification: "'
                                                                                     f'{reminder.reminder_text}"'))

            remindersmaster.write_new_status(reminder=reminder, new_status=remindersmaster.Reminder.Status.NOTIFIED)

        for reminder in remindersmaster.get_today_overdue_reminders():
            send_message(message=bothoster.BotMessage(user_id=reminder.user_id,
                                                      text=f'Overdue automated notification: '
                                                           f'{reminder.reminder_text}"'))

            remindersmaster.write_new_status(reminder=reminder, new_status=remindersmaster.Reminder.Status.NOTIFIED)

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
    log_writer.add_line(constants.BotHost.BOT_HOST_SUCCESS_NOTIFICATION)
except Exception as error:
    log_writer.add_line(constants.BotHost.BOT_HOST_FAILURE_NOTIFICATION)
    log_writer.add_line(str(error))
    log_writer.save_log()
    exit()

messages_handler = messageshandler.MessagesHandler()
infinite_handling()
