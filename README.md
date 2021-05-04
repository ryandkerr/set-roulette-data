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
