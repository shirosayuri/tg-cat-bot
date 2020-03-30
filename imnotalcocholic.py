# -*- coding: utf-8 -*-
from bot import bot
from telebot import types
from postgres_func import select_random, select_condition

kind_dict = {
    'gin': 'Джин', 'Джин': 'gin',
    'aperitif': 'Апперетиф', 'Апперетиф': 'aperitif',
    'vodka': 'Водка', 'Водка': 'vodka',
    'wine': 'Вино', 'Вино': 'wine',
    'cognac': 'Коньяк', 'Коньяк': 'cognac',
    'armagnac': 'Арманьяк', 'Арманьяк': 'armagnac',
    'rum': 'Ром', 'Ром': 'rum',
    'champagne': 'Шампанское', 'Шампанское':  'champagne',
    'liquors': 'Ликёр или настойка', 'Ликёр или настойка': 'liquors',
    'whiskey': 'Виски', 'Виски': 'whiskey',
    'brandy': 'Бренди', 'Бренди': 'brandy'
}


def keyboard(buttons, width=2):
    keyb = types.InlineKeyboardMarkup(row_width=width)
    keyb.add(
        *[types.InlineKeyboardButton(text=name, callback_data=name) for name in buttons])

    return keyb


user_session = {}

@bot.message_handler(commands=['alcocholic'])
def start_vine_msg(message):
    # команда для первого входа в бота
    user_session[message.chat.id] = {'title': None,
                                     'country': None,
                                     'type': None,
                                     'sugar': None,
                                     'temperature': None,
                                     'grape': None,
                                     'alcohol': None,
                                     'compatibility': None,
                                     'taste': None,
                                     'old': None,
                                     'class': None,
                                     'material': None,
                                     'color': None,
                                     'style': None,
                                     'filter': None,
                                     'added': None,
                                     'distillation': None,
                                     'link': None,
                                     'price': None,
                                     'kind': None}
    try:
        kinds = []
        for i in select_condition(table='imnotalcocholic', column='kind', distinct=True):
            kinds.append(kind_dict[i[0]])
        kinds.append('Мне повезёт')
        bot.send_message(chat_id=message.chat.id,
                         text='Что ты хочешь выпить?',
                         parse_mode='Markdown',
                         reply_markup=keyboard(kinds)
                         ).wait()
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda c: True)
def button(button):
    not_none_values = {}
    for dict_key, dict_value in user_session[button.message.chat.id].items():
        if dict_value:
            not_none_values.update({dict_key: dict_value})
    print(not_none_values)
    if button.data == 'Мне повезёт':

        vine = select_random('imnotalcocholic', 'title, kind')
        print(vine)
        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Могу предложить тебе {}: {}.'.format(kind_dict[vine[1]].lower(), vine[0]),
                              parse_mode='Markdown').wait()

    elif button.data in kind_dict.keys():
        user_session[button.message.chat.id]['kind'] = kind_dict[button.data]
        alco_type = select_condition(table='imnotalcocholic',
                                     column='type',
                                     condition="kind = '{}'".format(kind_dict[button.data]),
                                     distinct=True)
        print(alco_type, user_session)


    else:
        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Пожалуйста, подождите, идёт разработка.',
                              parse_mode='Markdown').wait()

