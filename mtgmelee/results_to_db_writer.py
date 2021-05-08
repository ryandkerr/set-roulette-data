import sqlite3

class ResultsToDBWriter(object):
    def __init__(self, *, results, db_name, results_table):
        self.results = results
        self.db_name = db_name
        self.results_table = results_table

    def write_to_db(self):
        self._create_table()
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        for result in self.results:
            tournament_id = result.tournament_id
            rnd = result.rnd

            # check for byes, and sort players alphabetically
            if (result.player2 is None) or (result.player1.id.lower() < result.player2.id.lower()):
                player1_id = result.player1.id
                player2_id = result.player2.id if result.player2 else None
                player1_deck_id = result.player1_deck_id
                player2_deck_id = result.player2_deck_id
                winner_id = result.winner.id if result.player2 else None
                wins = result.wins
                losses = result.losses
            else:
                player1_id = result.player2.id
                player2_id = result.player1.id
                player1_deck_id = result.player2_deck_id
                player2_deck_id = result.player1_deck_id
                winner_id = result.winner.id
                wins = result.wins
                losses = result.losses

            cur.execute(f"""
            REPLACE INTO {self.results_table} (tournament_id, rnd, player1_id, player2_id, player1_deck_id, player2_deck_id, winner_id, wins, losses)
            VALUES (:tournament_id, :rnd, :player1_id, :player2_id, :player1_deck_id, :player2_deck_id, :winner_id, :wins, :losses)
            """,
            {
                "tournament_id": tournament_id,
                "rnd": rnd,
                "player1_id": player1_id,
                "player2_id": player2_id,
                "player1_deck_id": player1_deck_id,
                "player2_deck_id": player2_deck_id,
                "winner_id": winner_id,
                "wins": wins,
                "losses": losses
            })

        cur.close()
        conn.commit()
        conn.close()

    def _create_table(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.results_table} (
            tournament_id INT,
            rnd STRING,
            player1_id STRING,
            player2_id STRING,
            player1_deck_id STRING,
            player2_deck_id STRING,
            winner_id STRING,
            wins INT,
            losses INT,
            PRIMARY KEY(tournament_id, rnd, player1_id, player2_id)
        );
        """)

        cur.close()
        conn.commit()
        conn.close()