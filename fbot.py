import logging
from queue import Queue
import cherrypy
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
from settings import NAME, PORT, TOKEN
import exchange_rates


class SimpleWebsite:
    @cherrypy.expose
    def index(self):
        return """<H1>Welcome!</H1>"""


class BotInstruction:
    @cherrypy.expose
    def index(self):
        bot = BotComm(TOKEN, NAME)
        bot.say_hello("629791023", "Hello from http!")
        return "<H1>Bot working...</H1>"


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
        self.dp.add_handler(CommandHandler("help", self._help))
        self.dp.add_handler(CommandHandler("kurs", self._kurs))
        self.dp.add_handler(CommandHandler("chatid", self._get_chat_id))
        self.dp.add_handler(CommandHandler("json", self._get_json))
        self.dp.add_handler(MessageHandler(Filters.text, self._echo_all))
        self.dp.add_error_handler(self._error)

    @cherrypy.tools.json_in()
    def POST(self, *args, **kwargs):
        update = cherrypy.request.json
        update = telegram.Update.de_json(update, self.bot)
        self.dp.process_update(update)

    def _error(self, error):
        cherrypy.log("Error occurred - {}".format(error))

    def _start(self, bot, update):
        print(">>> " + update.effective_message)
        update.effective_message.reply_text("Hello " + update.effective_message.first_name + "!")

    def _help(self, bot, update):
        text = "My first bot - echobot\n" \
               + "/start - Start the bot\n" \
               + "/help - about menu\n" \
               + "/kurs - Kurs valut (usd, eur, etc)\n" \
               + "/chatid - chat id\n" \
               + "/json - answer in json"
        update.effective_message.reply_text(text)
        
    def _kurs(self, bot, update):
        arr = update.effective_message.text.split(" ")
        if len(arr) < 2:
            update.effective_message.reply_text("Sorry, currency not found")
            return

        currency_code = arr[1].strip().upper()
        if currency_code == "RUR" or currency_code == "RUB":
            update.effective_message.reply_text("1")
            return

        currency_info = exchange_rates.get_rate(currency_code)
        if currency_info:
            text = "Курс " + currency_info.get("currency") + ": " + currency_info.get("value") \
                   + " (" + currency_info.get("date") + ")"
        else:
            text = "Unknown currency, try again"
        update.effective_message.reply_text(text)

    def _get_chat_id(self, bot, update):
        self.bot.send_message(chat_id=update.effective_message.chat.id, text=update.effective_message.chat.id)

    def _get_json(self, bot, update):
        self.bot.send_message(chat_id=update.effective_message.chat.id, text=str(update))

    def say_hello(self, chat_id, message_text):
        self.bot.send_message(chat_id=chat_id, text=message_text)

    def _echo_all(self, bot, update):
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
    cherrypy.tree.mount(BotInstruction(), "/bot")
    cherrypy.tree.mount(
        BotComm(TOKEN, NAME),
        "/{}".format(TOKEN),
        {"/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
    cherrypy.engine.start()
