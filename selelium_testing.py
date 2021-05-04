import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = './chromedriver'
DATA_FOLDER = 'data'
RAW_FOLDER = 'raw'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise StandardError("Usage: python3 selenium_testing.py <TOURNAMENT_URL>")

    tournament_url = sys.argv[1]
    tournament_id = tournament_url.split('/')[-1]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,
                            # options=chrome_options
                            )

    driver.get(tournament_url)
    directory_name = f"./{DATA_FOLDER}/{RAW_FOLDER}/{tournament_id}"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    results_page = 0
    while True:
        time.sleep(5)
        source = driver.page_source
        file_name = f"{directory_name}/tournament_standings_{tournament_id}_{results_page}.html"
        out = open(file_name, "w")
        out.write(source)
        out.close()
        
        button = driver.find_element_by_id('tournament-standings-table_next')
        if 'disabled' in button.get_attribute('class'):
            break

        driver.execute_script("arguments[0].click();", button)
        results_page += 1

    driver.close()
