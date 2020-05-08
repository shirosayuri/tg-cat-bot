# -*- coding: utf-8 -*-
import json
from bot import bot
from telebot import types
from postgres_func import select_random, select_condition, insert_condition, update_condition, delete_condition
import os


log_chat = os.environ['admin_chat_id']

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


all_kinds = [i[0] for i in select_condition(table='imnotalcocholic',
                                            column='kind',
                                            distinct=True)]

all_types = [i[0] for i in select_condition(table='imnotalcocholic',
                                            column='type',
                                            distinct=True)]

all_country = [i[0] for i in select_condition(table='imnotalcocholic',
                                              column='country',
                                              distinct=True)]

all_prices_dict = {'< 300 р.': [1, 300],
                   '300 - 700 р.': [300, 700],
                   '700 - 1200 р.': [700, 1200],
                   '1 200 - 2 000 р.': [1200, 2000],
                   '2 000 - 4 000 р.': [2000, 4000],
                   '4 000 - 6 000 р.': [4000, 6000],
                   '6 000 - 10 000 р.': [6000, 1000],
                   '10 000 - 15 000 р.': [10000, 15000],
                   '15 000 - 20 000 р.': [15000, 20000],
                   '> 20 000 р.': [20000, ]}


@bot.message_handler(commands=['alcoholic'])
def start_vine_msg(message):
    # здесь добавляем юзера в таблицу с юзерскими сессиями,
    # чтобы не потерять его на просторах асинхронного программирования

    try:

        kinds = []
        for i in select_condition(table='imnotalcocholic', column='kind', distinct=True):
            kinds.append(i[0])
        kinds.append('Мне повезёт')
        bot.send_message(chat_id=message.chat.id,
                         text='Что ты хочешь выпить?',
                         parse_mode='Markdown',
                         reply_markup=keyboard(kinds)
                         )
        if not select_condition('user_sessions', 'user_id',
                                "user_id = '{}' and command = 'alcoholic'".format(message.chat.id)):
            insert_condition(table='user_sessions', values=(str(message.chat.id), 'alcoholic'),
                             columns='(user_id, command)')
    except Exception as e:
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in imnotalcocholic at start_vine_msg func'.format(e)
                         )
        bot.send_message(chat_id=message.chat.id,
                         text='Ой, что-то пошло не так. Попробуй ещё раз.',
                         parse_mode='Markdown'
                         )


