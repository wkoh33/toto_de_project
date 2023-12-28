import json 
import datetime
import boto3
import uuid
import os

client = boto3.client('stepfunctions')

def validate(date_text):
    try:
        datetime.date.fromisoformat(date_text)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def lambda_handler(event, context):
    transaction_id = str(uuid.uuid1())
    state_machine_arn = os.getenv('state_machine_arn')

    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    start_date = f"{end_date.split('-')[0]}-{end_date.split('-')[1]}-01"
    
    is_backfill = False
    if 'startDate' in event and 'endDate' in event:
        startDate = event['startDate']
        endDate = event['endDate']
        
        validate(startDate)
        validate(endDate)
            
        start_date = startDate
        end_date = endDate
        
        is_backfill = True
    
    print(f'{"BACKFILL" if is_backfill else "FORWARD FILL"} - Start: {start_date} to End: {end_date}')
    message = {transaction_id: transaction_id,"startDate": start_date, "endDate": end_date}
    
    response = client.start_execution(
		stateMachineArn=state_machine_arn,
		name=transaction_id,
		input=json.dumps(message)	
	)