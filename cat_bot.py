# -*- coding: utf-8 -*-
import random
import telebot
import requests
import logging
import os
import psycopg2
import hashlib
from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import sys

from bot import bot

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


@bot.message_handler(commands=['start', 'help'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(chat_id=message.chat.id, text='Привет, я кот-бот, который очень любит котиков и умные мысли!\n'
                                                       'Напиши мне и я поделюсь ими с тобой.\n'
                                                       'Умные мысли приходят сразу,а котики идут подольше,'
                                                       ' у них же лапки!')
    elif message.text == "/help":
        bot.send_message(chat_id=message.chat.id, text='Чтобы получить умную мысль напиши /pizdec \n'
                                                       'Что бы получить котика напиши /cat')
    else:
        bot.send_message(chat_id=message.chat.id, text='Неизвестная команда. Но ты попробуй еще раз.')


def get_cat():
    try:
        r = requests.get('http://thecatapi.com/api/images/get?format=src')
        url = r.url
    except Exception as error:
        url = get_cat()
        print('Error with cat parsing')
        pass
    return url


@bot.message_handler(commands=['cat'])
def send_cat(message):
    bot.send_photo(message.chat.id, get_cat())


@bot.message_handler(commands=['pizdec'])
def bot_pain_message(message):
    sql = 'SELECT msg FROM texts ORDER BY RANDOM() LIMIT 1'
    cur.execute(sql)
    text = cur.fetchone()
    bot.send_message(chat_id=message.chat.id, text=text, parse_mode='Markdown')


@bot.message_handler(commands=['add_phrase'])
def bot_add_phrase(message):
    if message.from_user.username in ('ShiroSayuri', 'AcidCat', 'asalata88'):
        bot.send_message(chat_id=message.chat.id,
                         text="Какую фразу ты хочешь добавить? Пожалуйста, напиши одно предложение в сообщении, "
                              "я не хочу их сам на строчки разбивать :'(",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, new_phrase)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, я тебя не знаю и не доверяю. '
                              'Тебе придётся найти моего создателя: я слушаю только их.',
                         parse_mode='Markdown')


def new_phrase(message):
    if message.content_type == 'text':
        sql = 'INSERT INTO texts (msg) VALUES (%s)'
        cur.execute(sql, (message.text,))
        conn.commit()
        bot.send_message(chat_id=message.chat.id,
                         text="Надеюсь, ты проверила её на грамматику, потому что действие нельзя отменить :'D",
                         parse_mode='Markdown')
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Мы так не договаривались! Пришли фразу, пожалуйста, а не вот это вот всё :C',
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, new_phrase)


if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling(True, timeout=180)
        except Exception as error:
            logging.error(error)
