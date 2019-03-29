import settings
import telebot


bot = telebot.TeleBot(settings.TOKEN)


@bot.message_handler(commands=['start', [help]])
def send_welcom(message):
    bot.reply_to(message, "Hello MF!")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()
