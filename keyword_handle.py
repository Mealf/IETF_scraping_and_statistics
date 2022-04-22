import re
import time
from file_ops import get_keyword_list
from keyword_normalize import *



def get_keyword_from_text(text: str) -> list[str]:
    keyword_list = get_keyword_list()
    result = set()

    text = text.replace('\n', '')
    # 分行用的'-'會有問題?
    text = text.replace('-', ' ')
    # 去括號
    text = text.replace('(', ' ')
    text = text.replace(')', ' ')
    # 移除多餘空白
    text = re.sub(' +', ' ', text)
    # 移除前後空白
    text = text.strip()

    tokens = text.split(' ')
    words = []

    max_token = get_keyword_list_max_token()

    for token in tokens:
        words.append('')

        for i in reversed(range(len(words))):
            words[i] += ' ' + token
            words[i] = keyword_normalize(words[i])
            if words[i] in keyword_list:
                result.add(words[i])

            if len(words[i].split()) > max_token:
                words.pop(i)
    return list(result)


def get_keyword_list_max_token() -> int:
    keyword_list = get_keyword_list()
    max_token = 0

    for kw in keyword_list:
        max_token = max(len(kw.split()), max_token)

    return max_token
        


if __name__ == '__main__':
    start_time = time.time()
    
    print("--- %s seconds ---" % (time.time() - start_time))