import scrython
import time

class BulkSkryfallFetcher(object):
    def __init__(self, card_names):
        self.card_names = set(card_names)

    def fetch_all(self):
        out = []
        for i, card in enumerate(self.card_names):
            if i % 10 == 0:
                print(f'Fetching card {i} out of {len(self.card_names)}')
            time.sleep(.1)
            scry_card = scrython.cards.Named(exact=card)
            out.append(scry_card)

        return out
 