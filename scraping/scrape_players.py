import requests
from lxml import html
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import os


# Initialize headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

HEADERS = {"User-Agent": "Mozilla/5.0"}
RANKING_URL = "https://www.tennisabstract.com/reports/atp_elo_ratings.html"


def normalize(name):
    return name.replace("\xa0", " ").strip()

def get_top20_players():
    response = requests.get(RANKING_URL, headers=HEADERS)
    tree = html.fromstring(response.content)
    rows = tree.xpath('//table[contains(@class, "tablesorter")]/tbody/tr')
    players = []
    for r in rows[:20]:
        name = r.xpath('.//td[2]/a/text()')
        if name:
            players.append(normalize(name[0]))
    print("Players found:", players)
    return players

def clean_name_for_url(name):
    # Remove accents and special characters so it matches the site url format
    clean = (
        name.replace("\xa0", " ")
            .replace(" ", "")
            .replace("-", "")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("Á", "A")
            .replace("É", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ú", "U")
    )
    return clean


def scrape_player_profile(name):
    clean = clean_name_for_url(name)
    url = f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={clean}"

    print("\n=== SCRAPING PLAYER ===")
    print("URL:", url)

    driver.get(url)
    time.sleep(1)

    # Scroll to the bio area to trigger JS loading
    driver.execute_script("window.scrollTo(0, 300);")
    time.sleep(1)

    # Try clicking Bio tab (some players need it)
    try:
        bio_tab = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH,'//span[contains(text(), "Bio")]'))
        )
        bio_tab.click()
        time.sleep(1)
    except:
        pass

    # Wait up to 5 seconds for <p id="biog"> to appear
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH,'//p[@id="biog"]'))
        )
    except:
        print("BIO not found even after waiting")
        return {"name": name}

    # Now extract rows
    rows = driver.find_elements(By.XPATH, '//p[@id="biog"]//table//tr')
    print("Found bio rows:", len(rows))

    info = {"name": name}

    for r in rows:
        text = r.text.strip()
        
        # Skip empty or weird header lines
        if not text or "@" in text and "age" not in text.lower():
            continue
        
        # Split on the first ":" only
        if ":" in text:
            key, val = text.split(":", 1)
            key = key.strip().capitalize() # makes "Age", "Plays", "Current rank"
            val = val.strip()

        # Remove "Photo:" and "Titles/Finals" noise
        if key.lower() in ["photo", "titles/finals"]:
            continue

        info[key] = val
        print("Extracted:", key, "=", val.strip())

    return info

def main():
    players = get_top20_players()
    all_rows = []
    for p in players:
        try:
            rows = scrape_player_profile(p)
            all_rows.append(rows)
        except Exception as e:
            print("Error with player", p, e)
        time.sleep(1)

    df = pd.DataFrame(all_rows)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", "players_profiles.csv")

    df.to_csv(data_path, index=False)
    print("Saved", data_path)

if __name__ == '__main__':
    main()

driver.quit()