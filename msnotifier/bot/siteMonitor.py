import urllib.request
import time
from bs4 import BeautifulSoup
from typing import List

class Alert:
    def __init__(self,adr,user_id):
        self.adr=adr
        self.user_id=user_id
        self.errors=[]


def compare_content_by_tags(previous: List[List[str]],
                            current: List[List[str]]) -> List[List[tuple]]:
    length = len(current)
    diffs = [[] for i in range(length)]
    for i in range(length):
        for elem in modified_zip(previous[i], current[i]):
            if elem[0] != elem[1]:
                diffs[i].append(elem)
    return diffs


def get_content(url: str) -> str:
    return urllib.request.urlopen(url).read()


def modified_zip(first: list, second: list):
    result = [elem for elem in zip(first, second)]
    if len(first) > len(result):
        for i in range(len(result), len(first)):
            result.append((first[i], None))
    elif len(second) > len(result):
        for i in range(len(result), len(second)):
            result.append((None, second[i]))
    return result


def split_content_by_tags(html: str, tags: List[str]) -> List[List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    return [soup.find_all(tag) for tag in tags]


def get_diffs(tags: List[str], addresses: List[Alert], t: float) -> list:
    before = [split_content_by_tags(get_content(url.adr), tags) for url in addresses]
    time.sleep(t)
    after = [split_content_by_tags(get_content(url.adr), tags) for url in addresses]
    comparison_lst = []
    for i in range(len(before)):
        comparison_lst.append(compare_content_by_tags(before[i], after[i]))
    return comparison_lst


"""
For each website there are tag_diffs, which are tuples of content with the tag before and after
Example print for data below:
[]
[]
[(<h1 class="ywentc-1 gSKBNp"><a class="sc-1opjz2c-0 hJbLrA" href="https://wiadomosci.wp.pl/">
Tym żyje Polska <span class="ywentc-5 ciJuja">
</span></a></h1>, None)]
[]
It means that mediamond.fi webpage didn't have any h1, h2 differences,
while wp.pl had differences in h1, in that case there was one item with h1 tag, and afterwards None of them. 
"""
if __name__ == "__main__":
    time_seconds = 10
    addresses = [Alert("https://www.onet.pl",1)]
    for elem in get_diffs(["h1", "h2"], addresses, time_seconds):
        for tag_diff in elem:
            print(tag_diff)
