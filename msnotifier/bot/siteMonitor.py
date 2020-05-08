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


def example_usage(url: str, t: float) -> None:
    tags = ["a", "h1", "h2", "p"]
    while True:
        x = split_content_by_tags(get_content(url), tags)
        time.sleep(t)
        y = split_content_by_tags(get_content(url), tags)

        z = compare_content_by_tags(x,y)
        for i in range(len(tags)):
            for elem in z[i]:
                print("BEFORE:", elem[0])
                print("AFTER:", elem[1])


if __name__ == "__main__":
    # obserwacja stronki co 15 sekund
    time_seconds = 15
    website = "http://www.mediamond.fi/"
    example_usage(website, time_seconds)
