import csv
import requests

from bs4 import BeautifulSoup

from mtgmelee import *

def make_soup(url):
    response = requests.get(url)
    s = BeautifulSoup(response.content, "html.parser")
    return s

example_deck = 'https://mtgmelee.com/Decklist/View/128264'
soup = make_soup(example_deck)


results_rows = soup.find('div', id='tournament-path-grid-item') \
    .find_all('table')[2] \
    .find_all('tr')

def is_sideboard(table):
    return table.find('thead').find_all('td')[0].string.lower() == 'sideboard'

def parse_cards(tables):
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


def parse_decklist(soup):
    id = soup.find('input', attrs={'name':'decklistId'})['value']
    url = soup.find('meta', property='og:url')['content']
    title = soup.find('meta', property='og:title')['content']

    player_info = soup.find('span', class_='decklist-card-title-author').find('a')
    player_name = player_info.string
    player_url = 'http://mtgmelee.com' + player_info['href']
    player_id = player_info['href'].split('/')[-1]
    player = Player(name=player_name, url=player_url, id=player_id)
    
    tables = soup.find('div', class_='decklist-card-body') \
                 .find_all('table', class_='decklist-section-table')

    main_deck_tables = [t for t in tables if not is_sideboard(t)]
    sideboard_table = [t for t in tables if is_sideboard(t)]

    main_deck = parse_cards(main_deck_tables)
    sideboard = parse_cards(sideboard_table)

    return Decklist(id=id,
                    url=url,
                    title=title,
                    player=player,
                    main_deck=main_deck,
                    sideboard=sideboard)
