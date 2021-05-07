import sqlite3

from mtgmelee.bulk_scryfall_fetcher import BulkSkryfallFetcher

DB_NAME = 'mtgmelee.db'
DECKS_TABLE = 'decks'
CARDS_TABLE = 'cards'
PLAYERS_TABLE = 'players'
SCRYFALL_CARD_TABLE = 'scryfall_cards'

if __name__ == '__main__':
    # get list of unique card names from cards db
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {SCRYFALL_CARD_TABLE} (
        id STRING PRIMARY KEY,
        name STRING,
        mana_cost STRING,
        cmc INT,
        type_line STRING
    );
    """)

    cur.execute(f"""
    SELECT
        distinct c.name 
    FROM {CARDS_TABLE} c
    LEFT JOIN {SCRYFALL_CARD_TABLE} s
        ON LOWER(c.name) = LOWER(s.name)
    WHERE
        s.name IS NULL;
    """)
    results = cur.fetchall()
    card_names = [row[0] for row in results]

    fetcher = BulkSkryfallFetcher(card_names[:10])
    scryfall_cards = fetcher.fetch_all()

    for card in scryfall_cards:
        cur.execute(f"""
        REPLACE INTO {SCRYFALL_CARD_TABLE} (id, name, mana_cost, cmc, type_line)
        VALUES (:id, :name, :mana_cost, :cmc, :type_line);
        """,
        {
            "id": card.id(),
            "name": card.name(),
            "mana_cost": card.mana_cost(),
            "cmc": int(card.cmc()),
            "type_line": card.type_line()
        })

    cur.close(),
    conn.commit()
    conn.close()

    # fetch all scryfall objects

    # write those objects to scryfall db