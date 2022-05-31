import boto3
import datetime
import random

client = boto3.client('sqs', endpoint_url='http://localhost:4566')
today = str(datetime.datetime.now().strftime("%d-%m-%Y"))

def air_temperature():
	r = random.randint(20, 80)
	msg = str(r)
	client.send_message(QueueUrl='http://localhost:4566/000000000000/ventilation', MessageBody=msg, MessageAttributes={'date': {'StringValue': today, 'DataType': 'String'}})
	print('-- Air temperature of greenhouses: ' + msg + '° C')

air_temperature()
