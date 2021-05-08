import sqlite3

from mtgmelee.bulk_scryfall_fetcher import BulkSkryfallFetcher

DB_NAME = 'mtgmelee.db'
DECKS_TABLE = 'decks'
CARDS_TABLE = 'cards'
PLAYERS_TABLE = 'players'
SCRYFALL_CARD_TABLE = 'scryfall_cards'

def is_color(*, color_list, color):
    return color in color_list

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
        type_line STRING,
        color_w BOOL,
        color_u BOOL,
        color_b BOOL,
        color_r BOOL,
        color_g BOOL
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

    interval = 100
    start_ix = 0
    end_ix = interval
    while start_ix < len(card_names):
        print(f'Progress: {start_ix} out of {len(card_names)} cards')
        current_batch = card_names[start_ix:end_ix]
        fetcher = BulkSkryfallFetcher(current_batch)
        scryfall_cards = fetcher.fetch_all()

        for card in scryfall_cards:
            try:
                mana_cost = card.mana_cost()
            except:
                mana_cost = None
            
            try:
                cmc = int(card.cmc())
            except:
                cmc = None

            try:
                colors = card.colors()
            except:
                colors = []

            cur.execute(f"""
            REPLACE INTO {SCRYFALL_CARD_TABLE} (id, name, mana_cost, cmc, type_line, color_w, color_u, color_b, color_r, color_g)
            VALUES (:id, :name, :mana_cost, :cmc, :type_line, :color_w, :color_u, :color_b, :color_r, :color_g);
            """,
            {
                "id": card.id(),
                "name": card.name(),
                "mana_cost": mana_cost,
                "cmc": cmc,
                "type_line": card.type_line(),
                "color_w": is_color(color_list=colors, color='W'),
                "color_u": is_color(color_list=colors, color='U'),
                "color_b": is_color(color_list=colors, color='B'),
                "color_r": is_color(color_list=colors, color='R'),
                "color_g": is_color(color_list=colors, color='G')
            })

        conn.commit()
        
        start_ix = end_ix
        end_ix += interval

    cur.close(),
    conn.commit()
    conn.close()
