# -*- coding: utf-8 -*-
from bot import bot
from postgres_func import select_condition, check_superuser, insert_condition, delete_condition
from functions import enough

#######################################дальше живут драконы############################################################


@bot.message_handler(commands=['god_mode'])
def god_mode(message):
    bot.clear_step_handler(message)
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'admin'):
        bot.send_message(chat_id=message.chat.id,
                         text="Привет, {}. \nТебе доступны следующие команды:\n"
                              "/add_phrase,\n/delete_phrase,\n/add_moder,\n/delete_moder."
                              "\nEnjoy.".format(message.from_user.username))
    elif role == 'moder':
        bot.send_message(chat_id=message.chat.id,
                         text="Привет, {}. \nТебе доступны следующие команды:\n"
                              "/add_phrase,\n/delete_phrase."
                              "\nEnjoy.".format(message.from_user.username),
                         parse_mode='Markdown')
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAIHmF41kWHKUfajjxb0umLKOG-EMWanAALwLgAC4KOCB2bcGHGkwKtzGAQ')


@bot.message_handler(commands=['add_moder'])
def bot_add_moder(message):
    bot.clear_step_handler(message)
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'admin'):
        bot.send_message(chat_id=message.chat.id,
                         text="Напиши логин того, кому хочешь выдать права на добавление фраз.\n"
                              "Напиши ___хватит___, если передумал.",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, add_moder)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAIHmF41kWHKUfajjxb0umLKOG-EMWanAALwLgAC4KOCB2bcGHGkwKtzGAQ')


@bot.message_handler(commands=['delete_moder'])
def bot_delete_moder(message):
    bot.clear_step_handler(message)
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'admin'):
        bot.send_message(chat_id=message.chat.id,
                         text="Напиши логин того, у кого нужно отобрать дополнительные права.\n"
                              "Напиши ___хватит___, если передумал.",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, delete_moder)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAIHmF41kWHKUfajjxb0umLKOG-EMWanAALwLgAC4KOCB2bcGHGkwKtzGAQ')


@bot.message_handler(commands=['add_phrase'])
def bot_add_phrase(message):
    bot.clear_step_handler(message)
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'moder', 'admin'):
        bot.send_message(chat_id=message.chat.id,
                         text="Какую фразу ты хочешь добавить? Пожалуйста, напиши одно предложение в сообщении, "
                              "я не хочу их сам на строчки разбивать :'(\n"
                              "Напиши ___хватит___, если передумал.",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, new_phrase)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAIHmF41kWHKUfajjxb0umLKOG-EMWanAALwLgAC4KOCB2bcGHGkwKtzGAQ')


@bot.message_handler(commands=['delete_phrase'])
def bot_delete_phrase(message):
    bot.clear_step_handler(message)
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'moder', 'admin'):
        bot.send_message(chat_id=message.chat.id,
                         text="Какую фразу ты хочешь удалить? Учти, нужно полное совпадение.\n"
                              "Напиши ___хватит___, если передумал.",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, delete_phrase)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAIHmF41kWHKUfajjxb0umLKOG-EMWanAALwLgAC4KOCB2bcGHGkwKtzGAQ')


def new_phrase(message):
    text_exists = select_condition('texts', 'msg', "msg = '{msg}'".format(msg=message.text))
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'moder', 'admin'):
        if enough(message.text):
            bot.send_message(chat_id=message.chat.id,
                             text="Ой, больно-то и хотелось!",
                             parse_mode='Markdown')
        elif message.content_type == 'text' and message.text[0] != '/' and not text_exists:
            result = insert_condition(table='texts', values=(message.text,), columns='(msg)')
            if result:
                bot.send_message(chat_id=message.chat.id,
                                 text="Я всё добавил, но если что, можно удалить.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text="Хм, кажется, что-то не так с базой данных. Давай попробуем ещё раз.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
        elif text_exists:
            bot.send_message(chat_id=message.chat.id,
                             text="Такой текст уже есть, давай попробуем ещё раз. ",
                             parse_mode='Markdown',
                             reply_to_message_id=message.message_id)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text='Мы так не договаривались! Пришли фразу, пожалуйста, а не вот это вот всё :C',
                             parse_mode='Markdown',
                             reply_to_message_id=message.message_id)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAIHmF41kWHKUfajjxb0umLKOG-EMWanAALwLgAC4KOCB2bcGHGkwKtzGAQ')
    bot.clear_step_handler(message)


def delete_phrase(message):
    text_exists = select_condition('texts', 'msg', "msg = '{msg}'".format(msg=message.text))
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'moder', 'admin'):
        if enough(message.text):
            bot.send_message(chat_id=message.chat.id,
                             text="Ой, больно-то и хотелось!",
                             parse_mode='Markdown')
        elif text_exists:
            result = delete_condition(table='texts', condition="msg = '{msg}'".format(msg=message.text))
            if result:
                bot.send_message(chat_id=message.chat.id,
                                 text="Ну что ж, я её удалил. Теперь страдай.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text="Хм, кажется, что-то не так с базой данных. Давай попробуем ещё раз.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text="А такой фразы-то и нет, делай теперь с этим что хочешь!",
                             parse_mode='Markdown',
                             reply_to_message_id=message.message_id)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
    bot.clear_step_handler(message)


def add_moder(message):
    moder_exists = select_condition('superusers', 'user_role', "login = '{msg}'".format(msg=message.text))
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'admin'):
        if enough(message.text):
            bot.send_message(chat_id=message.chat.id,
                             text="Ой, больно-то и хотелось!",
                             parse_mode='Markdown')
        elif message.content_type == 'text' and message.text[0] != '/' and not moder_exists:
            result = insert_condition(table='superusers', values=(message.text, "moder"))
            if result:
                bot.send_message(chat_id=message.chat.id,
                                 text="Я добавил нового модератора, но если что, можно и удалить!",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text="Хм, кажется, что-то не так с базой данных. Давай попробуем ещё раз.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
        elif moder_exists:
            bot.send_message(chat_id=message.chat.id,
                             text="А такой модератор уже есть, соряш-соряш.",
                             parse_mode='Markdown',
                             reply_to_message_id=message.message_id)

        else:
            bot.send_message(chat_id=message.chat.id,
                             text='Мы так не договаривались! Пришли фразу, пожалуйста, а не вот это вот всё :C',
                             parse_mode='Markdown',
                             reply_to_message_id=message.message_id)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
    bot.clear_step_handler(message)


def delete_moder(message):
    role = check_superuser(login=message.from_user.username)
    if role in ('superuser', 'admin'):
        moder_exists = select_condition('superusers', 'user_role', "login = '{msg}'".format(msg=message.text))
        if enough(message.text):
            bot.send_message(chat_id=message.chat.id,
                             text="Ой, больно-то и хотелось!",
                             parse_mode='Markdown')
        elif moder_exists:
            result = delete_condition(table='superusers', condition="login = '{msg}'".format(msg=message.text))
            if result:
                bot.send_message(chat_id=message.chat.id,
                                 text="Ну что ж, я отобрал его права. Теперь страдай.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text="Хм, кажется, что-то не так с базой данных. Давай попробуем ещё раз.",
                                 parse_mode='Markdown',
                                 reply_to_message_id=message.message_id)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text="А такого модератора-то и нет, делай теперь с этим что хочешь!",
                             parse_mode='Markdown',
                             reply_to_message_id=message.message_id)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Прости, мама запрещает мне общаться с незнакомцами.',
                         parse_mode='Markdown')
    bot.clear_step_handler(message)