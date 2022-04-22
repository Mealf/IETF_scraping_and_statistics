import time
from ietf_info import *
from file_ops import *
from keyword_handle import *


def get_RFC_keyword():
    ''' 從rfc-index.xml取得官方關鍵字 '''
    # TODO: 重複關鍵字問題
    result = []

    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'data' / 'RFC_keywords.csv'

    url = r'https://www.rfc-editor.org/rfc-index.xml'
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'lxml')
    rfcs = soup.find_all('rfc-entry')

    for rfc in rfcs:
        id = rfc.find('doc-id').string
        kw_tags = rfc.find_all('kw')
        for kw_tag in kw_tags:
            kw = kw_tag.string
            if kw is None:
                continue
            
            # avoid ',' in <kw></kw>
            for kw in kw.split(','):
                kw = keyword_normalize(kw)
                if kw != '':
                    result.append([id, kw])
    
    save_to_csv(result, file_location)

    return result


def get_keyword_from_title():
    ''' 從RFC與draft的標題中取得關鍵字 '''
    # TODO: 重複關鍵字問題
    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'data' / 'title_keyword.csv'

    wgs = get_working_groups_list()
    keyword_list = get_keyword_list()

    result = []

    for i, wg in enumerate(wgs, start=1):
        print(f'{i}: {wg}')

        # 從wg取得所有文件名稱
        docs = get_doc_list(wg)
        for doc in docs:
            title = doc['title']
            id = doc['id']

            # 從文件名稱取得關鍵字
            for kw in get_keyword_from_text(title):
                result.append([id, kw])


    save_to_csv(result, file_location)

    return result


if __name__ == '__main__':
    start_time = time.time()
    get_RFC_keyword()
    print("--- %s seconds ---" % (time.time() - start_time))