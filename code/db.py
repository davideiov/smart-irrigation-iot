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
    TableName='Fields',
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
	
table_fields.put_item(Item={'id': '1', 'mq_available': '500', 'type': 'mais'})
table_fields.put_item(Item={'id': '2', 'mq_available': '350', 'type': 'soia'})
table_fields.put_item(Item={'id': '3', 'mq_available': '600', 'type': 'bietola'})
table_fields.put_item(Item={'id': '4', 'mq_available': '550', 'type': 'riso'})

print('Table', table_water, 'created and populated!')
print('Table', table_fields, 'created and populated!')




