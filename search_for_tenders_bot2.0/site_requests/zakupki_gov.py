import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from config import HEADERS
import main


async def search(date_now, title, session, time_slot, count):
    data = {'searchString': title}
    list_of_answers = []
    try:
        async with session.get('https://zakupki.gov.ru/epz/order/extendedsearch/results.html', headers=HEADERS, params=data) as responce:
            soup = BeautifulSoup(await responce.text(), 'lxml')
            data = soup.find_all('div', {'class': 'row no-gutters registry-entry__form mr-0'})
            for elem in data:
                date = elem.find('div', {'class': 'data-block mt-auto'}).find_all('div', {'class': 'data-block__value'})
                day2, m2, y2 = list(map(lambda x: int(x), date[1].text.split('.')))
                placement_date = datetime(y2, m2, day2)
                if 0 <= (date_now - placement_date).days <= time_slot:
                    header = elem.find('div', {'class': 'registry-entry__header-mid__number'}).find('a', {'target': '_blank'})
                    number = header.text.rstrip().lstrip()
                    more_info = f'https://zakupki.gov.ru{header["href"]}'
                    name = elem.find('div', {'class': 'registry-entry__body-value'}).text
                    customer = elem.find('div', {'class': 'registry-entry__body-href'}).find('a', {'target': '_blank'}).text.rstrip().lstrip()
                    price = elem.find('div', {'class': 'price-block__value'}).text.rstrip().lstrip() if elem.find('div', {'class': 'price-block__value'}) != None else 'НЕТ'
                    if len(date) == 3:
                        end_date = date[-1].text
                        day, m, y = list(map(lambda x: int(x), end_date.split('.')))
                        request_date = datetime(y, m, day)
                        d = request_date - date_now
                        if d.days < 0:
                            break
                        end_date = f'{d.days} дней ({end_date})'
                    else:
                        end_date = 'нет времени окончания подачи заявок'
                    list_of_answers.append({"number": number,
                                            "name": name,
                                            "customer": customer,
                                            "price": price,
                                            "end_date": end_date,
                                            "more_info": more_info})
    except:
        pass
    count["ЕИС закупки"] += 1
    return list_of_answers

#print(site_request(datetime.now(), 'техническое обследование'))