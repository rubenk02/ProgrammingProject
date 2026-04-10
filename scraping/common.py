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
    response = requests.get(
        "https://www.tennisabstract.com/jsmatches/leadersource.js",
        headers=HEADERS, timeout=20
    )
    response.raise_for_status()

    match = re.search(r"crank\s*=\s*\{(.*?)\};", response.text)
    pairs = re.findall(r"'([^']+)':\s*(\d+)", match.group(1))
    sorted_players = sorted(pairs, key=lambda x: int(x[1]))
    return [name for name, _ in sorted_players[:20]]


def create_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)
