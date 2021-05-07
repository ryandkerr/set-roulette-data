import os
import sys

from bs4 import BeautifulSoup
from mtgmelee.parsers import DecklistParser
from mtgmelee.deck_to_db_writer import DeckToDBWriter

DB_NAME = 'mtgmelee.db'
DECKS_TABLE = 'decks'
CARDS_TABLE = 'cards'
PLAYERS_TABLE = 'players'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise StandardError('Usage: python3 parse_decklists_to_db.py <PATH_TO_DECKLIST_DIR>')

    decklist_dir = sys.argv[1]
    
    for decklist_file in os.listdir(decklist_dir):
        print(f'Parsing and writing {decklist_file}')
        with open(f'{decklist_dir}/{decklist_file}') as f:
            html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            parser = DecklistParser(soup)
            deck = parser.parse()

            db_writer = DeckToDBWriter(deck=deck,
                                       db_name=DB_NAME,
                                       decks_table=DECKS_TABLE,
                                       cards_table=CARDS_TABLE,
                                       players_table=PLAYERS_TABLE)
            db_writer.write_to_db()
