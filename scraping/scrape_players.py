import pandas as pd
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import os

from common import clean_name_for_url, create_headless_driver, get_top20_players


# Initialize headless browser
driver = create_headless_driver()


TARGET_COLUMNS = [
    "name", "age", "current_rank"
]

def _extract_field(text, label):
    pattern = (
        rf"{label}:\s*(.*?)"
        r"(?=Age:|Plays:|Current rank:|Peak rank:|Elo rank:|Profile:|Titles/Finals|Photo:|$)"
    )
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    return " ".join(m.group(1).split()).strip()

def _age_only(age_text):
    if not age_text:
        return None
    m = re.search(r"\d+", age_text)
    return m.group(0) if m else None

def scrape_player_profile(name):
    clean = clean_name_for_url(name)
    url = f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={clean}"

    print("\n=== SCRAPING PLAYER ===")
    print("URL:", url)

    driver.get(url)
    time.sleep(1)

    try:
        bio_tab = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Bio")]'))
        )
        bio_tab.click()
    except:
        pass

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//p[@id="biog"]'))
        )
    except:
        return {
            "name": name,
            "age": None,
            "current_rank": None,
        }

    info = {
        "name": name,
        "age": None,
        "current_rank": None,
    }

    rows = driver.find_elements(By.XPATH, '//p[@id="biog"]//table//tr')
    for r in rows:
        tds = r.find_elements(By.TAG_NAME, "td")
        if len(tds) < 2:
            continue

        raw_key = tds[0].text.strip().lower().replace(":", "")
        raw_val = " ".join(tds[1].text.split()).strip()

        if not raw_val:
            continue

        if raw_key == "age":
            info["age"] = _age_only(raw_val)
        elif raw_key == "current rank":
            info["current_rank"] = raw_val

    biog_text = driver.find_element(By.XPATH, '//p[@id="biog"]').text
    biog_text = " ".join(biog_text.split())

    if not info["age"]:
        info["age"] = _age_only(_extract_field(biog_text, "Age"))
    if not info["current_rank"]:
        info["current_rank"] = _extract_field(biog_text, "Current rank")

    return info

def main():
    players = get_top20_players()
    print("Players found:", players)
    all_rows = []

    for p in players:
        try:
            all_rows.append(scrape_player_profile(p))
        except Exception as e:
            print("Error with player", p, e)

    df = pd.DataFrame(all_rows)
    df = df[TARGET_COLUMNS]

    df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", "top20_players_raw.csv")
    df.to_csv(data_path, index=False)

if __name__ == '__main__':
    main()

driver.quit()