from .base import *
from bs4 import BeautifulSoup

class DecklistParser(object):
    def __init__(self, soup):
        self.soup = soup

    def parse(self):
        id = int(self.soup.find('input', attrs={'name':'decklistId'})['value'])
        url = self.soup.find('meta', property='og:url')['content']
        title = self.soup.find('meta', property='og:title')['content']
        tournament_id = int(self.soup.find('div', class_='decklist-card-info-tournament') \
            .find('a')['href'].split('/')[-1])

        player_info = self.soup.find('span', class_='decklist-card-title-author').find('a')
        player_name = player_info.string
        player_url = 'http://mtgmelee.com' + player_info['href']
        player_id = player_info['href'].split('/')[-1]
        player = Player(name=player_name, url=player_url, id=player_id)
        
        tables = self.soup.find('div', class_='decklist-card-body') \
                     .find_all('table', class_='decklist-section-table')

        main_deck_tables = [t for t in tables if not self._is_sideboard(t)]
        sideboard_table = [t for t in tables if self._is_sideboard(t)]

        main_deck = self._parse_cards(main_deck_tables)
        sideboard = self._parse_cards(sideboard_table)

        return Decklist(id=id,
                        url=url,
                        title=title,
                        player=player,
                        main_deck=main_deck,
                        sideboard=sideboard,
                        tournament_id=tournament_id)
        
    def _is_sideboard(self, table):
        return table.find('thead').find_all('td')[0].string.lower() == 'sideboard'

    def _parse_cards(self, tables):
        out = []
        for table in tables:
            names = table.find('tbody') \
                         .find_all('td', class_='decklist-builder-card-name-cell')
            names = [x.string for x in names]
            quantities = table.find('tbody') \
                              .find_all('td', class_='decklist-builder-card-quantity-cell')
            quantities = [x.string for x in quantities]

            assert(len(names) == len(quantities))

            cards = {}
            for name, quantity in zip(names, quantities):
                if name in cards:
                    cards[name] += quantity
                else:
                    cards[name] = quantity

            for name, quantity in cards.items():
                out.append(Card(name=name, quantity=quantity))

        return out

        