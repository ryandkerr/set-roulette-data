import sys
from mtgmelee.scrapers import TournamentStandingsScraper, StandingsToDecklistsScraper

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise StandardError('Usage: python3 scrape_tournament.py <TOURNAMENT_URL>')

    chrome_driver_path = './chromedriver'
    data_dir = 'data'
    raw_dir = 'raw'

    
    tournament_url = sys.argv[1]
    tournament_id = tournament_url.split('/')[-1]
    out_dir = f'data/raw/{tournament_id}/standings'
    scraper = TournamentStandingsScraper(tournament_url=tournament_url,
                                         chrome_driver_path=chrome_driver_path,
                                         out_dir=out_dir)
    scraper.scrape()

    decklists_dir = f'data/raw/{tournament_id}/decklists'
    decklist_scraper = StandingsToDecklistsScraper(tournament_dir=out_dir,
                                            out_dir=decklists_dir)
    decklist_scraper.scrape()