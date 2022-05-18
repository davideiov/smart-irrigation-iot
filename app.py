import boto3
from flask import Flask
from flask import render_template

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

@app.route("/")
def homepage():
    return render_template('dashboard.html', fields=db_fields, water=water)
