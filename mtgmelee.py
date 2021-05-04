class Decklist(object):
    def __init__(self, *, id, url, title, player, main_deck, sideboard):
        self.id = id
        self.url = url
        self.title = title
        self.player = player
        self.main_deck = main_deck
        self.sideboard = sideboard

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
    def __init__(self, *, round, opponent, decklist, result):
        self.round = round
        self.opponent = opponent
        self.decklist = decklist
        self.result = result

    def __str__(self):
        return self.result
