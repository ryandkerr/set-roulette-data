import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TournamentResultsScraper(object):
    def __init__(self,
                 *,
                 tournament_url,
                 chrome_driver_path,
                 data_dir,
                 raw_dir,
                 sleep_sec=5):
        self.tournament_url = tournament_url
        self.chrome_driver_path = chrome_driver_path
        self.data_dir = data_dir
        self.raw_dir = raw_dir
        self.tournament_id = tournament_url.split('/')[-1]
        self.sleep_sec = sleep_sec

    def scrape(self):
        driver = self.create_driver()
        driver.get(self.tournament_url)

        tournament_dir = f"./{self.data_dir}/{self.raw_dir}/{self.tournament_id}"
        if not os.path.exists(tournament_dir):
            os.makedirs(tournament_dir)
        
        results_page = 0
        while True:
            time.sleep(self.sleep_sec)
            source = driver.page_source
            file_name = f"{tournament_dir}/tournament_standings_{self.tournament_id}_{results_page}.html"
            out = open(file_name, "w")
            out.write(source)
            out.close()
            
            button = driver.find_element_by_id('tournament-standings-table_next')
            if 'disabled' in button.get_attribute('class'):
                break

            driver.execute_script("arguments[0].click();", button)
            results_page += 1

        driver.close()
        
    def create_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        return webdriver.Chrome(executable_path=self.chrome_driver_path,
                                options=chrome_options)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise StandardError("Usage: python3 selenium_testing.py <TOURNAMENT_URL>")

    chrome_driver_path = './chromedriver'
    data_dir = 'data'
    raw_dir = 'raw'

    
    tournament_url = sys.argv[1]
    scraper = TournamentResultsScraper(tournament_url=tournament_url,
                                       chrome_driver_path=chrome_driver_path,
                                       data_dir=data_dir,
                                       raw_dir=raw_dir)
    scraper.scrape()
