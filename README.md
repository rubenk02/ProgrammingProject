# ATP Tennis Data Analysis

## Project Goal
This project analyzes ATP tennis data to answer three research questions:

1. How important is ranking for match outcomes?
2. Do players perform differently depending on the surface?
3. Which player characteristics are associated with winning matches?

## Research Questions

### 1. Ranking and Match Outcomes
- Do higher-ranked players consistently win?
- How often do lower-ranked players (upsets) win?

### 2. Surface-Specific Performance
- Are some players significantly better on clay, grass, or hard courts?
- How do surface-specific stats differ from overall performance?

### 3. Player Characteristics and Success
- Do better serve stats correlate with higher win rates?
- Can we identify patterns between player stats and success?

## Data Collection Completed
Data is scraped from Tennis Abstract using scripts in `scraping/`.

### 1. Player Profiles
- Script: `scraping/scrape_players.py`
- Output: `data/top20_players_raw.csv`
- Fields currently collected:
	- `name`
	- `age`
	- `current_rank`

### 2. Match History
- Script: `scraping/scrape_matches.py`
- Output: `data/matches_raw.csv`
- Fields collected:
	- `date`, `tournament`, `surface`, `source_player`, `rd`, `rk`, `vrk`, `winner`, `loser`, `score`

### 3. Player Surface/Overall Stats
- Script: `scraping/scrape_stats.py`
- Output: `data/stats_raw.csv`
- Only selected rows are kept:
	- `Overall` (Last 52 weeks)
	- `Hard`
	- `Clay`
	- `Grass`

### Shared Scraping Utilities
- Module: `scraping/common.py`
- Shared logic includes:
	- top-player list retrieval
	- player URL name normalization
	- headless driver creation

## Cleaning and Processing Completed

### 1. Match Cleaning
- Script: `processing/clean_matches.py`
- Output: `data/matches_clean.csv`
- Implemented transformations:
	- `rd` renamed to `Round`
	- `winner_rank_at_match` and `loser_rank_at_match` created
	- rank mapping is done using `source_player` perspective
	- analysis-friendly final column order

### 2. Stats Cleaning
- Script: `processing/clean_stats.py`
- Output: `data/stats_clean.csv`
- Implemented transformations:
	- readable column names
	- requested naming:
		- `match_record_last52weeks`
		- `tiebreak_record_last52weeks`
	- `player` moved to the first column

## Current Pipeline (Reproducible Run Order)
Run from project root:

1. `python ./scraping/scrape_players.py`
2. `python ./scraping/scrape_matches.py`
3. `python ./scraping/scrape_stats.py`
4. `python ./processing/clean_matches.py`
5. `python ./processing/clean_stats.py`

## Important Note for Final Runs
For faster testing, top-player retrieval in `scraping/common.py` may be temporarily reduced (for example to 5 players).
Before final analysis and report results, restore this to the full intended scope.

## What Still Needs To Be Done

### A. Final Data Scope and Refresh
1. Ensure full target player scope is enabled in `scraping/common.py`.
2. Re-run the full pipeline to regenerate all raw and cleaned datasets.

### B. Data Quality and Validation
1. Confirm duplicate policy for matches in `matches_clean.csv`.
2. Inspect unresolved rank mappings and document handling.
3. Validate data types for ranks, dates, and percentages.

### C. Analytical Dataset Construction
1. Build a match-level analysis table combining:
	 - cleaned matches
	 - player profile information
	 - cleaned surface/overall stats
2. Engineer core features such as:
	 - rank difference at match time
	 - upset indicator
	 - surface-specific performance gaps

### D. Statistical Analysis to Answer Research Questions
1. Ranking impact:
	 - win rate by rank-difference bins
	 - upset frequency analysis
	 - baseline logistic model for match outcome
2. Surface impact:
	 - per-player win rates by surface
	 - comparison of overall vs surface-specific stats
3. Player-characteristic impact:
	 - correlation and multivariate analysis between serve/return metrics and success

### E. Final Reporting
1. Methods section (scraping + cleaning + modeling pipeline)
2. Results section (figures/tables per research question)
3. Discussion of limitations and assumptions
4. Reproducibility section with exact run commands
