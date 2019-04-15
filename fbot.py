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
        print("!!!!!! Welcome!")
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
        self.dp.add_handler(MessageHandler(Filters.text, self._process_update))
        self.dp.add_error_handler(self._error)

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        print("!!!!!! post")
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _error(self, error):
        print("!!!!!! error")
        cherrypy.log("Error occurred - {}".format(error))

    def _start(self, bot, update):
        print("!!!!!! start")
        update.effective_message.reply_text('Hello friend!')

    def _process_update(self, bot, update):
        self.bot.send_message(chat_id=update.effective_message.chat.id, text="")


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the cherrypy configuration
    cherrypy.config.update({"server.socket_host": "0.0.0.0", })
    print("!!!!!! cherrypy set host")
    cherrypy.config.update({"server.socket_port": int(PORT), })
    print("!!!!!! cherrypy set port")
    cherrypy.tree.mount(SimpleWebsite(), "/")
    print("!!!!!! cherrypy start SimpleWebsite")
    cherrypy.tree.mount(
        BotComm(TOKEN, NAME),
        "/{}".format(TOKEN),
        {"/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
