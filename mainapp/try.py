from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.keys import Keys


chrome_options = Options()
# chrome_options.add_experimental_option("prefs", {
#     "download.prompt_for_download": True,
#     "download.directory_upgrade": True,
#     "safebrowsing.enabled": True
# })

driver = Chrome(executable_path='D:\jupyter\stockforecast\chromedriver.exe', options=chrome_options)

driver.get('https://nepsealpha.com/nepse-data')



select_click = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(4) > span > span.selection > span')
select_click.click()

select_input = driver.find_element(By.CSS_SELECTOR, 'body > span > span > span.select2-search.select2-search--dropdown > input')
select_input.send_keys("rhgcl")
select_input.send_keys(Keys.ENTER)


start_date = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(2) > input')
start_date.send_keys("07/01/2013")

filter_button = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(5) > button')
filter_button.click()
time.sleep(1)

csv_button = driver.find_element(By.CSS_SELECTOR, '#result-table_wrapper > div.dt-buttons > button.dt-button.buttons-csv.buttons-html5.btn.btn-outline-secondary.btn-sm')
csv_button.click()

time.sleep(5)

import os
import subprocess

# Get the user's download folder path
download_folder = os.path.expanduser("~\\Downloads")

# Open the download folder in Windows Explorer
subprocess.Popen(f'explorer "{download_folder}"')
