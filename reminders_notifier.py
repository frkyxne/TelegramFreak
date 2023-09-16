import bot_hoster
import datetime

bot = bot_hoster.Bot()
bot.host()
bot.send_message(message=bot_hoster.BotMessage(user_id=1186580310, text='qwe'))
bot.infinite_polling()
