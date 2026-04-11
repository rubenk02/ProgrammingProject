import re
import unicodedata

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# URL that hosts ATP ranking
RANKING_URL = "https://www.tennisabstract.com/jsmatches/leadersource.js"

# Headers used to mimic a real browser and avoid request blocking
HEADERS = {"User-Agent": "Mozilla/5.0"}

def normalize_text(value):    
    """
    Normalize text by:
    - Handling None values safely
    - Replacing non-breaking spaces
    - Collapsing multiple spaces into one
    - Stripping leading/trailing whitespace
    """
    if value is None:
        return ""
    return " ".join(str(value).replace("\xa0", " ").split()).strip()


def clean_name_for_url(name): 
    """
    Convert a player's name into a URL-safe, ASCII-only string. Steps:
    - Normalize text
    - Remove spaces and hyphens
    - Convert accented characters to ASCII equivalents
    - Remove any remaining non-alphanumeric characters
    """
    compact = normalize_text(name).replace(" ", "").replace("-", "")
    ascii_name = unicodedata.normalize("NFKD", compact).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]", "", ascii_name)

def get_top20_players():    
    """
    Fetch the current ATP ranking data from Tennis Abstract
    and return a list with the names of the top 20 players.
    """
    response = requests.get(
        RANKING_URL,
        headers=HEADERS, timeout=20
    )
    response.raise_for_status()
    # Extract the JavaScript object containing player rankings
    match = re.search(r"crank\s*=\s*\{(.*?)\};", response.text)
    
    # Extract player names and ranking values
    pairs = re.findall(r"'([^']+)':\s*(\d+)", match.group(1))
    
    # Sort players by ascending rank number
    sorted_players = sorted(pairs, key=lambda x: int(x[1]))
    
    # Return only the top 20 player names
    return [name for name, _ in sorted_players[:20]]


def create_headless_driver():    
    """
    Create and return a headless Chrome WebDriver instance,
    which runs without opening a visible browser window.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)
