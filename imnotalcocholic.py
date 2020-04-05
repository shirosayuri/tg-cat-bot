# -*- coding: utf-8 -*-
import json
import datetime
from bot import bot
from telebot import types
from postgres_func import select_random, select_condition, insert_condition, update_condition, delete_condition

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
    'brandy': 'Бренди', 'Бренди': 'brandy',
    'tequila': 'Текила', 'Текила': 'tequila',
    'grappa': 'Граппа', 'Граппа': 'grappa',
    'water': 'Вода', 'Вода': 'water'
}


def not_none_condition(user_session_dict):
    not_none_condition = []
    for dict_key, dict_value in user_session_dict.items():
        if dict_value:
            not_none_condition.append("{} = '{}'".format(dict_key, dict_value))
    return ' and '.join(not_none_condition)


def keyboard(buttons, width=2):
    keyb = types.InlineKeyboardMarkup(row_width=width)
    keyb.add(
        *[types.InlineKeyboardButton(text=name, callback_data=name) for name in buttons])

    return keyb


all_types = [i[0] for i in select_condition(table='imnotalcocholic',
                                            column='type',
                                            distinct=True)]

all_country = [i[0] for i in select_condition(table='imnotalcocholic',
                                              column='country',
                                              distinct=True)]

all_prices_dict = {'< 150 р.': [0, 150],
                   '150-300 р.': [150, 300],
                   '300-500 р.': [300, 500],
                   '500-700 р.': [500, 700],
                   '> 700 р.': [700, ]}


@bot.message_handler(commands=['alcocholic', 'alcoholic'])
def start_vine_msg(message):
    # здесь добавляем юзера в таблицу с юзерскими сессиями,
    # чтобы не потерять его на просторах асинхронного программирования
    try:
        if not select_condition('user_sessions', 'user_id',
                                "user_id = '{}' and command = 'alcoholic'".format(message.chat.id)):
            insert_condition(table='user_sessions', values=(str(message.chat.id), 'alcoholic'),
                             columns='(user_id, command)')
        kinds = []
        for i in select_condition(table='imnotalcocholic', column='kind', distinct=True):
            kinds.append(kind_dict[i[0]])
        kinds.append('Мне повезёт')
        bot.send_message(chat_id=message.chat.id,
                         text='Что ты хочешь выпить?',
                         parse_mode='Markdown',
                         reply_markup=keyboard(kinds)
                         )
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text='Ой, что-то пошло не так. Попробуй ещё раз.',
                         parse_mode='Markdown'
                         )


