from bs4 import BeautifulSoup
from datetime import datetime
from config import HEADERS


async def search(date_now, title, session, time_slot, count):
    data = {'q': title, 'page': 1}
    list_of_answers = []
    try:
        async with session.get('https://www.etp-ets.ru/44/catalog/procedure', headers=HEADERS, params=data) as response:
            soup = BeautifulSoup(await response.text(), 'lxml').find('table', {}).find_all('tr', {})[1:]
            i = 2
            if soup and soup[0].find('td', {}).text != 'Данных не найдено':
                for obj in soup:
                    date = obj.find('td', {'class': f'row-publication_datetime{" sortable" * i}'}).text.split('(')[0]
                    day1, m1, y1 = list(map(lambda x: int(x), date.split(' ')[0].split('.')))
                    h1, minute1, s1 = list(map(lambda x: int(x), date.split(' ')[1].split(':')))
                    public_date = datetime(y1, m1, day1, h1, minute1, s1)
                    d1 = date_now - public_date
                    if 0 <= d1.days <= time_slot:
                        number = obj.find('td', {'class': 'row-procedure_name'}).text.rstrip().lstrip().split(' ')[-1][1:-1]
                        name = obj.find('td', {'class': 'row-procedure_name'}).find('a', {}).text.rstrip().lstrip()
                        customer = obj.find('td', {'class': 'row-customer_name'}).find('a', {}).text.rstrip().lstrip()
                        price = obj.find('td', {'class': f'row-contract_start_price{" sortable" * i}'}).text.rstrip().lstrip()
                        date = obj.find('td', {'class': f'row-request_end_give_datetime{" sortable" * i}'}).text
                        i += 1
                        day, m, y = list(map(lambda x: int(x), date.split(' ')[0].split('.')))
                        h, minute, s = list(map(lambda x: int(x), date.split(' ')[1].split('(')[0].split(':')))
                        request_date = datetime(y, m, day, h, minute, s)
                        d = (request_date - date_now).days
                        if d < 0:
                            break
                        else:
                            end_date = f'{d} дней ({date.split("(")[0]})'
                            more_info = obj.find('td', {'class': 'row-procedure_name'}).find('a', {})['href']
                            list_of_answers.append({
                                "number": number,
                                "name": name,
                                "customer": customer,
                                "price": price + " руб.",
                                "end_date": end_date,
                                "more_info": more_info
                            })
                    else:
                        i += 1
    except:
        pass
    count["Фабрикант"] += 1
    return list_of_answers