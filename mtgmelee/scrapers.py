import os
import pdb
import requests
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TournamentScraper(object):
    def __init__(self,
                 *,
                 tournament_url,
                 chrome_driver_path,
                 out_dir,
                 sleep_sec=5):
        self.tournament_url = tournament_url
        self.chrome_driver_path = chrome_driver_path
        self.out_dir = out_dir
        self.sleep_sec = sleep_sec

    def scrape_standings(self):
        driver = self._create_driver()
        driver.get(self.tournament_url)

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        
        standings_page = 0
        while True:
            print(f'Scraping standings page {standings_page}')
            time.sleep(self.sleep_sec)
            source = driver.page_source
            file_name = f'{self.out_dir}/tournament_standings_{standings_page}.html'
            out = open(file_name, 'w')
            out.write(source)
            out.close()
            
            button = driver.find_element_by_id('tournament-standings-table_next')
            if 'disabled' in button.get_attribute('class'):
                break

            driver.execute_script('arguments[0].click();', button)
            standings_page += 1

        driver.close()

    def scrape_results(self):
        driver = self._create_driver()
        driver.get(self.tournament_url)

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        
        #TODO
        # for each round button
            # click the button
            # wait
            # click "show 500 rows"
            # wait
            # save page to dir

        driver.close()
        
    def _create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        return webdriver.Chrome(executable_path=self.chrome_driver_path,
                                options=chrome_options)


class StandingsToDecklistsScraper(object):
    def __init__(self, *, tournament_dir, out_dir):
        self.tournament_dir = tournament_dir
        self.out_dir = out_dir

    def scrape(self):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        
        for result_file in os.listdir(self.tournament_dir):
            with open(f'{self.tournament_dir}/{result_file}') as f:
                html = f.read()
                soup = BeautifulSoup(html, 'html.parser')

                decklist_rows = soup.find(id='tournament-standings-table') \
                    .find('tbody') \
                    .find_all('td', class_='Decklists-column')

                decklist_urls = []
                for row in decklist_rows:
                    a = row.find('a')
                    if a:  # is is possible for a player to not submit a decklist
                        decklist_urls.append(f"https://mtgmelee.com{a['href']}")

                for url in decklist_urls:
                    print(f'Scraping {url}')
                    time.sleep(.2)

                    decklist_id = url.split('/')[-1]
                    response = requests.get(url)
                    decklist_soup = BeautifulSoup(response.content, 'html.parser')
                    file_name = f'{self.out_dir}/decklist_{decklist_id}.html'
                    out = open(file_name, 'w')
                    out.write(str(decklist_soup))
                    out.close()

if __name__ == '__main__':
    scraper = TournamentScraper(tournament_url='https://mtgmelee.com/Tournament/View/389',
        chrome_driver_path='~/Dropbox/projects/mtg/set-roulette/set-roulette-data/chromedriver',
        out_dir='~/Dropbox/projects/mtg/set-roulette/set-roulette-data/data/raw/389/results')

    scraper.scrape_results()
