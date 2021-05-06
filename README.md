# set-roulette-data
This project scrapes and analyzes data from [MTGMelee](http://mtgmelee.com)
tournaments.

## Tournament Results Scraper
This scrapes the HTML of the provided tournament results page and saves the raw
files to `./data/raw/<tournament_id>/`.

Usage:
```
python3 selenium_testing.py <TOURNAMENT_URL>
```

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
