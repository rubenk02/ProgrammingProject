import requests
from lxml import html
import pandas as pd
import time
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------------------------------------------------
# SELENIUM SETUP
# -----------------------------------------------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -----------------------------------------------------------------------
# IMPORT PLAYER LIST FUNCTION FROM scrape_players.py
# -----------------------------------------------------------------------
from scrape_players import get_top20_players, clean_name_for_url


# -----------------------------------------------------------------------
# CLEAN TOURNAMENT NAME → URL SLUG (AUTOMATIC VERSION)
# -----------------------------------------------------------------------
def tournament_slug(name: str, year: int):
    """
    Convert tournament name into the 'current' TennisAbstract HTML format.
    Example:
        "Miami Masters" → "2026ATPMiamiMasters.html"
    """
    clean = name

    # remove accents
    accents = {
        "á": "a","é": "e","í": "i","ó": "o","ú": "u",
        "Á": "A","É": "E","Í": "I","Ó": "O","Ú": "U"
    }
    for a,b in accents.items():
        clean = clean.replace(a,b)

    # remove special punctuation
    clean = re.sub(r"[^A-Za-z0-9 ]", "", clean)

    # remove spaces
    clean = clean.replace(" ", "")

    # final slug format
    return f"{year}ATP{clean}.html"


# -----------------------------------------------------------------------
# SCRAPE TOURNAMENT LIST FROM PLAYER PAGE (2020–2026)
# -----------------------------------------------------------------------
def scrape_player_tournaments(player):
    clean = clean_name_for_url(player)
    url = f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={clean}"

    print(f"\n=== SCRAPING TOURNAMENTS FOR {player} ===")
    driver.get(url)
    time.sleep(1)

    # ✅ Correct XPath
    lines = driver.find_elements(By.XPATH, "//div[@id='seasons']/p")

    results = []

    for line in lines:
        text = line.text.strip()
        if not text:
            continue

        # Format: "2024: Miami Masters: R64, R32, R16"
        if ":" not in text:
            continue

        # extract year
        year_match = re.match(r"(\d{4}):", text)
        if not year_match:
            continue

        year = int(year_match.group(1))
        if year < 2020 or year > 2026:
            continue

        # remove "2024:"
        rest = text.split(":", 1)[1].strip()

        if ":" not in rest:
            continue

        tournament, rounds_text = rest.split(":", 1)
        tournament = tournament.strip()

        # ✅ filter OUT Challengers
        if "CH" in tournament or "Challenger" in tournament:
            continue

        rounds = [r.strip() for r in rounds_text.split(",") if r.strip()]

        results.append({
            "player": player,
            "year": year,
            "tournament": tournament,
            "rounds": rounds
        })

    return results


# -----------------------------------------------------------------------
# SCRAPE MATCHES FROM A TOURNAMENT PAGE
# -----------------------------------------------------------------------
def scrape_tournament_matches(year, tournament_name):
    """
    Builds the tournament URL automatically and scrapes matches.
    Returns list of match records.
    """

    slug = tournament_slug(tournament_name, year)
    url = f"https://www.tennisabstract.com/current/{slug}"

    print(f"\n--- SCRAPING TOURNAMENT PAGE ---")
    print(url)

    driver.get(url)
    time.sleep(1)

    matches = []
    rows = driver.find_elements(By.XPATH, "//table//tr")

    for r in rows:
        cells = r.find_elements(By.TAG_NAME, "td")
        if len(cells) < 6:
            continue

        rnd = cells[3].text.strip()
        match_text = cells[6].text.strip()
        score = cells[5].text.strip() if len(cells) > 5 else ""

        # parse winner/player names
        # Example: "**Sinner** d. Alcaraz"
        winner = None
        p1 = None
        p2 = None

        if " d. " in match_text:
            left, right = match_text.split(" d. ")
            left = left.replace("*","").strip()
            right = right.replace("*","").strip()
            p1 = left
            p2 = right
            winner = p1

        matches.append({
            "year": year,
            "tournament": tournament_name,
            "round": rnd,
            "player1": p1,
            "player2": p2,
            "winner": winner,
            "score": score,
            "url": url
        })

    return matches


# -----------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------
def main():
    players = get_top20_players()

    # STEP 2 — scrape tournaments from players
    all_player_tours = []
    for p in players:
        try:
            t = scrape_player_tournaments(p)
            all_player_tours.extend(t)
        except Exception as e:
            print("ERROR scraping", p, e)
        time.sleep(1)

    df_raw = pd.DataFrame(all_player_tours)
    print("\nRaw player tournaments:", len(df_raw))

    # STEP 3 — dedupe tournaments
    df_unique = df_raw[["year","tournament"]].drop_duplicates()
    print("Unique tournaments:", len(df_unique))

    # save tournaments_2020_2026.csv
    base = os.path.dirname(os.path.abspath(__file__))
    data_path_t = os.path.join(base, "..", "data", "tournaments_2020_2026.csv")
    df_unique.to_csv(data_path_t, index=False)
    print("\nSaved tournaments:", data_path_t)

    # STEP 4 — scrape matches from each unique tournament
    all_matches = []
    for _, row in df_unique.iterrows():
        year = int(row["year"])
        tname = row["tournament"]
        try:
            m = scrape_tournament_matches(year, tname)
            all_matches.extend(m)
        except Exception as e:
            print("ERROR scraping tournament:", year, tname, e)
        time.sleep(1)

    df_matches = pd.DataFrame(all_matches)

    # save matches_2020_2026.csv
    data_path_m = os.path.join(base, "..", "data", "matches_2020_2026.csv")
    df_matches.to_csv(data_path_m, index=False)
    print("Saved matches:", data_path_m)


# -----------------------------------------------------------------------
# RUN
# -----------------------------------------------------------------------
if __name__ == "__main__":
    main()
    driver.quit()
