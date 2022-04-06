# Set Roulette Data
This project scrapes and analyzes data from [MTGMelee](http://mtgmelee.com)
tournaments.

Before running any of the below scripts, activate your conda environment (see devsetup for instructions).
## Scrape Tournament Standings
This script scrapes the HTML of the provided tournament results page and saves the raw
files to `./data/raw/<TOURNAMENT_ID>/standings`. It then saves the html files of all decklists
in the tournament to `./data/raw/<TOURNAMENT_ID>/decklists`

Usage:
```
python3 scrape_tournament.py <TOURNAMENT_URL> [<TOURNAMENT_URL> ...]
```

## Parse & Save Decklists to DB
This script parses a directory of downloaded decklist pages and writes the data
(decks, players, cards, and results) to the `mtgmelee.db` sqlite3 database.

Usage:
```
python3 parse_decklists_to_db.py <PATH/TO/DECKLIST/DIR> [<PATH/TO/DECKLIST/DIR> ...]
```

## Parse & Save Results to DB (not yet implemented)
This script parses a directory of downloaded tournament results pages and writes
the results to the `mtgmelee.db` sqlite3 database.

Usage:
```
python3 parse_results_to_db.py <PATH/TO/RESULTS/DIR> [<PATH/TO/RESULTS/DIR> ...]
```

## Populate Scryfall DB
This script populates the scryfall card table with cards that are in the current
tournament results card table. It will only hit scryfall for cards that are
not currently in the scryfall database.

Usage:
```
python3 populate_scyfall_db.py
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


Then download the packages that aren't available with conda:
```
pip install -r requirements.txt
```

# Future Projects
- Round-by-round results scraper
- Player ELO
- Host website with interactive data visualizations and articles
