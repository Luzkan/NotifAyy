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


def get_diffs(tags: List[str],
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

    return comparison_lst


def get_diffs_string_format(diffs: tuple,
                            tags: List[str]) -> tuple:

    data = [] 
    id_and_diffs = diffs
    for i in range(len(id_and_diffs)):
        alert_number = str(id_and_diffs[i][0])
        tag_diffs = id_and_diffs[i][1]
        tag_diffs_content = ""
        for h in range(len(tag_diffs)):
            tag_diffs_content += ("\nTAG ")
            tag_diffs_content += tags[h]
            tag_diffs_content += "\n"
            if tag_diffs[h]:
                tag_diffs_content += "\nBEFORE:\n"
                tag_diffs_content += str(tag_diffs[h][0][0])
                tag_diffs_content += "\nAFTER:\n"
                tag_diffs_content += str(tag_diffs[h][0][1])
            else:
                tag_diffs_content += "No changes\n"
        data.append((alert_number, tag_diffs_content))
    return data


if __name__ == "__main__":
    time_seconds = 3
    addresses = ["http://www.mediamond.fi", "https://wp.pl", "http://www.mediamond.fi"]
    tags = ["h1", "h2", "h3", "p"]
    x = get_diffs(tags, [1, 2, 3], addresses, time_seconds)
    for elem in get_diffs_string_format(x, tags):
        print(elem)
