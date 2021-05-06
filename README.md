# set-roulette-data
This project scrapes and analyzes data from [MTGMelee](http://mtgmelee.com)
tournaments.

## Tournament Results Scraper
This scrapes the HTML of the provided tournament results page and saves the raw
files to `./data/raw/<TOURNAMENT_ID>/standings`. Then save the html files of all decklists
in the tournament to `./data/raw/<TOURNAMENT_ID>/decklists`

Usage:
```
python3 scrape_tournament.py <TOURNAMENT_URL>
```

## Parse & Save Decklists to DB
This script parses a directory of downloaded decklist pages and writes the data
to the `mtgmelee.db` sqlite3 database.

Usage:
```
python3 parse_decklists_to_db.py <PATH_TO_DECKLIST_DIR>
```
<br><br>

# Dev Setup
Download [Chromedriver](https://chromedriver.chromium.org/downloads), name the
file `chromedriver`, and move it to this directory.

### Env setup: Conda
If you use Conda, create a conda environment with the required packages and
python version:
```
conda env create -f environment.yml
```

If you have already created this environment, activate it
```
conda activate set-roulette-data
```
