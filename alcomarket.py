import requests
from bs4 import BeautifulSoup
from postgres_func import insert_condition, select_condition, update_condition

base_url = 'https://alcomarket.ru'


def get_current_page(path):
    return BeautifulSoup(requests.get(path).text, features="html.parser")


def parse_one_item(item_soup):
    a_tag = item_soup.find('a')
    href = a_tag.attrs.get('href')
    if 'wine' in href.split('/'):
        kind = 'wine'
    elif 'shampanskoe-i-igristoe' in href.split('/'):
        kind = 'champagne'
    elif 'rom' in href.split('/'):
        kind = 'rum'
    elif 'viski' in href.split('/'):
        kind = 'whiskey'
    elif 'cognac' in href.split('/'):
        kind = 'cognac'
    elif 'likery' in href.split('/'):
        kind = 'liquors'
    elif 'vodka' in href.split('/'):
        kind = 'vodka'
    elif 'gin' in href.split('/'):
        kind = 'gin'
    elif 'absent' in href.split('/'):
        kind = 'absinthe'
    elif 'aperitive' in href.split('/'):
        kind = 'aperitif'
    elif 'armanyak' in href.split('/'):
        kind = 'armagnac'
    elif 'brendi' in href.split('/'):
        kind = 'brandy'
    elif 'grappa' in href.split('/'):
        kind = 'grappa'
    elif 'kalvados' in href.split('/'):
        kind = 'calvados'
    elif 'tequila' in href.split('/'):
        kind = 'tequila'
    elif 'voda' in href.split('/'):
        kind = 'water'
    elif 'sok' in href.split('/'):
        kind = 'juice'
    else:
        kind = 'Unknown'
    title = a_tag.attrs.get('title')
    cur_soup = get_current_page(base_url + href)
    all_sets = cur_soup.find_all('div', attrs={'class': 'col-xs-6'})
    price = cur_soup.find_all('div', attrs={'class': 'price'})[0].find('span').text
    item_dict = {}
    country, alco_type, sugar, temperature, grape, alcohol, compatibility, taste, old, alco_class, material, color, \
    style, alco_filter, added, distillation = [None for i in range(0, 16)]
    for one_set in all_sets:
        title = title
        item = one_set.text.replace('\t', '').strip().split('\n')
        if item[0] == 'Страна':
            country = item[-1].strip()
        if item[0] == 'Тип':
            alco_type = item[-1].strip()
        if item[0] == 'Сахар':
            sugar = item[-1].strip()
        if item[0] == 'Подача':
            temperature = item[-1].strip()
        if item[0] == 'Сорт винограда':
            grape = item[-1].strip()
        if item[0] == 'Алкоголь':
            alcohol = item[-1].strip()
        if item[0] == 'Сочетаемость':
            compatibility = str(item[1:-1])
        if item[0] == 'Вкус':
            taste = str(item[1:-1])
        if item[0] == 'Выдержка':
            old = item[-1].strip()
        if item[0] == 'Класс':
            alco_class = item[-1].strip()
        if item[0] == 'Материал' or item[0] == 'Сырье':
            material = item[-1].strip()
        if item[0] == 'Цвет':
            color = item[-1].strip()
        if item[0] == 'Стиль':
            style = item[-1].strip()
        if item[0] == 'Фильтрация':
            alco_filter = item[-1].strip()
        if item[0] == 'Добавки':
            added = item[-1].strip()
        if item[0] == 'Дистилляция':
            distillation = item[-1].strip()
    item_dict.update({'title': title,
                      'country': country,
                      'type': alco_type,
                      'sugar': sugar,
                      'temperature': temperature,
                      'grape': grape,
                      'alcohol': alcohol,
                      'compatibility': compatibility,
                      'taste': taste,
                      'old': old,
                      'class': alco_class,
                      'material': material,
                      'color': color,
                      'style': style,
                      'filter': alco_filter,
                      'added': added,
                      'distillation': distillation,
                      'link': base_url+href,
                      'price': int(price),
                      'kind': kind})
    try:
        alcochol_exists = select_condition('imnotalcocholic', 'title', "title = '{title}'".format(title=title))
        if alcochol_exists:
            return True
        else:
            insert_condition('imnotalcocholic', tuple(item_dict.values()), str(tuple(item_dict.keys())).replace("'", ''))
            return True
    except Exception as e:
        return None


def parse_full_page(wine_soup):
    try:
        all_items = wine_soup.find_all('div', attrs={'class': 'catalog_item'})
        [parse_one_item(x) for x in all_items]
        return True
    except Exception as e:
        return None


def get_next_page_url(wine_soup):
    try:
        next_page_href = (wine_soup.find('a', attrs={'title': 'Следующая страница'}).attrs.get('href'))
        return base_url + next_page_href
    except Exception as e:
        return None

add_urls = ['/catalog/krepkiy-alkogol/', '/catalog/water/', '/catalog/wine/', '/catalog/shampanskoe-i-igristoe/', ]
full_sh_list = []
for add_url in add_urls:
    wine_html = requests.get(base_url + add_url)

    wine_soup = BeautifulSoup(wine_html.text, features="html.parser")

    # get data from the first page
    full_sh_list = parse_full_page(wine_soup)

    page_number = 1
    cur_soup = wine_soup
    while get_next_page_url(cur_soup):
        page_number += 1
        next_page_full_path = get_next_page_url(cur_soup)
        cur_soup = BeautifulSoup(requests.get(next_page_full_path).text, features="html.parser")
        try:
            parse_full_page(cur_soup)
        except Exception as e:
            print(e)
            break


