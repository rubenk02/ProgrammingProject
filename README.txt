FINAL PROJECT - TENNIS DATA PIPELINE AND ANALYSIS

1) GROUP MEMBERS
- Student 1: Mara Gasperetti
- Student 2: Ruben Krieger
- Student 3: Amine Hafaidhia

2) PROJECT OVERVIEW
This project collects ATP Top-20 player data, cleans it, and analyzes three research questions:
- Q1: How important is ranking for match outcomes?
- Q2: Do players perform differently depending on surface?
- Q3: Which player characteristics are associated with winning?

3) PROJECT STRUCTURE
- scraping/
	- common.py: shared scraping utilities (driver setup, name normalization, top-player retrieval)
	- scrape_players.py: scrapes player profile data
	- scrape_matches.py: scrapes match history
	- scrape_stats.py: scrapes player stats by surface and overall
- processing/
	- clean_matches.py: cleans and standardizes raw match data
	- clean_stats.py: cleans and standardizes raw stats data
- data/
	- top20_players.csv: player profiles
	- matches_raw.csv: raw matches
	- stats_raw.csv: raw player stats
	- matches_clean.csv: cleaned matches for analysis
	- stats_clean.csv: cleaned stats for analysis
- plots/: generated figures
- analysis.ipynb: notebook with data-quality checks, Q1-Q3 analysis, and figures
- presentation.pdf: slides used for the final presentation, summarizing the project
- Video.mp4: recorded video presentation (≈8 minutes)

4) REQUIREMENTS
Python version:
- Python 3.10+ recommended

Python packages:
- pandas
- numpy
- matplotlib
- requests
- lxml
- selenium
- webdriver-manager

Install all dependencies with:
pip install pandas numpy matplotlib requests lxml selenium webdriver-manager

System/software requirements:
- Google Chrome installed (required by Selenium Chrome driver)
- Internet connection for scraping

5) HOW TO RUN THE PROJECT
Run commands from the project root folder.

Step A - Data scraping:
python scraping/scrape_players.py
python scraping/scrape_matches.py
python scraping/scrape_stats.py

Step B - Data cleaning:
python processing/clean_matches.py
python processing/clean_stats.py

Step C - Analysis:
- Open analysis.ipynb and run all cells in order.
- Generated charts are saved in plots/.

6) OUTPUTS
Main final files:
- data/matches_clean.csv
- data/stats_clean.csv
- plots/*.png

7) NOTES AND ASSUMPTIONS
- Some missing values are expected and intentional (for example, when a player has no matches on a surface).
- Duplicated match rows can appear in raw scraped data (same match from both player perspectives) and are handled in cleaning.
- Notebook findings are based on the available scraped period and sample.

8) VIDEO PRESENTATION LINK
- Final project video: https://upm365-my.sharepoint.com/:v:/g/personal/ma_gasperetti_alumnos_upm_es/IQAle6bNwpZxTKYmnq_3bJcXAajLpXCpylyGNccafomE0tQ?e=big6vX

9) QUICK TROUBLESHOOTING
- If Selenium fails to start, check Chrome installation/version and reinstall webdriver-manager.
- If imports fail, reinstall dependencies in the active environment.
- If files are not found, make sure commands are executed from the project root.