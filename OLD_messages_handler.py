import telebot
import time
import io
from enum import Flag, auto


class MessagesHandler:
    class Task:
        class TaskType(Flag):
            Reminder = auto()
            Greeting = auto()

        def __init__(self, task_type: TaskType, user_id: str, time_started: time.time()):
            self.taskType = task_type
            self.userId = user_id
            self.timeStarted = time_started

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot

    FAST_REPLY_COMMANDS = \
        {
            "start",
            "help",
            "my_bio",
        }

    def recognize_command(self, text: str) -> str:
        all_commands = self.FAST_REPLY_COMMANDS
        text = text.lower()

        if text in all_commands:
            return text

        if text[1:] in all_commands:
            return text[1:]

    Not_Created_Tasks_Queue = []

    def get_not_created_task_by_userid(self, userid: int) -> Task:
        for task in self.Not_Created_Tasks_Queue:
            if task.userId == userid:
                return task

    def handle_message(self, message: telebot.types.Message):
        print(f'Message from {message.from_user.first_name}: {message.text}')

        already_created_task = self.get_not_created_task_by_userid(message.from_user.id)
        command = self.recognize_command(message.text)

        if command is None and already_created_task is None:
            self.bot.send_message(chat_id=message.chat.id, text=f'Command "{message.text}" is not supported')
            return

        if already_created_task is None:
            self.execute_new_command(command, message)
        else:
            self.supplement_task(message, already_created_task)

    def execute_new_command(self, command,  message: telebot.types.Message):
        if command in self.FAST_REPLY_COMMANDS:
            self.fast_reply(command, message)

    def fast_reply(self, command, message: telebot.types.Message):
        def get_replay_text() -> str:
            try:
                file_text = io.open(f'Fast Replies/{command}.txt', encoding="utf-8").read()
                return file_text
            except Exception:
                pass

            if command == 'my_bio':
                user = message.from_user
                return (f'First name: {user.first_name}\nSecond name: {user.last_name}\nUsername: {user.username}\n'
                        f'Language code: {user.language_code}\nId: {user.id}\nPremium: {user.is_premium}\n'
                        f'Is bot: {user.is_bot}\n\nRaw data:\n{user}')

        reply_text = get_replay_text()
        reply_markup = telebot.types.ReplyKeyboardMarkup()
        help_button = telebot.types.KeyboardButton('Help')
        bio_button = telebot.types.KeyboardButton('My_bio')
        reply_markup.row(help_button, bio_button)
        self.bot.send_message(message.chat.id, text=reply_text, reply_markup=reply_markup)


    def supplement_task(self, message: telebot.types.Message, task: Task):
        return
