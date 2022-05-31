import boto3
from operator import itemgetter
from flask import Flask
from flask import render_template, request

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

table = dynamodb.Table('Field')
response = table.scan()
db_fields = response['Items']

table = dynamodb.Table('Greenhouse')
response = table.scan()
db_greenhouses = response['Items']

table = dynamodb.Table('SavedWater')
response = table.scan()
db_water = response['Items']

water = [0,0,0,0,0,0,0,0,0,0,0,0]

imgf = ['https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%3Fid%3DOIP.F-F8-i8r92hK0c9pNHv1vAHaE8%26pid%3DApi&f=1',
	'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%3Fid%3DOIP.Jg6zrHaFRdGZw645jE_dpgHaEK%26pid%3DApi&f=1',
	'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ffoodprint.org%2Fwp-content%2Fuploads%2F2018%2F10%2FGettyImages-907966126_optimized.jpg&f=1&nofb=1']
	
imgg = ['https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.rvrXVsrIeadMqbwa4GtofAHaGL%26pid%3DApi&f=1',
	'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.TSD6aTq1ks1QWTQvE5edxgHaE4%26pid%3DApi&f=1',
	'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimages.freeimages.com%2Fimages%2Flarge-previews%2Fe7d%2Fgreenhouses-1406881.jpg&f=1&nofb=1']

for element in db_water:
	value = 0
	for day in element['days']:
		value += int(day)
	water[int(element['month-year'].split('-')[0]) - 1] = value

@app.route("/", methods=["GET", "POST"])
def homepage():
	if request.method == 'POST':
		table = ''
		if request.form.get('type') == "field":
			table = dynamodb.Table('Field')
		else:
			table = dynamodb.Table('Greenhouse')
		
		
		vid = str(request.form.get('id'))
		crop_type = str(request.form.get('a'))
		mqs = str(request.form.get('b'))
		
		if vid == "new":
			table.put_item(Item={'id': str(table.item_count+1), 'mq_available': mqs, 'crop_type': crop_type, 'ph': '7'})
		else:
			table.update_item(Key={'id': vid}, UpdateExpression="set crop_type = :crop_type", ExpressionAttributeValues={':crop_type': crop_type})
			table.update_item(Key={'id': vid}, UpdateExpression="set mq_available = :mq_available", ExpressionAttributeValues={':mq_available': mqs})
	
		response1 = dynamodb.Table('Field').scan()
		response2 = dynamodb.Table('Greenhouse').scan()
		
		return render_template('dashboard.html', fields=sorted(response1['Items'], key=lambda k : k['id']), greenhouses=sorted(response2['Items'], key=lambda k : k['id']), water=water, imgf=imgf, imgg=imgg, changhed='true')
		
	return render_template('dashboard.html', fields=sorted(db_fields, key=lambda k : k['id']), greenhouses=sorted(db_greenhouses, key=lambda k : k['id']), water=water, imgf=imgf, imgg=imgg)
	
	
