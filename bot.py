import telebot
import os

token = os.environ['TG_TOKEN']
bot = telebot.TeleBot(token)