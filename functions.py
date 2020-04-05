import requests
from bs4 import BeautifulSoup
import re
from random import randint


def get_cat():
    try:
        r = requests.get('http://thecatapi.com/api/images/get?format=src')
        url = r.url
    except Exception as error:
        url = get_cat()
        print('Error with cat parsing')
        pass
    return url


def enough(txt):
    return True if txt in ('хватит', 'Хватит', 'Хватит.', 'Хватит!') else False


def get_current_page(path):
    return BeautifulSoup(requests.get(path).text, features="html.parser")


def bashim():
    url = 'http://bash.im/random'
    status_code = requests.get(url).status_code
    htmlcode = get_current_page(url)
    qtexts = []
    for qtext in htmlcode.find_all("div", class_="quote__body"):
        qtext = re.sub('<div class="quote__body">|</div>', "", str(qtext))
        qtext = re.sub('<br/>', "\n", str(qtext))
        if len(qtext) < 200:
            qtexts.append(qtext)
    return qtexts[randint(0, len(qtexts))].strip()


def poetory():
    url = 'https://poetory.ru/all/rating'
    status_code = requests.get(url).status_code
    if status_code == 200:
        htmlcode = get_current_page(url)
        summary = int(htmlcode.find("div", class_="summary").text.strip().split(' ')[-1])
        htmlcode = get_current_page('https://poetory.ru/{}'.format(randint(1, summary)))
        poetry = htmlcode.find('div', class_='item-text').text
        if poetry and poetry != 'None':
            return poetry
        else:
            return None
    else:
        raise ValueError
