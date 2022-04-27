import re
from pathlib import Path
from file_ops import save_to_csv, get_keyword_list
from keyword_normalize import keyword_normalize
from get_keyword import get_keyword_from_title, get_RFC_keyword


def contains_word(s, subs):
    return f'{subs} ' in f' {s} '

               
def put_keyword_to_dict(keyword_list ,keywords, brackets_list):
    for keyword in keyword_list:
        if '(' in keyword:
            brackets_list.append(keyword)
        keywords[keyword] = {'next': set(), 'Docs': set()}


def bracket_processing(keywords, brackets_list):
    for keyword in brackets_list:
        abbreviation = keyword[keyword.find('(')+1: keyword.find(')')]
        brackets_removed = re.sub(r" *\([^()]*\) *", ' ', keyword)
        brackets_removed = brackets_removed.strip()
        

        # 括號內的縮寫加入關聯
        if abbreviation in keywords:
            keywords[keyword]['next'].add(abbreviation)
        
        #移除括號後加入關聯
        if brackets_removed in keywords:
            keywords[keyword]['next'].add(brackets_removed)

        #括號內的縮寫與前面的字關聯
        check = True
        for i in range(keyword.find('(')):
            if keyword[i] == ' ':
                check = True
            else:
                check = False
                if abbreviation!='' and keyword[i] == abbreviation[0]:
                    full_name = keyword[i: keyword.find('(')]
                    full_name = full_name.strip()

                    if len(full_name) < len(abbreviation):
                        full_name, abbreviation = abbreviation, full_name
                    if abbreviation in keywords and full_name in keywords:
                        keywords[abbreviation]['next'].add(full_name)
                    break
        

def abbreviation_processing(keywords):
    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'data' / 'abbreviations_list.csv'
    with open(file_location, 'r', encoding='utf-8') as f:
        rows = f.readlines()
        for row in rows:
            abbreviation, kw = row.split(',')
            abbreviation = keyword_normalize(abbreviation)
            kw = keyword_normalize(kw)

            if kw in keywords and abbreviation in keywords:
                # 雙向關聯
                keywords[abbreviation]['next'].add(kw)
                keywords[kw]['next'].add(abbreviation)


def word_break_processing(keyword_list, keywords):
    for keyword in keyword_list:
        if '(' in keyword:
            continue
        
        words = keyword.split()
        for word_size in range(1, len(words)):
            for start in range(0, len(words)-word_size+1):
                s = ' '.join(words[start:start+word_size])
                if s in keywords:
                    keywords[keyword]['next'].add(s)



def extend_keyword(keywords, docs_kw):
    result = []
    added = dict()
    for doc_kw in docs_kw:
        doc, kw = doc_kw
        
        if doc not in added:
            added[doc] = set()
        
        kw = keyword_normalize(kw)
        if kw in added[doc]:
            continue

        result.append([doc, kw])
        added[doc].add(kw)
        dfs_extend_keyword(keywords, doc, kw, added[doc], result)
    
    # save result
    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'data' / 'rfc_keyword_extend.csv'
    save_to_csv(result, file_location)


def dfs_extend_keyword(keywords, rfc, kw, added, result):
    if kw not in keywords:
        return 
    for next in keywords[kw]['next']:
        if next not in added:
            result.append([rfc, next])
            added.add(next)
            dfs_extend_keyword(keywords, rfc, next, added, result)


if __name__ == '__main__':
    brackets_list = []
    keyword_list = []
    keywords = dict()

    keyword_list = get_keyword_list()
    #print('for' in keyword_list)
    put_keyword_to_dict(keyword_list, keywords, brackets_list)
    bracket_processing(keywords, brackets_list)
    abbreviation_processing(keywords)
    word_break_processing(keyword_list, keywords)

    docs_kw = get_RFC_keyword() + get_keyword_from_title()
    extend_keyword(keywords, docs_kw)
