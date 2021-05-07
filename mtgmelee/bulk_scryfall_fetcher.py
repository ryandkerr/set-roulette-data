import scrython
import time

class BulkSkryfallFetcher(object):
    def __init__(self, card_names):
        self.card_names = set(card_names)

    def fetch_all(self):
        out = []
        for card in self.card_names:
            time.sleep(.1)
            scry_card = scrython.cards.Named(exact=card)
            out.append(scry_card)

        return out
 