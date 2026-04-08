import re
import unicodedata

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


RANKING_URL = "https://www.tennisabstract.com/reports/atp_elo_ratings.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def normalize_text(value):
    if value is None:
        return ""
    return " ".join(str(value).replace("\xa0", " ").split()).strip()


def clean_name_for_url(name):
    compact = normalize_text(name).replace(" ", "").replace("-", "")
    ascii_name = unicodedata.normalize("NFKD", compact).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]", "", ascii_name)


def get_top20_players():
    response = requests.get(RANKING_URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    tree = html.fromstring(response.content)
    rows = tree.xpath('//table[contains(@class, "tablesorter")]/tbody/tr')

    players = []
    for row in rows[:20]:
        name = row.xpath('.//td[2]/a/text()')
        if name:
            players.append(normalize_text(name[0]))

    return players


def create_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)
