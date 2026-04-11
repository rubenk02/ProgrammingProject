import pandas as pd
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import os

# Shared helper utilities used across the project
from common import clean_name_for_url, create_headless_driver, get_top20_players


# Initialize headless Selenium browser
driver = create_headless_driver()

# Columns we want in the final output CSV, in this order
TARGET_COLUMNS = [
    "name", "age", "current_rank"
]


def _extract_field(text, label):    
    """
    Extract the value following a given label from a block of text.
    Uses a regex that:
    - Matches 'label: <value>'
    - Stops when it encounters another known profile label or end of text
    """
    pattern = (
        rf"{label}:\s*(.*?)"
        r"(?=Age:|Plays:|Current rank:|Peak rank:|Elo rank:|Profile:|Titles/Finals|Photo:|$)"
    )
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    # Normalize whitespace in the extracted value
    return " ".join(m.group(1).split()).strip()


def _age_only(age_text):   
    """
    Extract only the numeric age from a string (e.g. '27 years, 3 months' → '27')
    """
    if not age_text:
        return None
    m = re.search(r"\d+", age_text)
    return m.group(0) if m else None


def scrape_player_profile(name):   
    """
    Scrape age and current ranking for a single player from Tennis Abstract.
    Returns a dict with:
    - name
    - age (string or None)
    - current_rank (string or None)
    """
    clean = clean_name_for_url(name)
    url = f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={clean}"

    print("\n=== SCRAPING PLAYER ===")
    print("URL:", url)
    
    # Load the player profile page
    driver.get(url)
    
    # Small delay to allow dynamic elements to start loading
    time.sleep(1)
    
    # Try to switch to the "Bio" tab if it exists
    try:
        bio_tab = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Bio")]'))
        )
        bio_tab.click()
    except:
        # Not all profiles require clicking the Bio tab
        pass
    # Wait for the biography section to be present
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//p[@id="biog"]'))
        )
    except:
        #  If bio data is unavailable, return empty fields for this player
        return {
            "name": name,
            "age": None,
            "current_rank": None,
        }
    # Initialize output structure for this player
    info = {
        "name": name,
        "age": None,
        "current_rank": None,
    }
    # Attempt to extract structured data from the bio table
    rows = driver.find_elements(By.XPATH, '//p[@id="biog"]//table//tr')
    for r in rows:
        tds = r.find_elements(By.TAG_NAME, "td")
        if len(tds) < 2:
            continue

        raw_key = tds[0].text.strip().lower().replace(":", "")
        raw_val = " ".join(tds[1].text.split()).strip()

        if not raw_val:
            continue
        # Match known fields from the table
        if raw_key == "age":
            info["age"] = _age_only(raw_val)
        elif raw_key == "current rank":
            info["current_rank"] = raw_val
    # Extract data from unstructured biography text
    biog_text = driver.find_element(By.XPATH, '//p[@id="biog"]').text
    biog_text = " ".join(biog_text.split())

    if not info["age"]:
        info["age"] = _age_only(_extract_field(biog_text, "Age"))
    if not info["current_rank"]:
        info["current_rank"] = _extract_field(biog_text, "Current rank")

    return info


def main():   
    """
    Main workflow:
    - Fetch current top 20 ATP players
    - Scrape profile info for each
    - Save results as a CSV file
    """
    players = get_top20_players()
    print("Players found:", players)
    all_rows = []

    for p in players:
        try:
            all_rows.append(scrape_player_profile(p))
        except Exception as e:
            print("Error with player", p, e)
    # Create DataFrame and keep only desired columns
    df = pd.DataFrame(all_rows)
    df = df[TARGET_COLUMNS]

    # Convert age to nullable integer type
    df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")
    # Save CSV relative to the project structure
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", "top20_players_raw.csv")
    df.to_csv(data_path, index=False)


if __name__ == '__main__':
    main()
# Clean up Selenium browser at the end of execution
driver.quit()