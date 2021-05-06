import os
import pdb
import sqlite3
import sys

from bs4 import BeautifulSoup
from mtgmelee.parsers import DecklistParser

DB_NAME = 'mtgmelee.db'
DECKS_TABLE = 'decks'
CARDS_TABLE = 'cards'
PLAYERS_TABLE = 'players'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise StandardError('Usage: python3 parse_decklists_to_db.py <PATH_TO_DECKLIST_DIR>')

    decklist_dir = sys.argv[1]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(f"""
    DROP TABLE IF EXISTS {DECKS_TABLE};
    """)
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {DECKS_TABLE} (
        id INT PRIMARY KEY,
        url STRING,
        title STRING,
        player_id STRING,
        tournament_id INT
    ) WITHOUT ROWID;
    """)

    cur.execute(f"""
    DROP TABLE IF EXISTS {CARDS_TABLE};
    """)
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {CARDS_TABLE} (
        deck_id INT,
        name STRING,
        quantity STRING,
        is_sideboard BOOL
    );
    """)

    cur.execute(f"""
    DROP TABLE IF EXISTS {PLAYERS_TABLE};
    """)
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {PLAYERS_TABLE} (
        id STRING PRIMARY KEY,
        url STRING,
        name STRING
    ) WITHOUT ROWID;
    """)
    
    for decklist_file in os.listdir(decklist_dir):
        print(f'Parsing and writing {decklist_file}')
        with open(f'{decklist_dir}/{decklist_file}') as f:
            html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            parser = DecklistParser(soup)
            deck = parser.parse()

            cur.execute(f"""
            INSERT INTO {DECKS_TABLE} (id, url, title, player_id, tournament_id)
            VALUES (:id, :url, :title, :player_id, :tournament_id);
            """,
            {
                "id": deck.id,
                "url": deck.url,
                "title": deck.title,
                "player_id": deck.player.id,
                "tournament_id": deck.tournament_id
            })

            cur.execute(f"""
            INSERT INTO {PLAYERS_TABLE} (id, url, name)
            VALUES (:id, :url, :name);
            """,
            {
                "id": deck.player.id,
                "url": deck.player.url,
                "name": deck.player.name
            })

            for card in deck.main_deck:
                cur.execute(f"""
                INSERT INTO {CARDS_TABLE} (deck_id, name, quantity, is_sideboard)
                VALUES (:deck_id, :name, :quantity, :is_sideboard);
                """,
                {
                    "deck_id": deck.id,
                    "name": card.name,
                    "quantity": card.quantity,
                    "is_sideboard": False
                })

            for card in deck.sideboard:
                cur.execute(f"""
                INSERT INTO {CARDS_TABLE} (deck_id, name, quantity, is_sideboard)
                VALUES (:deck_id, :name, :quantity, :is_sideboard);
                """,
                {
                    "deck_id": deck.id,
                    "name": card.name,
                    "quantity": card.quantity,
                    "is_sideboard": True
                })

    cur.close()
    conn.commit()
    conn.close()
