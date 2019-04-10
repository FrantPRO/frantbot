import settings
import telebot
import os
from flask import Flask, request
import logging
import exchange_rates

bot = telebot.TeleBot(settings.TOKEN)


@bot.message_handler(commands=['start'])
def send_welcom(message):
    bot.reply_to(message, "Hello friend!")


@bot.message_handler(commands=['help'])
def send_help(message):
    text = 'My first bot - echobot\n' \
           '/start - Start the bot\n' \
           '/help - about menu\n' \
           '/kurs[val] - Kurs valut (usd. eur)'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['kurs'])
def send_kurs(message):
    currency_info = None
    if 'usd' in message.text:
        currency_info = exchange_rates.get_rate_usd()

    elif 'eur' in message.text:
        currency_info = exchange_rates.get_rate_eur()

    if currency_info:
        text = 'Курс ' + currency_info.get('currency') + ': ' + currency_info.get('value') + ' (' + currency_info.get(
                'date') + ')'
    else:
        text = 'currency not found'

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.send_message(message.chat.id, message.text)


# if __name__ == '__main__':
#     bot.polling()

# Проверим, есть ли переменная окружения Хероку (как ее добавить смотрите ниже)
if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=os.environ.get('HOST'))
        print(os.environ.get('HOST'))
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
    # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
    bot.remove_webhook()
    bot.polling(none_stop=True)
