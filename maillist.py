import requests
import datetime
import time
import re
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from ietf_info import get_working_groups_list
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread,local


def get_maillist_url(wg_name:str):
    url = f'https://datatracker.ietf.org/wg/{wg_name}/documents/'
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    a_tags = soup.find_all('a')

    maillist_url = f'https://mailarchive.ietf.org/arch/browse/{wg_name}/'
    for a_tag in a_tags:
        if a_tag.text == 'List archive »':
            maillist_url = a_tag['href']
            break
    
    return maillist_url


def count_maillist(wg_name:str, start_year:int, start_month:int, session):
    if wg_name == 'httpbis':
        return count_maillist_httpbis(start_year, start_month, session)

    start_date = datetime.date(start_year, start_month, 1)
    now_date = datetime.date.today()
    now_date = now_date.replace(day=1)

    result = {'wg_name': wg_name, 'sum': 0}

    url = get_maillist_url(wg_name)

    r = session.get(url)
    if not r.url.startswith("https://mailarchive.ietf.org/arch/browse/"):
        result['error'] = 'other website'
        result['url'] = url
        return result

    if r.status_code != 200:
        result['error'] = r.status_code
        return result

    wg_name = r.url.replace('https://mailarchive.ietf.org/arch/browse/', '')
    wg_name = wg_name.replace('/', '')
    print(wg_name)

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find(class_='xtbody')
    dates = table.find_all(class_='date-col')
    referenceId = table.find_all(class_='id-col')[-1].text
    referenceitem = len(dates)
    
    while len(dates) > 0:
        for date in dates:
            date = datetime.datetime.strptime(date.text, "%Y-%m-%d").date()
            if date < start_date:
                return result

            
            while date < now_date:
                key = now_date.strftime('%Y-%m')
                if key not in result:
                    result[key] = 0
                now_date = now_date - relativedelta(months=1)
                
            
            key = now_date.strftime('%Y-%m')
            if key not in result:
                result[key] = 0

            result[key] += 1
            result['sum'] += 1

            #print(date.strftime("%Y-%m-%d"))
            

        data = {
            'qid': '',
            'referenceitem': referenceitem,
            'browselist': wg_name,
            'referenceid': referenceId,
            'direction': 'next'
        }

        # get next mail list
        r = session.get('https://mailarchive.ietf.org/arch/ajax/messages/', params=data)
        if r.status_code != 200:
            break
        
        soup = BeautifulSoup(r.text, 'html.parser')
        dates = soup.find_all(class_='date-col')
        referenceId = soup.find_all(class_='id-col')[-1].text
        referenceitem += len(dates)

    
    return result


def count_maillist_httpbis(start_year:int, start_month:int, session):
    start_date = datetime.date(start_year, start_month, 1)

    result = {'wg_name': 'httpbis', 'sum': 0}
    url = 'https://lists.w3.org/Archives/Public/ietf-http-wg/'
    r = session.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    a_tags = table.find_all("a", href=re.compile('[0-9]{4}([A-Z][a-z]{2}){2}/$'))
    exit = False
    for a_tag in a_tags:
        # 每三個月的紀錄
        href = a_tag['href']
        href = url + href
        r = session.get(href)
        soup = BeautifulSoup(r.text, 'html.parser')

        dates_msg = soup.find_all('dfn', text=re.compile('.*, +\d+ [a-zA-Z]+ \d{4}'))
        for date_msg in dates_msg:
            # 紀錄中的日期(會多筆訊息)
            date = datetime.datetime.strptime(date_msg.text,'%A, %d %B %Y').date()
            if date < start_date:
                exit = True
                break

            key = date.strftime('%Y-%m')
            if not key in result:
                result[key] = 0

            rows = date_msg.find_next_sibling('ul')
            result[key] += len(rows.find_all('li'))
            result['sum'] += len(rows.find_all('li'))
        
        if exit:
            break
    
    return result




def rank_wg_by_maillist(start_year=2020, start_month=1):
    wgs = get_working_groups_list()

    maillists = []
    
    processes = []
    session = requests.Session()
    with ThreadPoolExecutor(max_workers=10) as executor:
        for wg in wgs:
            processes.append(executor.submit(count_maillist, wg, start_year, start_month, session))
        
        for _ in as_completed(processes):
            maillists.append(_.result())
    
    keylist = []
    start_date = datetime.date(start_year, start_month, 1)
    now_date = datetime.date.today()
    now_date = now_date.replace(day=1)

    while(now_date >= start_date):
        keylist.append(now_date.strftime('%Y-%m'))
        now_date = now_date - relativedelta(months=1)

    maillists.sort(key=lambda x: [x.get(k, 0) for k in keylist], reverse=True)
    #print(keylist)
    return maillists


if __name__ == '__main__':
    start_time = time.time()
    print(*rank_wg_by_maillist(2022, 1), sep='\n')
    #print(get_maillist_url('avtcore'))
    #print(count_maillist('avtcore', 2022, 1))
    #print(count_maillist_httpbis(2022, 1))
    print("--- %s seconds ---" % (time.time() - start_time))