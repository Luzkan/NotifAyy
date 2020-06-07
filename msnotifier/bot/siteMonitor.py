import urllib.request
import time
from bs4 import BeautifulSoup
from typing import List


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


def get_diffs(user_id: int,
              tags: List[str],
              alert_ids: List[int],
              addresses: List[str],
              t: float) -> tuple:

    before = [(alert_ids[i], split_content_by_tags(get_content(addresses[i]), tags))
              for i in range(len(addresses))]

    time.sleep(t)

    after = [(alert_ids[i], split_content_by_tags(get_content(addresses[i]), tags))
             for i in range(len(addresses))]

    comparison_lst = [(alert_ids[i], compare_content_by_tags(before[i][1], after[i][1]))
                      for i in range(len(before))]

    return user_id, comparison_lst


def get_diffs_string_format(diffs: tuple, 
                            titles: List[str], 
                            addresses: List[str], 
                            tags: List[str]) -> None:
    message = ""
    id_and_diffs = diffs[1]
    for i in range(len(id_and_diffs)):
        message += "\n"
        message += ("Changes for alert number ")
        message += str(id_and_diffs[i][0])
        message += " with title: "
        message += titles[i]
        message += " and address: "
        message += addresses[i]
        message += "\n\n"
        tag_diffs = id_and_diffs[i][1]
        for h in range(len(tag_diffs)):
            message += ("TAG")
            message += tags[h]
            message += "\n"
            if tag_diffs[h]:
                message += "\nBEFORE:\n"
                message += str(tag_diffs[h][0][0])
                message += "\nAFTER:\n"
                message += str(tag_diffs[h][0][1])
            else:
                message += "No changes\n"
    return message



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
    time_seconds = 3
    addresses = ["http://www.mediamond.fi", "https://wp.pl", "http://www.mediamond.fi"]
    tags = ["h1", "h2", "h3", "p"]
    x = get_diffs(14184148, tags, [1, 2, 3], addresses, time_seconds)
    print(get_diffs_string_format(x, ["Alert 1", "Alert 2", "Alert 3"], addresses, tags))
