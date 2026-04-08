import argparse
import os

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common import clean_name_for_url, create_headless_driver, get_top20_players, normalize_text


PLAYER_URL = "https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={player_slug}"
TARGET_SURFACES = {"Last 52", "Hard", "Clay", "Grass"}


def extract_stats_rows(driver):
    rows = driver.find_elements(By.XPATH, "//tr")

    header = None
    extracted = []

    for row in rows:
        cells = row.find_elements(By.XPATH, "./th|./td")
        values = [normalize_text(c.text) for c in cells]
        if not values:
            continue

        if values[0] == "TOTALS":
            header = ["surface" if v == "TOTALS" else v.lower() for v in values]
            continue

        if values[0] in TARGET_SURFACES:
            values[0] = "Overall" if values[0] == "Last 52" else values[0]
            extracted.append(values)

    if header is None:
        return pd.DataFrame()

    # Keep only rows that match header length in case the page injects extra/short rows.
    normalized_rows = [r for r in extracted if len(r) == len(header)]
    return pd.DataFrame(normalized_rows, columns=header)


def scrape_player_stats(player_name, driver=None):
    slug = clean_name_for_url(player_name)
    url = PLAYER_URL.format(player_slug=slug)
    print(f"Scraping stats from: {url}")

    owns_driver = driver is None
    if owns_driver:
        driver = create_headless_driver()

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr"))
        )
        df = extract_stats_rows(driver)
        if not df.empty:
            df["player"] = player_name
        return df
    finally:
        if owns_driver and driver is not None:
            driver.quit()


def scrape_top20_stats():
    players = get_top20_players()
    print(f"Top-20 players found: {len(players)}")

    driver = create_headless_driver()

    all_frames = []
    try:
        for player in players:
            try:
                df_player = scrape_player_stats(player, driver=driver)
                if not df_player.empty:
                    all_frames.append(df_player)
            except Exception as exc:
                print(f"Error scraping {player}: {exc}")
    finally:
        driver.quit()

    if not all_frames:
        return pd.DataFrame()

    return pd.concat(all_frames, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(description="Scrape player split stats from Tennis Abstract classic pages.")
    parser.add_argument(
        "--player",
        required=False,
        help="Single player name, e.g. 'Novak Djokovic'. Omit to scrape all top-20 players.",
    )
    parser.add_argument("--output", default=None, help="Output CSV path. Default: data/stats_raw.csv")
    args = parser.parse_args()

    if args.player:
        df = scrape_player_stats(args.player)
    else:
        df = scrape_top20_stats()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = args.output or os.path.join(base_dir, "..", "data", "stats_raw.csv")

    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to: {output_path}")


if __name__ == "__main__":
    main()