@bot.callback_query_handler(func=lambda c: True)
def button(button):

    if button.data == 'Мне повезёт' or button.data in all_prices_dict.keys() or button.data == 'Любая стоимость':
        # здесь смотрим на юзерскую сессию если она есть
        user_session = {}
        user_session[button.message.chat.id] = select_condition('user_sessions',
                                                                'session',
                                                                "user_id = '{}'"
                                                                "and command = 'alcoholic'"
                                                                .format(button.message.chat.id))[0][0]
        vine_condition = not_none_condition(user_session[button.message.chat.id]) if user_session[
            button.message.chat.id] else ''
        if button.data in all_prices_dict.keys() and button.data != '> 20 000 р.':
            vine_condition += ' and price between {} and {}'.format(all_prices_dict[button.data][0], all_prices_dict[button.data][1])
        elif button.data == '> 20 000 р.':
            vine_condition += 'and price > 20000'

        vines = select_random('imnotalcocholic',
                              'title, ' # 0
                              'kind, ' # 1
                              'alcohol, ' # 2
                              'country, ' # 3
                              'price, '# 4
                              'sugar, ' # 5
                              'type, ' # 6
                              'temperature, ' # 7
                              'old,' # 8
                              'compatibility, ' # 9
                              'taste, ' # 10
                              'link ', # 11
                              vine_condition,
                              limit=3)
        message_text = []
        # здесь составляем текст если первый вопрос был выбран или нет, то есть если мы знаем тип или нет
        if user_session[button.message.chat.id] and user_session[button.message.chat.id]['kind']:
            for vine in vines:
                # если тип выбран
                message_text += ['{title}. {alcohol}{type}{country}{price}{taste}{sugar}'
                                 '{temperature}{old}{compatibility}'
                                     .format(title='\n[{}]({})'.format(vine[0], vine[11]),
                                             alcohol='\nПроцент алкоголя: {}'.format(vine[2]) if vine[2]
                                             else '\nПроцент алкоголя не написали 😭',
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
                .format(user_session[button.message.chat.id]['kind'].lower(),
                        '\n'.join(message_text))

        else:
            # если тип не выбран
            for vine in vines:
                message_text += ['{kind}: {title}. {alcohol}{type}{country}{price}{taste}{sugar}'
                                 '{temperature}{old}{compatibility}'
                                     .format(title='\n[{}]({})'.format(vine[0], vine[11]),
                                             kind=vine[1],
                                             alcohol='\nПроцент алкоголя: {}'.format(vine[2]) if vine[2]
                                             else '\nПроцент алкоголя не написали 😭',
                                             type='\nТип алкоголя: {}'.format(vine[6]) if vine[6] else '',
                                             country='\nСтрана происхождения: {}'.format(vine[3]) if vine[2] else '',
                                             price='\nСтоимость: {} р.'.format(vine[4]) if vine[4] else '',
                                             taste='\nВкус: {}'.format(vine[10]) if vine[10] else '',
                                             sugar='\nСодержание сахара: {}'.format(vine[5]) if vine[5] else '',
                                             temperature='\nТемпература подачи: {}'.format(vine[7]) if vine[7] else '',
                                             old='\nВыдержка: {}'.format(vine[8]) if vine[8] else '',
                                             compatibility='\nСочетается с: {}'.format(vine[9]) if vine[9] and len(vine[9]) else ''
                                             )]
            message_for_send = '***Могу предложить тебе***\n\n{}.'.format('\n\n'.join(message_text))

        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text=message_for_send,
                              parse_mode='Markdown',
                              disable_web_page_preview=True)

        # здесь удаляем наши знания о юзере из базы, нам это хранить ни к чему
        delete_condition('user_sessions', "user_id = '{}' and command = 'alcoholic'" .format(button.message.chat.id))

    elif button.data in all_kinds:
        # здесь записываем в словарик вид алкоголя и спрашиваем его тип,
        # например цвет. Любой значит что вопросы будут продолжаться
        user_session = {}
        user_session[button.message.chat.id] = select_condition('user_sessions',
                                                                'session',
                                                                "user_id = '{}'"
                                                                "and command = 'alcoholic'"
                                                                .format(button.message.chat.id))[0][0]
        user_session[button.message.chat.id] = {'kind': button.data}

        update_condition('user_sessions',
                         "session = '{}'".format(json.dumps(user_session[button.message.chat.id])),
                         "user_id = '{}'"
                         "and command = 'alcoholic'".format(button.message.chat.id))

        possible_types = select_condition(table='imnotalcocholic',
                                          column='type',
                                          condition=not_none_condition(user_session[button.message.chat.id]),
                                          distinct=True)
        alco_type = []
        if possible_types[0]:
            alco_type = [i[0].replace(', ', ' - ') if i[0] and i[0] not in all_kinds else 'Любой тип' for i in possible_types]
        alco_type += ['Любой тип', 'Мне повезёт']
        alco_type = set(alco_type)

        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Ты выбрал {}.\nКакого типа?'.format(button.data),
                              parse_mode='Markdown',
                              reply_markup=keyboard(alco_type)
                              )
    elif button.data in all_types or button.data == 'Любой тип' or button.data.replace(' - ', ', ') in all_types:
        user_session = {}
        user_session[button.message.chat.id] = select_condition('user_sessions',
                                                                'session',
                                                                "user_id = '{}'"
                                                                "and command = 'alcoholic'"
                                                                .format(button.message.chat.id))[0][0]
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
        if possible_country[0]:
            country = [i[0] if i[0] else 'Любая страна' for i in possible_country]
        country += ['Любая страна', 'Мне повезёт']

        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Ты выбрал {}, {}. \nИз какой страны?'
                              .format(user_session[button.message.chat.id]['kind'],
                                      button.data),
                              parse_mode='Markdown',
                              reply_markup=keyboard(country)
                              )

    elif button.data in all_country or button.data == 'Любая страна':
        user_session = {}
        user_session[button.message.chat.id] = select_condition('user_sessions',
                                                                'session',
                                                                "user_id = '{}'"
                                                                "and command = 'alcoholic'"
                                                                .format(button.message.chat.id))[0][0]
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
        if possible_price[0]:
            for price in possible_price:
                for all_price, all_price_list in all_prices_dict.items():
                    if all_price_list[0] <= price[0] < all_price_list[-1]:
                        prices.append(all_price)
                    elif price[0] > all_price_list[0] and all_price_list[-1] == all_price_list[0]:
                        prices.append(all_price)
                    else:
                        prices.append('Любая стоимость')
        prices += ['Любая стоимость', 'Мне повезёт']
        prices = set(prices)

        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Ты выбрал {}, {}, {}. \nВ какой цене?'
                              .format(user_session[button.message.chat.id]['kind'],
                                      user_session[button.message.chat.id]['type']
                                      if user_session[button.message.chat.id]['type']
                                      else 'Любой тип',
                                      button.data),
                              parse_mode='Markdown',
                              reply_markup=keyboard(prices))

    else:
        bot.edit_message_text(chat_id=button.message.chat.id,
                              message_id=button.message.message_id,
                              text='Ой, что-то пошло не так. Давай попробуем ещё раз?\nНу пожалуйста-пожалуйста.🥺',
                              parse_mode='Markdown')

