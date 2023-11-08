import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import boto3
import json
import random
import time
import os

client = boto3.client('s3')

def process_outlets(outlets, prize_group, df):
    for outlet_entry in outlets:
        outlet_entry = outlet_entry.get_text(strip=True)
        
        tmp_df = process_entry(outlet_entry, prize_group)
        df = df._append(tmp_df, ignore_index=True)

    return df

def process_entry(outlet_entry, prize_group):
    tmp_df = pd.DataFrame()

    # Check if outlet entry is iTOTO - System 12
    if 'iTOTO - System 12' in outlet_entry:
        outlets = outlet_entry.split("•")[1:]
        for outlet_address in outlets:
            outlet_address = outlet_address.split('-')
            outlet = outlet_address[0].strip()
            address = '-'.join(outlet_address[1:]).strip()

            tmp_df = tmp_df._append({
                'prize_group': prize_group,
                'outlet': outlet,
                'address': address,
                'count': 1,
                'entry': 'iTOTO - System 12',
                'is_quickpick': 0
            }, ignore_index=True)
    else:
        outlet_address = outlet_entry.split(" ( ")[0].strip()
        outlet_address = outlet_address.split('-')
        outlet = outlet_address[0].strip()
        address = '-'.join(outlet_address[1:]).strip()

        entry = outlet_entry.split(" ( ")[1].strip()
        count = int(entry.split(" ")[0].strip())
        is_quickpick = 1 if 'QuickPick' in entry else 0

        entry = entry.replace("QuickPick", "").replace("Entry )", "").strip()
        if "Ordinary" in entry:
            entry = 'Ordinary'
        elif "System" in entry:
            entry = 'System ' + entry.split("System ")[1].strip()
        tmp_df = tmp_df._append({
            'prize_group': prize_group,
            'outlet': outlet,
            'address': address,
            'count': count,
            'entry': entry.strip(),
            'is_quickpick': is_quickpick
        }, ignore_index=True)
    
    return tmp_df

def process_winning_outlets(soup, draw_date):
    # Get winning outlets
    winning_outlets_list = soup.find('div', { 'class' : 'divWinningOutlets' })
    df = pd.DataFrame()

    # Get Group 1
    group_1_winner_check = winning_outlets_list.select('strong')[0].get_text(strip=True)
    ul_index = 0

    if 'Group 1 winning tickets sold at' in group_1_winner_check:
        # Contains winning outlets
        group_1_winner_outlets = winning_outlets_list.select('ul')[ul_index].findAll('li')
        ul_index += 1
        
        df = process_outlets(group_1_winner_outlets, 1, df)

    # Get Group 2
    group_2_winner_check = winning_outlets_list.select('strong')[1].get_text(strip=True)
    if 'Group 2 winning tickets sold at' in group_2_winner_check:
        # Contains winning outlets
        group_2_winner_outlets = winning_outlets_list.select('ul')[ul_index].findAll('li')
        df = process_outlets(group_2_winner_outlets, 2, df)
                
    df['draw_date'] = draw_date
    
    return df

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

    # Get winning outlets
    winning_outlets_df = process_winning_outlets(soup, draw_date)
    
    # Save to s3
    bucket = os.environ['S3_BUCKET_NAME']

    client.put_object(
        Body=winning_outlets_df.to_csv(index=False),
        Bucket=bucket,
        Key=f"data/raw/winning_outlets/{draw_date}.csv"
    )