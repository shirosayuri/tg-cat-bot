import requests
from bs4 import BeautifulSoup
import re
from random import randint
from bot import bot
import os

log_chat = os.environ['admin_chat_id']


def get_cat():
    try:
        r = requests.get('http://thecatapi.com/api/images/get?format=src')
        url = r.url
    except Exception as e:
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in functions at get_cat func'.format(e)
                         )
        url = get_cat()
        pass
    return url


def enough(txt):
    return True if txt in ('хватит', 'Хватит', 'Хватит.', 'Хватит!') else False


def get_current_page(path):
    return BeautifulSoup(requests.get(path).text, features="html.parser")


def bashim():
    url = 'http://bash.im/random'
    i = 0
    while i < 2:
        i += 1
        try:
            htmlcode = get_current_page(url)
            qtexts = []
            for qtext in htmlcode.find_all("div", class_="quote__body"):
                qtext = re.sub('<div class="quote__body">|</div>', "", str(qtext))
                qtext = re.sub('<br/>', "\n", str(qtext))
                if len(qtext) < 200:
                    qtexts.append(qtext)
                if qtexts:
                    return qtexts[randint(0, len(qtexts)-1)].strip()
        except Exception as e:
            bot.send_message(chat_id=log_chat,
                             text='Exception {} in functions at bashim func'.format(e)
                             )


def poetory():
    url = 'https://poetory.ru/all/rating'
    status_code = requests.get(url).status_code
    try:
        if status_code == 200:
            htmlcode = get_current_page(url)
            summary = int(htmlcode.find("div", class_="summary").text.strip().split(' ')[-1])
            htmlcode = get_current_page('https://poetory.ru/{}'.format(randint(1, summary)))
            poetry = htmlcode.find('div', class_='item-text').text
            if poetry and poetry != 'None':
                return poetry
    except Exception as e:
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in functions at bashim func'.format(e)
                         )

