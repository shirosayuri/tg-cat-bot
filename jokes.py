# -*- coding: utf-8 -*-
from bot import bot
from functions import get_cat, bashim, poetory
from postgres_func import select_random
import os

log_chat = os.environ['admin_chat_id']


@bot.message_handler(commands=['cat'])
def send_cat(message):
    cat = get_cat()
    if str(cat).split('.')[-1] == 'gif':
        bot.send_document(message.chat.id, cat)
    else:
        bot.send_photo(message.chat.id, cat)


@bot.message_handler(commands=['pizdec'])
def bot_pain_message(message):
    bot.send_message(chat_id=message.chat.id,
                     text=select_random(table='texts', column='msg')).wait()


@bot.message_handler(commands=['bashim'])
def bot_bashim_message(message):
    try:
        bot.send_message(chat_id=message.chat.id,
                         text=bashim(),
                         parse_mode='html').wait()
    except Exception as e:
        bot.send_message(chat_id=message.chat.id,
                         text='Что-то не хочет bash.im дружить. Но мне есть что на это сказать!\n\n' +
                              select_random(table='texts', column='msg')[0]).wait()
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in jokes at bot_bashim_message func'.format(e)
                         )


@bot.message_handler(commands=['poetory'])
def bot_poetory_message(message):
    try:
        bot.send_message(chat_id=message.chat.id,
                         text=poetory(),
                         parse_mode='html').wait()
    except Exception as e:
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in jokes at bot_poetory_message func'.format(e)
                         )
        bot.send_message(chat_id=message.chat.id,
                         text='Что-то не хочет poetory.ru дружить. Но мне есть что на это сказать!\n\n' +
                              select_random(table='texts', column='msg')[0]).wait()