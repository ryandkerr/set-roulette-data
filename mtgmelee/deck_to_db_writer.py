import sqlite3

class DeckToDBWriter(object):
    def __init__(self, *, deck, db_name, decks_table, cards_table, players_table):
        self.deck = deck
        self.db_name = db_name
        self.decks_table = decks_table
        self.cards_table = cards_table
        self.players_table = players_table
        
    def write_to_db(self):
        self._create_tables()
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute(f"""
        REPLACE INTO {self.decks_table} (id, url, title, player_id, tournament_id)
        VALUES (:id, :url, :title, :player_id, :tournament_id);
        """,
        {
            "id": self.deck.id,
            "url": self.deck.url,
            "title": self.deck.title,
            "player_id": self.deck.player.id,
            "tournament_id": self.deck.tournament_id
        })

        cur.execute(f"""
        REPLACE INTO {self.players_table} (id, url, name)
        VALUES (:id, :url, :name);
        """,
        {
            "id": self.deck.player.id,
            "url": self.deck.player.url,
            "name": self.deck.player.name
        })

        for card in self.deck.main_deck:
            cur.execute(f"""
            REPLACE INTO {self.cards_table} (deck_id, name, quantity, is_sideboard)
            VALUES (:deck_id, :name, :quantity, :is_sideboard);
            """,
            {
                "deck_id": self.deck.id,
                "name": card.name,
                "quantity": card.quantity,
                "is_sideboard": False
            })

        for card in self.deck.sideboard:
            cur.execute(f"""
            REPLACE INTO {self.cards_table} (deck_id, name, quantity, is_sideboard)
            VALUES (:deck_id, :name, :quantity, :is_sideboard);
            """,
            {
                "deck_id": self.deck.id,
                "name": card.name,
                "quantity": card.quantity,
                "is_sideboard": True
            })

        cur.close()
        conn.commit()
        conn.close()


    def _create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.decks_table} (
            id INT PRIMARY KEY,
            url STRING,
            title STRING,
            player_id STRING,
            tournament_id INT
        ) WITHOUT ROWID;
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.cards_table} (
            deck_id INT NOT NULL,
            name STRING NOT NULL,
            quantity STRING NOT NULL,
            is_sideboard BOOL NOT NULL,
            PRIMARY KEY(deck_id, name, quantity, is_sideboard)
        );
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.players_table} (
            id STRING PRIMARY KEY,
            url STRING,
            name STRING
        ) WITHOUT ROWID;
        """)

        cur.close()
        conn.commit()
        conn.close()