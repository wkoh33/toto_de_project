import json
from datetime import datetime
import boto3
import uuid
import os

client = boto3.client('stepfunctions')

def lambda_handler(event, context):
    transaction_id = str(uuid.uuid1())
    state_machine_arn = os.getenv('state_machine_arn')

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = f"{end_date.split('-')[0]}-{end_date.split('-')[1]}-01"
    
    message = {transaction_id: transaction_id,"startDate": start_date, "endDate": end_date}
    
    response = client.start_execution(
		stateMachineArn=state_machine_arn,
		name=transaction_id,
		input=json.dumps(message)	
	)