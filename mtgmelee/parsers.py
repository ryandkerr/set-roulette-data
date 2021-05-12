import pdb

from .base import *
from bs4 import BeautifulSoup

class DecklistParser(object):
    def __init__(self, soup):
        self.soup = soup

    def parse_decklist(self):
        id = self._get_deck_id()
        url = self.soup.find('meta', property='og:url')['content']
        title = self._get_title()
        tournament_id = self._get_tournament_id()
        player = self._get_player()

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

    def parse_results(self):
        tournament_id = self._get_tournament_id()
        player1 = self._get_player()
        player1_deck_id = self._get_deck_id()

        tb = self.soup.find('div', id='tournament-path-grid-item') \
                 .find_all('table')[2].find('tbody')

        results = []
        rows = tb.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            rnd = tds[0].string
            result_str = tds[3].string
            if len(result_str.split(' won ')) == 1:  # handle byes
                r = Result(tournament_id=tournament_id,
                           rnd=rnd,
                           player1=player1,
                           player1_deck_id=player1_deck_id,
                           player2=None,
                           player2_deck_id=None,
                           winner=player1,
                           wins=None,
                           losses=None)

                results.append(r)
                continue

            winner_name = result_str.split(' won ')[0]
            wins = int(result_str.split(' won ')[1][0])
            losses = int(result_str.split(' won ')[1][2])

            player2_id = tds[1].find('a')['href'].split('/')[-1]
            player2_name = tds[1].find('a').string
            player2_url = "https://mtgmelee.com" + tds[1].find('a')['href']
            player2 = Player(id=player2_id, url=player2_url, name=player2_name)
            if tds[2].find('a'):  # it is possible for someone to not submit a decklist
                player2_deck_id = int(tds[2].find('a')['href'].split('/')[-1])
            else:
                player2_deck_id = None

            winner = player1 if winner_name == player1.name else player2

            r = Result(tournament_id=self._get_tournament_id(),
                       rnd=rnd,
                       player1=player1,
                       player1_deck_id=player1_deck_id,
                       player2=player2,
                       player2_deck_id=player2_deck_id,
                       winner=winner,
                       wins=wins,
                       losses=losses)

            results.append(r)
        return results

    def _get_deck_id(self):
        return int(self.soup.find('input', attrs={'name':'decklistId'})['value'])

    def _get_player(self):
        player_info = self.soup.find('span', class_='decklist-card-title-author').find('a')
        player_name = player_info.string
        player_url = 'https://mtgmelee.com' + player_info['href']
        player_id = player_info['href'].split('/')[-1]
        return Player(name=player_name, url=player_url, id=player_id)

    def _get_title(self):
        return self.soup.find('meta', property='og:title')['content']
    
    def _get_tournament_id(self):
        return int(self.soup.find('div', class_='decklist-card-info-tournament') \
                            .find('a')['href'].split('/')[-1])

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
            quantities = [int(x.string) for x in quantities]

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


class TournamentParser(object):
    def __init__(self, soup):
        self.soup = soup

    def parse_results(self):
        result_rows = self.soup.find('table', id='tournament-pairings-table') \
                               .find('tbody') \
                               .find_all('tr')

        results = []
        for row in result_rows:
            tds = row.find_all('td')
            player1 = self._get_player_from_a(tds[0].find('a'))
            player1_deck_id = int(tds[1].find('a')['href'].split('/')[-1])

            result_str = tds[4].string
            if len(result_str.split(' won ')) == 1:  # handle byes
                r = Result(tournament_id=self._get_tournament_id(),
                           rnd=self._get_round(),
                           player1=player1,
                           player1_deck_id=player1_deck_id,
                           player2=None,
                           player2_deck_id=None,
                           winner=player1,
                           wins=None,
                           losses=None)

                results.append(r)
                continue

            winner_name = result_str.split(' won ')[0]
            wins = int(result_str.split(' won ')[1][0])
            losses = int(result_str.split(' won ')[1][2])

            player2 = self._get_player_from_a(tds[2].find('a'))
            if tds[3].find('a'):  # it is possible for someone to not submit a decklist
                player2_deck_id = int(tds[3].find('a')['href'].split('/')[-1])
            else:
                player2_deck_id = None

            winner = player1 if winner_name == player1.name else player2
            r = Result(tournament_id=self._get_tournament_id(),
                       rnd=self._get_round(),
                       player1=player1,
                       player1_deck_id=player1_deck_id,
                       player2=player2,
                       player2_deck_id=player2_deck_id,
                       winner=winner,
                       wins=wins,
                       losses=losses)
            results.append(r)
        return results

    def _get_player_from_a(self, a):
        url = "https://mtgmelee.com" + a['href']
        id = url.split('/')[-1]
        name = a.string        
        return Player(id=id, url=url, name=name)

    def _get_tournament_id(self):
        return int(self.soup.find('meta', property='og:url')['content'].split('/')[-1])

    def _get_round(self):
        return self.soup.find('div', id='pairings') \
                        .find('button', class_='btn btn-primary round-selector active')['data-name']


if __name__ == '__main__':
    test_file = './data/raw/4985/decklists/decklist_104651.html'
    f = open(test_file)
    html = f.read()
    f.close()

    soup = BeautifulSoup(html, 'html.parser')
    pdb.set_trace()
