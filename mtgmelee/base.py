class Decklist(object):
    def __init__(self, *, id, url, title, player, main_deck, sideboard, tournament_id):
        self.id = id
        self.url = url
        self.title = title
        self.player = player
        self.main_deck = main_deck
        self.sideboard = sideboard
        self.tournament_id = tournament_id

    def __str__(self):
        return f"Deck: {self.title} by {self.player}"

class Card(object):
    def __init__(self, *, name, quantity):
        self.name = name
        self.quantity = quantity

    def __str__(self):
        return f"{self.quantity} {self.name}"


class Player(object):
    def __init__(self, *, id, url, name):
        self.id = id
        self.url = url
        self.name = name

    def __str__(self):
        return self.name


class Result(object):
    def __init__(self,
                 *,
                 tournament_id,
                 rnd,
                 player1,
                 player1_deck_id,
                 player2,
                 player2_deck_id,
                 winner,
                 wins,
                 losses):
        self.tournament_id = tournament_id
        self.rnd = rnd
        self.player1 = player1
        self.player1_deck_id = player1_deck_id
        self.player2 = player2
        self.player2_deck_id = player2_deck_id
        self.winner = winner
        self.wins = wins
        self.losses = losses

    def __str__(self):
        return f'{self.player1_name} vs {self.player2_name}'
