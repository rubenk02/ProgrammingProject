import argparse
import os
import re

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common import clean_name_for_url, create_headless_driver, get_top20_players, normalize_text


PLAYER_URL = "https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={player_slug}"

TARGET_COLUMNS = [
	"date",
	"tournament",
	"surface",
	"source_player",
	"rd",
	"rk",
	"vrk",
	"winner",
	"loser",
	"score",
]

def normalize_date(date_text):
	return normalize_text(date_text).replace("‑", "-").replace("–", "-")


def clean_player_display(raw_name):
	name = normalize_text(raw_name)
	name = re.sub(r"\[[A-Z]{3}\]", "", name).strip()

	# Remove seeding/entry tags like (3), (Q), (WC), etc.
	while True:
		updated = re.sub(r"^\((?:\d+|Q|WC|LL|PR|ALT|SE)\)\s*", "", name)
		if updated == name:
			break
		name = updated

	return normalize_text(name)


def split_matchup(matchup_text):
	text = normalize_text(matchup_text)
	parts = re.split(r"\s+d\.\s+|\s+def\.\s+|\s+defeated\s+|\s+bt\.\s+", text, maxsplit=1)

	if len(parts) != 2:
		return None, None

	winner = clean_player_display(parts[0])
	loser = clean_player_display(parts[1])
	return winner or None, loser or None


def expand_player_name_if_short(value, player_name):
	if not value:
		return value

	full_name = clean_player_display(player_name)
	last_name = full_name.split()[-1] if full_name.split() else full_name

	if normalize_text(value).lower() == normalize_text(last_name).lower():
		return full_name

	return value


def extract_matches_rows(driver, player_name):
	rows = driver.find_elements(By.XPATH, "//table//tr")
	out = []

	for row in rows:
		tds = row.find_elements(By.TAG_NAME, "td")
		if len(tds) < 8:
			continue

		cells = [normalize_text(td.text) for td in tds]

		date = normalize_date(cells[0])
		if not re.match(r"^\d{1,2}-[A-Za-z]{3}-\d{4}$", date):
			continue

		matchup = cells[6]
		winner, loser = split_matchup(matchup)
		winner = expand_player_name_if_short(winner, player_name)
		loser = expand_player_name_if_short(loser, player_name)

		out.append(
			{
				"date": date,
				"tournament": cells[1],
				"surface": cells[2],
				"source_player": player_name,
				"rd": cells[3],
				"rk": cells[4],
				"vrk": cells[5],
				"winner": winner,
				"loser": loser,
				"score": cells[7],
			}
		)

	return out


def scrape_player_matches(player_name, driver=None):
	slug = clean_name_for_url(player_name)
	url = PLAYER_URL.format(player_slug=slug)
	print(f"Scraping matches from: {url}")

	owns_driver = driver is None
	if owns_driver:
		driver = create_headless_driver()

	try:
		driver.get(url)
		WebDriverWait(driver, 20).until(
			EC.presence_of_all_elements_located((By.XPATH, "//table//tr"))
		)
		rows = extract_matches_rows(driver, player_name)
		return pd.DataFrame(rows, columns=TARGET_COLUMNS)
	finally:
		if owns_driver and driver is not None:
			driver.quit()


def scrape_top20_matches():
	players = get_top20_players()
	print(f"Top-20 players found: {len(players)}")

	driver = create_headless_driver()

	all_frames = []
	try:
		for player in players:
			try:
				df_player = scrape_player_matches(player, driver=driver)
				all_frames.append(df_player)
			except Exception as exc:
				print(f"Error scraping {player}: {exc}")
	finally:
		driver.quit()

	if not all_frames:
		return pd.DataFrame(columns=TARGET_COLUMNS)

	return pd.concat(all_frames, ignore_index=True)


def main():
	parser = argparse.ArgumentParser(description="Scrape match history from a Tennis Abstract classic player page.")
	parser.add_argument(
		"--player",
		required=False,
		help="Single player name, e.g. 'Novak Djokovic'. Omit to scrape all top-20 players.",
	)
	parser.add_argument("--output", default=None, help="Output CSV path. Default: data/matches_raw.csv")
	args = parser.parse_args()

	if args.player:
		df = scrape_player_matches(args.player)
	else:
		df = scrape_top20_matches()

	base_dir = os.path.dirname(os.path.abspath(__file__))
	output_path = args.output or os.path.join(base_dir, "..", "data", "matches_raw.csv")

	df.to_csv(output_path, index=False)
	print(f"Saved {len(df)} rows to: {output_path}")


if __name__ == "__main__":
	main()
