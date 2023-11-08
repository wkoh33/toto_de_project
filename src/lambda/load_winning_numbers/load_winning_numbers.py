import requests
from bs4 import BeautifulSoup
from datetime import datetime
import boto3
import json
import random
import time
import os

client = boto3.client('s3')

def process_winning_num(soup, draw_date):
    numbers_table = soup.findAll('table', { 'class' : 'table table-striped' })
    winning_numbers_table = numbers_table[0].findAll('td')

    winning_numbers = [number.text for number in winning_numbers_table]
    additional_number = numbers_table[1].find('td').text

    winning_num_json = {"winning_num_" + str(index + 1): value for index, value in enumerate(winning_numbers)}
    winning_num_json['additional_num'] = additional_number
    winning_num_json['draw_date'] = draw_date

    return winning_num_json

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

    # Get winning numbers and additional number
    winning_num_json = process_winning_num(soup, draw_date)

    # Save to s3
    bucket = os.environ['S3_BUCKET_NAME']

    client.put_object(
        Body=json.dumps(winning_num_json),
        Bucket=bucket,
        Key=f"data/raw/winning_numbers/{draw_date}.json"
    )