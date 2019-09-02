from settings import NAME, PORT, TOKEN, HOST
import exchange_rates





# bot.setWebhook("https://{}.herokuapp.com/{}".format(self.NAME, self.TOKEN))
#
#         self.dp.add_handler(CommandHandler("start", self._start))
#         self.dp.add_handler(CommandHandler("help", self._help))
#         self.dp.add_handler(CommandHandler("kurs", self._kurs))
#         self.dp.add_handler(CommandHandler("chatid", self._get_chat_id))
#         self.dp.add_handler(CommandHandler("json", self._get_json))



    # def _start(self, bot, update):
    #     update.effective_message.reply_text("Hello " + update.effective_message.from_user.first_name + "!")

    # def _help(self, bot, update):
    #     text = "My first bot - echobot\n" \
    #            + "/start - Start the bot\n" \
    #            + "/help - about menu\n" \
    #            + "/kurs - Kurs valut (usd, eur, etc)\n" \
    #            + "/chatid - chat id\n" \
    #            + "/json - answer in json"
    #     update.effective_message.reply_text(text)
        
    # def _kurs(self, bot, update):
    #     arr = update.effective_message.text.split(" ")
    #     if len(arr) < 2:
    #         update.effective_message.reply_text("Sorry, currency not found")
    #         return

        # currency_code = arr[1].strip().upper()
        # if currency_code == "RUR" or currency_code == "RUB":
        #     update.effective_message.reply_text("1")
        #     return
        #
        # currency_info = exchange_rates.get_rate(currency_code)
        # if currency_info:
        #     text = "Курс " + currency_info.get("currency") + ": " + currency_info.get("value") \
        #            + " (" + currency_info.get("date") + ")"
        # else:
        #     text = "Unknown currency, try again"
        # update.effective_message.reply_text(text)

    # def _get_chat_id(self, bot, update):
    #     self.bot.send_message(chat_id=update.effective_message.chat.id, text=update.effective_message.chat.id)
    #
    # def _get_json(self, bot, update):
    #     self.bot.send_message(chat_id=update.effective_message.chat.id, text=str(update))
    #
    # def say_hello(self, chat_id, message_text):
    #     self.bot.send_message(chat_id=chat_id, text=message_text)
    #
    # def _echo_all(self, bot, update):
    #     self.bot.send_message(chat_id=update.effective_message.chat.id, text=update.effective_message.text)


# if __name__ == "__main__":
#     # Enable logging
#     logging.basicConfig(
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         level=logging.INFO)
#     logger = logging.getLogger(__name__)
#
#     # Set up the cherrypy configuration
#     cherrypy.config.update({"server.socket_host": "0.0.0.0", })
#     cherrypy.config.update({"server.socket_port": int(PORT), })
#     cherrypy.tree.mount(SimpleWebsite(), "/")
#     cherrypy.tree.mount(BotInstruction(), "/bot")
#     cherrypy.tree.mount(
#         BotComm(TOKEN, NAME),
#         "/{}".format(TOKEN),
#         {"/": {
#             "request.dispatch": cherrypy.dispatch.MethodDispatcher()}})
#     cherrypy.engine.start()


import asyncio
import aiohttp
from aiohttp import web
import json

API_URL = "https://{}.herokuapp.com/{}".format(NAME, TOKEN)


async def handler(request):
    data = await request.json()
    headers = {
        'Content-Type': 'application/json'
    }
    message = {
        'chat_id': data['message']['chat']['id'],
        'text': data['message']['text']
    }
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.post(API_URL,
                                data=json.dumps(message),
                                headers=headers) as resp:
            try:
                assert resp.status == 200
            except:
                return web.Response(status=500)
    return web.Response(status=200)


async def init_app(loop):
    app = web.Application(loop=loop, middlewares=[])
    app.router.add_post('/api/v1', handler)
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        app = loop.run_until_complete(init_app(loop))
        web.run_app(app, host=HOST, port=PORT)
    except Exception as e:
        print('Error create server: %r' % e)
    finally:
        pass
    loop.close()