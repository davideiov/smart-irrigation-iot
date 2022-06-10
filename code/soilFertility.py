import boto3
import time
import requests
from config import DefaultConfig

def send_notifications(forg, num, crop, ph):
	CONFIG = DefaultConfig()
	client = boto3.client('ses', endpoint_url="http://localhost:4566")
	message = {
		'Subject': {
		    'Data': 'Fields problem',
		    'Charset': 'UTF-8'
		},
		'Body': {
		    'Text': {
		        'Data': 'There is a problem with the ' + forg + ' number ' + num + ' where the crops are ' + crop + ', the soil ph is ' + ph + '!\nPlease use fertilizer to avoid the lose of your crop.',
		        'Charset': 'string'
		    },
		    'Html': {
		        'Data': 'This message body contains HTML formatting.',
		        'Charset': 'UTF-8'
		    }
		}
	}
		
	response = client.send_email(
		Source="sender@example.com",
		Destination={
		    'ToAddresses': [
		        CONFIG.EMAIL_FARMER,
		    ],
		    'CcAddresses': [],
		    'BccAddresses': []
		},
		Message=message
	)
	
	log_client = boto3.client('logs',endpoint_url="http://localhost:4566")
		
	log_event = {
		'logGroupName': 'SoilFertility',
		'logStreamName': 'EmailSent',
		'logEvents': [
		    {
		        'timestamp': int(round(time.time() * 1000)),
		        'message': str(message)
		    },
		],
	}

	log_client.put_log_events(**log_event)
	if CONFIG.BOT_USE == "true":
		requests.get('https://api.telegram.org/bot' + CONFIG.BOT_TOKEN + '/sendMessage?chat_id=' + CONFIG.BOT_ID + '&parse_mode=Markdown&text=' + str(message["Body"]["Text"]["Data"]))
		
	print("\nThe message with id '" + response["MessageId"] + "' is corrected sent to " + CONFIG.EMAIL_FARMER + ' and to telegram bot!')
	

def check_ph():
	dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
	
	table_f = dynamodb.Table('Field')
	response_f = table_f.scan()
	fields = response_f['Items']
	
	table_g = dynamodb.Table('Greenhouse')
	response_g = table_g.scan()
	greenhouses = response_g['Items']
	
	for field in fields:
		if int(field["ph"]) < 4 or int(field["ph"]) > 9:
			send_notifications("field", field["id"], field["crop_type"], field["ph"])

	for greenhouse in greenhouses:
		if int(greenhouse["ph"]) < 4 or int(greenhouse["ph"]) > 9:
			send_notifications("greenhouse", greenhouse["id"], greenhouse["crop_type"], greenhouse["ph"])

def lambda_handler(event, context):
 	check_ph()
