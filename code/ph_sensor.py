import boto3
import random

def soil_ph():
	r = random.randint(0, 100)
	if r < 5:
		dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
		
		table_f = dynamodb.Table('Field')
		item_f = table_f.item_count
		
		table_g = dynamodb.Table('Greenhouse')
		item_g = table_g.item_count
		
		r = random.randint(1, min(item_f, item_g))
		
		if random.randint(0,1) == 0:
			table_f.update_item(Key={'id': str(r)}, UpdateExpression="set ph = :ph", ExpressionAttributeValues={':ph': str(random.randint(1,4))})
		else:
			table_g.update_item(Key={'id': str(r)}, UpdateExpression="set ph = :ph", ExpressionAttributeValues={':ph': str(random.randint(1,4))})
		
		print('-- Soil ph (id ' + str(r) + ') is unstable, let\'s send an email!')
	else:
		print('-- Soil ph is stable, that\'s OK!')
soil_ph()
