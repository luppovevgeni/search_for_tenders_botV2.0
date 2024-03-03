import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import HEADERS


async def search(date_now, title, session, time_slot, count):
    list_of_answers = []
    try:
        async with session.get(f'https://www.roseltorg.ru/procedures/search?query_field={title}', headers=HEADERS) as responce:
            soup = BeautifulSoup(await responce.text(), 'lxml').find_all('div', {'class': "search-results__item"})
            for obj in soup:
                date = obj.find('time', {'class': 'search-results__time'})
                end_date = date.text[:11].rstrip().lstrip()
                if (end_date - date_now).days > 0:
                    number = obj.find('div', {'class': 'search-results__lot'}).text.rstrip().lstrip()
                    name = obj.find('div', {'class': 'search-results__subject'}).text.rstrip().lstrip()
                    customer = obj.find('div', {'class': 'search-results__customer'}).text.rstrip().lstrip()
                    price = obj.find('div', {'class': 'search-results__sum'}).find('p', {}).text.rstrip().lstrip() + ' руб.'
                    more_info = 'https://www.roseltorg.ru/' + obj.find('a', {'class': 'search-results__link'})['href']
                    list_of_answers.append({"number": number,
                                            "name": name,
                                            "customer": customer,
                                            "price": price,
                                            "end_date": f'{((end_date - date_now).days)} дней ({end_date})',
                                            "more_info": more_info})
    except:
        pass
    count["Росэлторг"] += 1
    return list_of_answers