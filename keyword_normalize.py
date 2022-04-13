def keyword_normalize(keyword: str) -> str:
    keyword = keyword.lower()
    keyword = keyword.replace('-', ' ')
    keyword = keyword.strip()
    return keyword


def keywords_normalize(keywords: list[str]) -> list[str]:
    return [keyword_normalize(kw) for kw in keywords]