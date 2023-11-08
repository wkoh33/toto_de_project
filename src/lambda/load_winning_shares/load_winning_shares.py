import requests
from bs4 import BeautifulSoup
from datetime import datetime
import boto3
import json
import random
import time

def process_prize_amount(soup):
    prize_amount = soup.find('table', { 'class' : 'jackpotPrizeTable' }).find('td').text
    prize_amount = prize_amount.replace('$', '').replace(',', '')

    return prize_amount

def process_winning_shares(soup, winning_shares_json, draw_date):
    # Get winning shares
    winning_shares_table = soup.find('table', { 'class' : 'tableWinningShares' }).findAll('tr')

    # df = pd.DataFrame(columns=['prize_group', 'share_amount', 'number_of_winning_shares', 'draw_date'])
    for row in winning_shares_table:
        cols = row.findAll('td')
        cols_cleaned = [col.text.strip() for col in cols]
        if len(cols_cleaned) > 0:
            prize_group = cols_cleaned[0].replace('Group ', '')
            
            share_amount = cols_cleaned[1].replace('$', '').replace(',', '')
            if share_amount == '-':
                share_amount = None
            
            num_winning_shares = cols_cleaned[2].replace(',', '')
            if num_winning_shares == '-':
                num_winning_shares = None

            winning_shares_json['share_amount_' + str(prize_group)] = share_amount
            winning_shares_json['num_of_winning_shares_' + str(prize_group)] = num_winning_shares
    
    winning_shares_json['draw_date'] = draw_date
    return winning_shares_json

def handler(event, context):
    querystring = event["querystring"]
    # querystring = "sppl=RHJhd051bWJlcj0zNjE0"
    URL = "https://www.singaporepools.com.sg/en/product/Pages/toto_results.aspx?" + querystring
    
    time.sleep(random.randint(1, 5))
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # Get draw date
    draw_date_string = soup.find('th', { 'class' : 'drawDate' }).text
    parsed_date = datetime.strptime(draw_date_string, "%a, %d %b %Y")
    draw_date = parsed_date.strftime("%Y-%m-%d")

    # Get Group 1 prize amount
    prize_amount = process_prize_amount(soup)
    winning_shares_json = {'prize_amount': prize_amount}

    # Get winning shares
    winning_shares_json = process_winning_shares(soup, winning_shares_json, draw_date)
    
    return winning_shares_json