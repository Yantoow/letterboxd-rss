"""
Author:         Yanto Christoffel
Project Title:  LetterboxdRSS
"""

import re
import html
from typing import List, Optional
import datetime
from functools import cmp_to_key


class Movie:
    def __init__(
        self,
        title=None,
        year=None,
        watched_date=None,
        rewatch=None,
        rating=None,
        poster=None,
        link=None,
    ):
        """Initializes a Movie object."""
        self.title = title
        self.year = year
        self.watched_date = watched_date
        self.rewatch = rewatch
        self.rating = rating
        self.poster = poster
        self.link = link

    def __repr__(self) -> str:
        """Handles the way a Movie object is printed."""
        if self.title:
            if self.year:
                return f"{self.title} ({self.year})"
            return f"{self.title} (?)"
        return "Unknown"


def compare_titles(movie1, movie2) -> int:
    """Compares Movie objects by their titles."""
    if movie1.title and movie2.title:
        if movie1.title < movie2.title:
            return -1
        elif movie1.title > movie2.title:
            return 1

    return 0


def compare_ratings(movie1, movie2) -> int:
    """Compares Movie objects by their ratings."""
    if movie1.rating and movie2.rating:
        if movie1.rating < movie2.rating:
            return 1
        elif movie1.rating > movie2.rating:
            return -1
        return 0

    if movie1.rating and not (movie2.rating):
        return -1

    return 1


def compare_years(movie1, movie2) -> int:
    """Compares Movie objects by their years."""
    if movie1.year and movie2.year:
        if movie1.year < movie2.year:
            return 1
        elif movie1.year > movie2.year:
            return -1

    return 0


def sort_movies(movies, sorting_key) -> List[Movie]:
    """Returns a sorted movie list according to the given sorting key."""
    return sorted(movies, key=cmp_to_key(sorting_key))


def fix_html_title(title) -> str:
    """Replaces the HTML representation of some
    symbols with the actual symbols."""
    special_char_map = {
        "\\xc3\\x81": "Á",
        "\\xc3\\x89": "É",
        "\\xc3\\x8d": "Í",
        "\\xc3\\x93": "Ó",
        "\\xc3\\x9a": "Ú",
        "\\xc3\\xa1": "á",
        "\\xc3\\xa9": "é",
        "\\xc3\\xad": "í",
        "\\xc3\\xb3": "ó",
        "\\xc3\\xba": "ú",
        "\\xc3\\x80": "À",
        "\\xc3\\x88": "È",
        "\\xc3\\x8c": "Ì",
        "\\xc3\\x92": "Ò",
        "\\xc3\\x99": "Ù",
        "\\xc3\\xa0": "à",
        "\\xc3\\xa8": "è",
        "\\xc3\\xac": "ì",
        "\\xc3\\xb2": "ò",
        "\\xc3\\xb9": "ù",
        "\\xc3\\x84": "Ä",
        "\\xc3\\x8b": "Ë",
        "\\xc3\\x8f": "Ï",
        "\\xc3\\x96": "Ö",
        "\\xc3\\x9c": "Ü",
        "\\xc3\\xa4": "ä",
        "\\xc3\\xab": "ë",
        "\\xc3\\xaf": "ï",
        "\\xc3\\xb6": "ö",
        "\\xc3\\xbc": "ü",
        "\\xc3\\xb1": "ñ",
        "\\xc3\\xa7": "ç",
        "\\xc5\\x9f": "ş",
        "\\xc5\\x9e": "Ş",
        "\\xc4\\x9f": "ğ",
        "\\xc3\\x86": "Æ",
        "\\xc2\\xa1": "¡",
        "\\xc2\\xbd": "½",
        "\\xc4\\xb1": "\u0131",
        "\\xe2\\x80\\x93": "\u2013",
        "\\xe2\\x80\\x99": "\u2019",
    }

    title = html.unescape(title)

    for key, value in special_char_map.items():
        title = title.replace(key, value)

    return title


def fix_date(watched_date) -> str:
    """Changes the format of the given date."""
    if watched_date:
        parsed = datetime.datetime.strptime(watched_date, "%Y-%m-%d")
        return parsed.strftime("%a, %d %B, %Y")

    return None


def find_element(tag, source) -> Optional[str]:
    """Returns a list of found elements according to the given tag."""
    match = re.search(f"{tag}>(.*?)</letterboxd:{tag}>", source)

    if match:
        return match.group()[len(tag) + 1 : -len(tag) - 14]
    return None


def get_movie(item_text) -> Optional[Movie]:
    """Returns a Movie object from a text."""
    if "letterboxd-list" in item_text:
        return None

    title = find_element("filmTitle", item_text)
    year = find_element("filmYear", item_text)
    watched_date = find_element("watchedDate", item_text)
    rewatch = find_element("rewatch", item_text)
    rating = find_element("memberRating", item_text)
    poster = re.findall('img src="(.*?)"/>', item_text)
    link = re.findall("<link>(.*?)</link>", item_text)

    title = fix_html_title(title)
    watched_date = fix_date(watched_date)

    return Movie(title, year, watched_date, rewatch, rating, poster, link)


def get_last_n(page_text, n) -> List[Movie]:
    """Composes a list containing the last n movies."""
    if n > 50:
        n = 50

    last_n_items = re.findall("<item>(.*?)</item>", page_text)[:n]

    return list(
        filter(None, [get_movie(item_text) for item_text in last_n_items])
    )
