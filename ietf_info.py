import requests
import re
import time
from pathlib import Path
from bs4 import BeautifulSoup
from file_ops import *


def get_working_groups_list(use_cache: bool = True) -> list[str]:
    wgs_name = []

    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'cache_file' / 'wg_list.txt'

    if use_cache and is_cache_file_available(file_location):
        # read cache file
        with open(file_location, 'r', encoding='utf-8') as f:
            for wg in f.readlines():
                wg = wg.strip()
                wgs_name.append(wg)

    else:
        url = 'https://datatracker.ietf.org/wg/'
        r = requests.get(url)

        soup = BeautifulSoup(r.text, 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            a_tags = table.find_all('a')
            for a_tag in a_tags:
                if re.match('^/wg/.*', a_tag['href']):
                    wgs_name.append(a_tag.text.strip())

        # create/update cache file
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, 'w', encoding='utf-8') as f:
            for wg in wgs_name:
                f.write(f'{wg}\n')

    return wgs_name


def get_doc_list(wg_name, rfc=True, draft=True, use_cache=True):
    ''' Return all doc(rfc and draft)'s id, title and url '''

    script_location = Path(__file__).absolute().parent
    file_location = script_location / \
        'cache_file' / 'wg_docs' / f'{wg_name}.txt'

    docs = []

    text = ""

    if use_cache and is_cache_file_available(file_location):
        # read cache file
        with open(file_location, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        url = f"https://datatracker.ietf.org/wg/{wg_name}/documents"
        r = requests.get(url)
        text = r.text

        # create/update cache file
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, 'w', encoding='utf-8') as f:
            f.write(text)

    soup = BeautifulSoup(text, 'html.parser')
    doc_tds = soup.find_all('td', class_='doc')
    for doc_td in doc_tds:
        a_tag = doc_td.find('a')
        doc_id = a_tag['href']
        doc_id = doc_id.replace('doc', '').replace('/', '')

        if (draft and doc_id.startswith('draft')) or (rfc and doc_id.startswith('rfc')):
            title = a_tag.parent.findNext('b').text
            document_url = 'https://datatracker.ietf.org/doc/' + doc_id
            row = a_tag.find_parent('tr')
            status = row.find('td', class_='status')
            if 'Replaced by' in status.text:
                continue
            
            if doc_id.startswith('rfc'):
                doc_id = doc_id.replace('rfc', 'RFC', 1)
            docs.append({'id': doc_id, 'title': title, 'url': document_url})

    return docs


def get_draft_list(wg_name: str, use_cache: bool = True) -> list[dict[str, str]]:
    ''' Return all draft's id, title and url '''

    return get_doc_list(wg_name, rfc=False, draft=True, use_cache=use_cache)


def get_rfc_list(wg_name: str, use_cache: bool = True) -> list[dict[str, str]]:
    ''' Return all rfc's id, tilte and url '''

    return get_doc_list(wg_name, rfc=True, draft=False, use_cache=use_cache)


def get_RFCs_order_by_WGs(rfc_list: bool = True) -> list[dict[str, int, list[str]]]:
    '''
        Return the number of RFCs per working group
        exec time: 439 sec
    '''

    wgs = get_working_groups_list(use_cache=True)

    result = []
    for i, wg in enumerate(wgs, start=1):
        # get rfc list from wg
        print(f'{i}: {wg}')

        rfcs = get_rfc_list(wg, use_cache=True)
        wg_info = {'name': wg, 'count': 0}
        if rfc_list:
            wg_info['rfcs'] = []

        for rfc in rfcs:
            if rfc_list:
                wg_info['rfcs'].append(rfc['id'])

            wg_info['count'] += 1

        result.append(wg_info)

    result.sort(key=lambda wg_info: wg_info['count'], reverse=True)
    return result

    
    

if __name__ == '__main__':
    start_time = time.time()
    #get_RFC_keyword()
    #print(get_working_groups_list(use_cache=False))
    print("--- %s seconds ---" % (time.time() - start_time))
