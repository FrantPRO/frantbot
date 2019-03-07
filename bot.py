# -*- coding: utf-8 -*-
import config
from telegram.ext import Updater, CommandHandler


def hello(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))


updater = Updater(config.token)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.start_polling()
updater.idle()

# @bot.message_handler(content_types=["text"])
# def repeat_all_messages(message):  # Название функции не играет никакой роли, в принципе
#     bot.send_message(message.chat.id, message.text)
#
#
# if __name__ == '__main__':
#     bot.polling(none_stop=True)
