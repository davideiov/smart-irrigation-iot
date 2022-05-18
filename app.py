import boto3
from operator import itemgetter
from flask import Flask
from flask import render_template, request

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

table = dynamodb.Table('Fields')
response = table.scan()
db_fields = response['Items']

table = dynamodb.Table('SavedWater')
response = table.scan()
db_water = response['Items']

water = [0,0,0,0,0,0,0,0,0,0,0,0]

for element in db_water:
	value = 0
	for day in element['days']:
		value += int(day)
	water[int(element['month-year'].split('-')[0]) - 1] = value

@app.route("/", methods=["GET", "POST"])
def homepage():
	if request.method == 'POST':
		table = dynamodb.Table('Fields')
		field_id = str(request.form.get('id'))
		crop_type = str(request.form.get('a'))
		mqs = str(request.form.get('b'))
		
		table.update_item(Key={'id': field_id}, UpdateExpression="set crop_type = :crop_type", ExpressionAttributeValues={':crop_type': crop_type})
		table.update_item(Key={'id': field_id}, UpdateExpression="set mq_available = :mq_available", ExpressionAttributeValues={':mq_available': mqs})
	
		response = table.scan()
		
		return render_template('dashboard.html', fields=sorted(response['Items'], key=lambda k : k['id']), water=water)
		
	return render_template('dashboard.html', fields=sorted(db_fields, key=lambda k : k['id']), water=water)
	
	
