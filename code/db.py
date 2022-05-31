import boto3
import datetime
import random

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

table_water = dynamodb.create_table(
    TableName='SavedWater',
    KeySchema=[
        {
            'AttributeName': 'month-year',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'month-year',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

table_fields = dynamodb.create_table(
    TableName='Field',
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

table_greenhouses = dynamodb.create_table(
    TableName='Greenhouse',
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

table_water.put_item(Item={'month-year': '03-2022', 'days': []})
for i in range(31):
	element = table_water.get_item(Key={'month-year': '03-2022'})
	days = element['Item']['days']
	days.append(int(random.randint(75,300)))
	table_water.update_item(Key={'month-year': '03-2022'}, UpdateExpression="set days = :days", ExpressionAttributeValues={':days': days})

table_water.put_item(Item={'month-year': '04-2022', 'days': []})
for i in range(30):
	element = table_water.get_item(Key={'month-year': '04-2022'})
	days = element['Item']['days']
	days.append(int(random.randint(75,300)))
	table_water.update_item(Key={'month-year': '04-2022'}, UpdateExpression="set days = :days", ExpressionAttributeValues={':days': days})

table_water.put_item(Item={'month-year': '05-2022', 'days': []})
for i in range(int(datetime.datetime.now().strftime("%d")) - 1):
	element = table_water.get_item(Key={'month-year': '05-2022'})
	days = element['Item']['days']
	days.append(int(random.randint(75,300)))
	table_water.update_item(Key={'month-year': '05-2022'}, UpdateExpression="set days = :days", ExpressionAttributeValues={':days': days})
	
table_fields.put_item(Item={'id': '1', 'mq_available': '500', 'crop_type': 'corn', 'ph': '7'})
table_fields.put_item(Item={'id': '2', 'mq_available': '350', 'crop_type': 'soy', 'ph': '7'})
table_fields.put_item(Item={'id': '3', 'mq_available': '600', 'crop_type': 'chard', 'ph': '7'})
table_fields.put_item(Item={'id': '4', 'mq_available': '550', 'crop_type': 'rice', 'ph': '1'})

table_greenhouses.put_item(Item={'id': '1', 'mq_available': '100', 'crop_type': 'fruit', 'ph': '7'})
table_greenhouses.put_item(Item={'id': '2', 'mq_available': '70', 'crop_type': 'vegetable', 'ph': '7'})

client = boto3.client('logs',endpoint_url="http://localhost:4566")
retention_period_in_days = 5

client.create_log_group(logGroupName='SoilFertility')

client.put_retention_policy(
	logGroupName='SoilFertility',
	retentionInDays=retention_period_in_days
)
client.create_log_stream(
    logGroupName='SoilFertility',
    logStreamName='EmailSent'
)

print('Table', table_water, 'created and populated!')
print('Table', table_fields, 'created and populated!')
print('Table', table_greenhouses, 'created and populated!')
print('Cloudwatch stream correctly created!')




