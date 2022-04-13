import os
import requests
from keyword_normalize import *
from pathlib import Path
from os.path import exists
from datetime import datetime
from bs4 import BeautifulSoup

def save_to_csv(result: list[list[str]], file_name: str = 'result.csv') -> None:
    #file_name += '.csv'
    with open(file_name, 'w', encoding='utf-8') as f:
        for row in result:
            for col in range(len(row)):
                if col == len(row) - 1:
                    f.write(f'{row[col]}\n')
                else:
                    f.write(f'{row[col]},')


def read_keyword_list() -> list[str]:
    kws = []
    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'cache_file' / 'keywords.txt'

    if not is_cache_file_available(file_location):
        update_keyword_list()

    with open(file_location, 'r', encoding='utf-8') as f:
        for kw in f.readlines():
            #print(kw)
            kws.append(kw)

    kws = keywords_normalize(kws)

    return kws


def update_keyword_list() -> None:
    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'cache_file' / 'keywords.txt'

    url = r'https://www.rfc-editor.org/rfc-index.xml'
    r = requests.get(url)

    keywords = set()

    soup = BeautifulSoup(r.text, 'lxml')
    rfcs = soup.find_all('rfc-entry')
    
    for rfc in rfcs:
        kws = rfc.find_all('kw')
        for kw in kws:
            if kw.string is None:
                continue
            
            kw = keyword_normalize(kw.string)
            keywords.add(kw)
    
    # Save result
    with open(file_location, 'w', encoding='utf-8') as f:
        for kw in keywords:
            f.write(f'{kw}\n')


def is_cache_file_available(file_path:str) -> bool:
    if not exists(file_path):
        return False
    
    m_time = os.path.getmtime(file_path)
    dt_m = datetime.fromtimestamp(m_time)

    return dt_m.date() == datetime.today().date()

if __name__ == '__main__':
    print(read_keyword_list())