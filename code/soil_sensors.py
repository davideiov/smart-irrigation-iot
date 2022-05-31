import boto3
import datetime
import random

client = boto3.client('sqs', endpoint_url='http://localhost:4566')
today = str(datetime.datetime.now().strftime("%d-%m-%Y"))


def soil_humidity():
	r = random.randint(25, 80)
	msg = str(r)
	client.send_message(QueueUrl='http://localhost:4566/000000000000/humidity', MessageBody=msg, MessageAttributes={'date': {'StringValue': today, 'DataType': 'String'}})
	print('-- Soil moisture: ' + msg + '%')

def soil_temperature():
	r = random.randint(5, 35)
	msg = str(r)
	client.send_message(QueueUrl='http://localhost:4566/000000000000/temperature', MessageBody=msg, MessageAttributes={'date': {'StringValue': today, 'DataType': 'String'}})
	print('-- Soil temperature: ' + msg + '° C')

soil_humidity()
soil_temperature()
