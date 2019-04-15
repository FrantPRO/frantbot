# import exchange_rates

import logging
from queue import Queue

import cherrypy
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher

from settings import NAME, PORT, TOKEN


class SimpleWebsite:
    @cherrypy.expose
    def index(self):
        return """<H1>Welcome!</H1>"""


class BotComm:
    exposed = True

    def __init__(self, TOKEN, NAME):
        super(BotComm, self).__init__()
        self.TOKEN = TOKEN
        self.NAME = NAME
        self.bot = telegram.Bot(self.TOKEN)
        try:
            self.bot.setWebhook("https://{}.herokuapp.com/{}".format(self.NAME, self.TOKEN))
        except:
            raise RuntimeError("Failed to set the webhook")

        self.update_queue = Queue()
        self.dp = Dispatcher(self.bot, self.update_queue)

        self.dp.add_handler(CommandHandler("start", self._start))
        # self.dp.add_handler(MessageHandler(Filters.text, self._process_update))
        self.dp.add_error_handler(self._error)

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _error(self, error):
        cherrypy.log("Error occurred - {}".format(error))

    def _start(self, bot, update):
        update.effective_message.reply_text('Hello friend!')

    # @bot.message_handler(commands=['help'])
    # def send_help(message):
    #     text = 'My first bot - echobot\n' \
    #            '/start - Start the bot\n' \
    #            '/help - about menu\n' \
    #            '/kurs usd - Kurs valut (usd. eur)'
    #     bot.send_message(message.chat.id, text)

    # @bot.message_handler(func=lambda m: True)
    # def echo_all(message):
    #     bot.send_message(message.chat.id, message.text)

    # @bot.message_handler(commands=['kurs'])
    # def send_kurs(message):
    #     currency_info = None
    #     if 'usd' in message.text:
    #         currency_info = exchange_rates.get_rate_usd()
    #
    #     elif 'eur' in message.text:
    #         currency_info = exchange_rates.get_rate_eur()
    #
    #     if currency_info:
    #         text = 'Курс ' + currency_info.get('currency') + ': ' + currency_info.get(
    #             'value') + ' (' + currency_info.get(
    #             'date') + ')'
    #     else:
    #         text = 'currency not found'
    #
    #     bot.send_message(message.chat.id, text)

    # def _accept_order(self, bot, update):
    #     chat_id = update.effective_message.chat.id
    #     order_text = update.effective_message.text
    #     order_user = update.effective_message.from_user
    #     order_user_first_name = order_user.first_name
    #     order_user_last_name = order_user.last_name
    #     order_user_username = order_user.username
    #     text = "{first_name} {last_name} ({username}) " \
    #            "желает: {order}".format(first_name=order_user_first_name,
    #                                     last_name=order_user_last_name,
    #                                     username=order_user_username,
    #                                     order=order_text)
    #     self.bot.send_message(chat_id=chat_id, text=text)
    #     update.effective_message.reply_text("Ваш заказ принят!")

    # def _process_update(self, bot, update):
    #     chat_id = update.effective_message.chat.id
    #     if chat_id == 112789249:
    #         self.bot.send_message(chat_id=chat_id, text="")


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the cherrypy configuration
    cherrypy.config.update({"server.socket_host": "0.0.0.0", })
    cherrypy.config.update({"server.socket_port": int(PORT), })
    cherrypy.tree.mount(SimpleWebsite(), "/")
    cherrypy.tree.mount(
        BotComm(TOKEN, NAME),
        "/{}".format(TOKEN),
        {"/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
