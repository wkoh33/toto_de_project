from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import json

def check_input_dates(start_date, end_date):
    date_format = '%Y-%m-%d'

    # Check if start_date and end_date format are valid
    try:
        check_start_date = datetime.strptime(start_date, date_format)
        check_end_date = datetime.strptime(end_date, date_format)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

    # Check if start_date and end_date are valid
    if check_start_date > check_end_date:
        raise ValueError("start_date should be before end_date")

def lambda_handler(event, context):
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    
    start_date = event['startDate']
    end_date = event['endDate']
    
    # Check input dates
    # start_date = '2022-01-01'
    # end_date = '2022-03-01'
    check_input_dates(start_date, end_date)
    print("Dates valid")
    
    time.sleep(random.randint(1, 5))
    URL = "https://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx"

    driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)
    driver.implicitly_wait(10) # seconds

    driver.get(URL)
    
    # click on date dropdown to trigger webpage JS to load all dates
    date_options = driver.find_element(By.CLASS_NAME, "selectDrawList")
    date_options.click()
    
    # Get source code
    html_source = driver.page_source

    driver.close();
    driver.quit();

    # Get dates
    soup = BeautifulSoup(html_source, "html.parser")
    date_options = soup.select('select.selectDrawList option')
    
    message = []
    for option in date_options:
        if option.text == 'Please select':
            continue
        
        draw_date_string = option.text
        parsed_date = datetime.strptime(draw_date_string, "%a, %d %b %Y")
        draw_date = str(parsed_date.strftime("%Y-%m-%d"))
        
        querystring = option['querystring']
        
        # Check if draw_date is within start_date and end_date
        if start_date <= draw_date <= end_date:
            message.append({
                'draw_date': draw_date,
                'querystring': querystring
            })
    
    return message