import os

from cat_bot import bot
import flask
import hashlib
from telebot import types

server = flask.Flask(__name__)
hashvalue = hashlib.sha256('{}'.format(os.environ['TG_TOKEN']).encode())
api_token = hashvalue.hexdigest()
APP_NAME = 'tg-cat-bot'


@server.route('/' + api_token, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(
        flask.request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route('/', methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, api_token))
    return "Hello from Heroku!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8443)


