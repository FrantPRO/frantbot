import settings
import telebot
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


if __name__ == '__main__':
    bot.polling()
