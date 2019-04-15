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
            url = "https://{}.herokuapp.com/{}".format(self.NAME, self.TOKEN)
            print(url)
            self.bot.setWebhook(url)
        except:
            raise RuntimeError("Failed to set the webhook")

        self.update_queue = Queue()
        self.dp = Dispatcher(self.bot, self.update_queue)

        self.dp.add_handler(CommandHandler("start", self._start))
        self.dp.add_handler(MessageHandler(Filters.text, self._process_update))
        self.dp.add_error_handler(self._error)

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _error(self, error):
        cherrypy.log("Error occurred - {}".format(error))

    def _start(self, bot, update):
        print("!!!!!! start")
        update.effective_message.reply_text('Hello friend!')

    def _process_update(self, bot, update):
        self.bot.send_message(chat_id=update.effective_message.chat.id, text=update.effective_message.text)


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
