import os
import sys

from bs4 import BeautifulSoup
from mtgmelee.parsers import TournamentParser
from mtgmelee.results_to_db_writer import ResultsToDBWriter

DB_NAME = 'mtgmelee.db'
DECKS_TABLE = 'decks'
CARDS_TABLE = 'cards'
PLAYERS_TABLE = 'players'
RESULTS_TABLE = 'results'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('Usage: python3 parse_results_to_db.py <PATH/TO/RESULTS/DIR> [<PATH/TO/RESULTS/DIR>...]')

    for results_dir in sys.argv[1:]:
        for results_file in os.listdir(results_dir):
            print(f'Parsing and writing {results_file}')
            with open(f'{results_dir}/{results_file}') as f:
                html = f.read()
                soup = BeautifulSoup(html, 'html.parser')
                parser = TournamentParser(soup)

                results = parser.parse_results()
                results_writer = ResultsToDBWriter(results=results,
                                                db_name=DB_NAME,
                                                results_table=RESULTS_TABLE)
                results_writer.write_to_db()