@bot.callback_query_handler(func=lambda c: True)
def button(button):
    # здесь смотрим на юзерскую сессию если она есть
    user_session = {}
    user_session[button.message.chat.id] = select_condition('user_sessions',
                                                            'session',
                                                            "user_id = '{}'"
                                                            "and command = 'alcoholic'"
                                                            .format(button.message.chat.id))[0][0]
    if button.data == 'Мне повезёт' or button.data in all_prices_dict.keys() or button.data == 'Любая стоимость':
        user_session[button.message.chat.id] = select_condition('user_sessions',
                                                                'session',
                                                                "user_id = '{}'"
                                                                "and command = 'alcoholic'"
                                                                .format(button.message.chat.id))[0][0]
        vine_condition = not_none_condition(user_session[button.message.chat.id]) if user_session[button.message.chat.id] else ''
        vines = select_random('imnotalcocholic',
                              'title, ' #0
                              'kind, ' #1
                              'alcohol, ' #2
                              'country, ' #3
                              'price, '#4
                              'sugar, ' #5
                              'type, ' #6
                              'temperature, ' #7
                              'old,' #8
                              'compatibility, ' #9
                              'taste, ' #10
                              'link ', #11
                              vine_condition,
                              limit=3)
        message_text = []
        # здесь составляем текст если первый вопрос был выбран или нет, то есть если мы знаем тип или нет
        if user_session[button.message.chat.id] and user_session[button.message.chat.id]['kind']:
            for vine in vines:
                # если тип выбран
                message_text += ['{title}. {alcohol}{type}{country}{price}{taste}{sugar}'
                                 '{temperature}{old}{compatibility}'
                                     .format(title='\n***{}***'.format(vine[0]),
                                             alcohol='\nПроцент алкоголя: {}'.format(vine[2]) if vine[2]
                                             else '\nБезалкогольный (но это не точно) ',
                                             type='\nТип алкоголя: {}'.format(vine[6]) if vine[6] else '',
                                             country='\nСтрана происхождения: {}'.format(vine[3]) if vine[2] else '',
                                             price='\nСтоимость: {} р.'.format(vine[4]) if vine[4] else '',
                                             taste='\nВкус: {}'.format(vine[10]).replace("'", '') if vine[10] else '',
                                             sugar='\nСодержание сахара: {}'.format(vine[5]) if vine[5] else '',
                                             temperature='\nТемпература подачи: {}'.format(vine[7]) if vine[7] else '',
                                             old='\nВыдержка: {}'.format(vine[8]) if vine[8] else '',
                                             compatibility='\nСочетается с: {}'.format(vine[9])
                                                                                       .replace("'", '')
                                             .replace("'", '') if vine[9] and len(vine[9]) else ''
                                               )]
            message_for_send = 'Могу предложить тебе {}:\n\n{}.'\
                .format(kind_dict[user_session[button.message.chat.id]['kind']].lower(),
                        '\n'.join(message_text))

        else:
            # если тип не выбран
            for vine in vines:
                message_text += ['{kind}: {title}. {alcohol}{type}{country}{price}{taste}{sugar}'
                                 '{temperature}{old}{compatibility}'
                                     .format(title='\n***{}***'.format(vine[0]),
                                             kind=kind_dict[vine[1]],
                                             alcohol='\nПроцент алкоголя: {}'.format(vine[2]) if vine[2]
                                             else '\nБезалкогольный (но это не точно) ',
                                             type='\nТип алкоголя: {}'.format(vine[6]) if vine[6] else '',
                                             country='\nСтрана происхождения: {}'.format(vine[3]) if vine[2] else '',
                                             price='\nСтоимость: {} р.'.format(vine[4]) if vine[4] else '',
                                             taste='\nВкус: {}'.format(vine[10]).replace("'", '') if vine[10] else '',
                                             sugar='\nСодержание сахара: {}'.format(vine[5]) if vine[5] else '',
                                             temperature='\nТемпература подачи: {}'.format(vine[7]) if vine[7] else '',
                                             old='\nВыдержка: {}'.format(vine[8]) if vine[8] else '',
                                             compatibility='\nСочетается с: {}'.format(vine[9])
                                                                                       .replace("'", '')
                                             .replace("'", '') if vine[9] and len(vine[9]) else ''
                                               )]
            message_for_send = '***Могу предложить тебе***\n\n{}.'.format('\n\n'.join(message_text))

        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text=message_for_send,
                              parse_mode='Markdown')

        # здесь удаляем наши знания о юзере из базы, нам это хранить ни к чему
        delete_condition('user_sessions', "user_id = '{}' and command = 'alcoholic'" .format(button.message.chat.id))

    elif button.data in kind_dict.keys():
        # здесь записываем в словарик вид алкоголя и спрашиваем его тип,
        # например цвет. Любой значит что вопросы будут продолжаться
        user_session[button.message.chat.id] = {'kind': kind_dict[button.data]}

        update_condition('user_sessions',
                         "session = '{}'".format(json.dumps(user_session[button.message.chat.id])),
                         "user_id = '{}'"
                         "and command = 'alcoholic'".format(button.message.chat.id))

        possible_types = select_condition(table='imnotalcocholic',
                                          column='type',
                                          condition=not_none_condition(user_session[button.message.chat.id]),
                                          distinct=True)
        alco_type = []
        if possible_types[0][0]:
            alco_type = [i[0].replace(', ', ' - ') if i[0] else 'Любой тип' for i in possible_types]
        alco_type += ['Любой тип', 'Мне повезёт']
        alco_type = set(alco_type)

        bot.send_message(chat_id=button.message.chat.id,
                         text='Ты выбрал {}.\nКакого типа?'.format(button.data),
                         parse_mode='Markdown',
                         reply_markup=keyboard(alco_type)
                         )
    elif button.data in all_types or button.data == 'Любой тип' or button.data.replace(' - ', ', ')  in all_types:

        # здесь записываем в словарик тип алкоголя и спрашиваем о стране
        if button.data == 'Любой тип':
            user_session[button.message.chat.id].update({'type': None})

        else:
            user_session[button.message.chat.id].update({'type': button.data.replace(' - ', ', ')})
        update_condition('user_sessions',
                         "session = '{}'".format(json.dumps(user_session[button.message.chat.id])),
                         "user_id = '{}'"
                         "and command = 'alcoholic'".format(button.message.chat.id))

        possible_country = select_condition(table='imnotalcocholic',
                                            column='country',
                                            condition=not_none_condition(user_session[button.message.chat.id]),
                                            distinct=True)
        country = []
        if possible_country[0][0]:
            country = [i[0] for i in possible_country]
        country += ['Любая страна', 'Мне повезёт']

        bot.send_message(chat_id=button.message.chat.id,
                         text='Ты выбрал {}, {}. \nИз какой страны?'
                         .format(kind_dict[user_session[button.message.chat.id]['kind']],
                                 button.data),
                         parse_mode='Markdown',
                         reply_markup=keyboard(country)
                         )

    elif button.data in all_country or button.data == 'Любая страна':
        # здесь записываем в словарик страну и узнаём ценовую категорию
        if button.data == 'Любая страна':
            user_session[button.message.chat.id].update({'country': None})
        else:
            user_session[button.message.chat.id].update({'country': button.data})

        update_condition('user_sessions',
                         "session = '{}'".format(json.dumps(user_session[button.message.chat.id])),
                         "user_id = '{}'"
                         "and command = 'alcoholic'".format(button.message.chat.id))

        possible_price = select_condition(table='imnotalcocholic',
                                          column='price',
                                          condition=not_none_condition(user_session[button.message.chat.id]),
                                          distinct=True)
        prices = []
        if possible_price[0][0]:
            for price in possible_price:
                for all_price, all_price_list in all_prices_dict.items():
                    if price[0] > all_price_list[-1] and len(all_price_list) == 1:
                        prices.append(all_price)
                    elif all_price_list[0] <= price[0] < all_price_list[-1]:
                        prices.append(all_price)
        prices += ['Любая стоимость', 'Мне повезёт']
        set(prices)

        bot.send_message(chat_id=button.message.chat.id,
                         text='Ты выбрал {}, {}, {}. \nВ какой цене?'
                         .format(kind_dict[user_session[button.message.chat.id]['kind']],
                                 user_session[button.message.chat.id]['type']
                                 if user_session[button.message.chat.id]['type']
                                 else 'Любой тип',
                                 button.data),
                         parse_mode='Markdown',
                         reply_markup=keyboard(prices)
                         )

    else:
        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Пожалуйста, подождите, идёт разработка.',
                              parse_mode='Markdown')

