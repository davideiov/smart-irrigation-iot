import boto3
import datetime
import json
import requests
from config import DefaultConfig

client = boto3.client('sqs', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
today = str(datetime.datetime.now().strftime("%d-%m-%Y"))

def get_weather() -> dict:
	CONFIG = DefaultConfig()

	url_today = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + CONFIG.FIELDS_LOC + "%20italia/today?unitGroup=metric&elements=tempmax%2Ctempmin%2Ctemp%2C" + "humidity%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Ccloudcover%2C" + "solarradiation%2Cconditions%2Cet0&include=days%2Ccurrent%2Calerts&" + "key=" + CONFIG.WEATHER_KEY + "&contentType=json"

	url_yesterday = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + CONFIG.FIELDS_LOC + "%20italia/yesterday?unitGroup=metric&elements=tempmax%2Ctempmin%2Ctemp%2C" + "humidity%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Ccloudcover%2C" + "solarradiation%2Cconditions%2Cet0&include=days%2Ccurrent%2Calerts&" + "key=" + CONFIG.WEATHER_KEY + "&contentType=json"

	weather_info = {
		"yesterday": requests.get(url=url_today).json(),
		"today": requests.get(url=url_yesterday).json()
	}
	
	return weather_info
    
def get_iot_info():
	temp = 0
	hum = 0

	hum_msg = client.receive_message(QueueUrl='http://localhost:4566/000000000000/humidity', AttributeNames=['All'], MessageAttributeNames=['date'])
	temp_msg = client.receive_message(QueueUrl='http://localhost:4566/000000000000/temperature', AttributeNames=['All'], MessageAttributeNames=['date'])

	if "Messages" in hum_msg.keys():
		date = hum_msg["Messages"][0]["MessageAttributes"]["date"]["StringValue"]
		if date == today:
			hum = int(hum_msg["Messages"][0]["Body"])
		client.delete_message(QueueUrl='http://localhost:4566/000000000000/humidity', ReceiptHandle=hum_msg["Messages"][0]["ReceiptHandle"])
				
	if "Messages" in temp_msg.keys():
		date = temp_msg["Messages"][0]["MessageAttributes"]["date"]["StringValue"]
		if date == today:
			temp = int(temp_msg["Messages"][0]["Body"])
		client.delete_message(QueueUrl='http://localhost:4566/000000000000/temperature', ReceiptHandle=temp_msg["Messages"][0]["ReceiptHandle"])

	if hum == 0 or temp == 0:
		print("--- THERE IS A PROBLEM WITH AT LEAST ONE QUEUE ---")

	return temp, hum	

def process_data():
	weather_info = get_weather()
	soil_temp, soil_hum = get_iot_info()

	f = open('needs.json')
	fabb_schema = json.load(f)
	f.close()

	mm_yesterday = weather_info["yesterday"]["days"][0]["precip"] 	#mm fallen yesterday
	prob_prec_today = weather_info["today"]["days"][0]["precipprob"] 	#probability of rain today
	prob_mm_today = weather_info["today"]["days"][0]["precip"] 	#mm waited today
	
	day = today.split("-")[0]
	month = today.split("-")[1]
	year = today.split("-")[2]
	
	table = dynamodb.Table('Field')
	response = table.scan()
	fields = response['Items']
	
	table = dynamodb.Table('Greenhouse')
	response = table.scan()
	greenhouses = response['Items']
	
	for gh in greenhouses:
		gh["type"] = "gh";
	
	fields.extend(greenhouses)
	
	saved_water_fields = []
	
	for field in fields:
		crop_type = field['crop_type']
		mq_field = float(field['mq_available'])
		expected_fabb = float(fabb_schema[crop_type][month]) #daily need, lt/m2 a day
		fabb_today = expected_fabb

		#decrease an half of amount of water fallen yesterday
		fabb_today = float(fabb_today - (mm_yesterday/2))

		#simulation of an irrigation plan due precipitation probability
		if prob_prec_today > 20 and prob_prec_today < 40: 
			fabb_today = fabb_today - prob_mm_today/4
		elif prob_prec_today > 40 and prob_prec_today < 80:
			fabb_today = fabb_today - prob_mm_today/3
		elif prob_prec_today > 80 and prob_prec_today < 100:
			fabb_today = fabb_today - prob_mm_today/2

		#increase of irrigation due soil temperature
		if soil_temp > 19 and soil_temp < 26:
			fabb_today = fabb_today + fabb_today/8
		elif soil_temp > 25 and soil_temp < 31:
			fabb_today = fabb_today + fabb_today/6
		elif soil_temp > 31:	
			fabb_today = fabb_today + fabb_today/4

		#decrease of irrigation due soil humidity
		if soil_hum > 59 and soil_hum < 71:
			fabb_today = fabb_today - fabb_today/10
		elif soil_hum > 70 and soil_hum < 81:
			fabb_today = fabb_today - fabb_today/8
		elif soil_hum > 80:
			fabb_today = fabb_today - fabb_today/6

		#amount of water saved
		if float(expected_fabb - fabb_today) > 0:
			saved_water = float(expected_fabb - fabb_today) 
		else:
			saved_water = 0
		
		saved_water = round(saved_water * mq_field, 2)
		fabb_today = round(fabb_today * mq_field, 2)
		
		saved_water_fields.append(saved_water)
		
		#send request to sprinklers IoT
		if "type" in field:
			#r = requests.get('https://sprinklers?greenhouse=' + field['id'] + '&lt=' str(fabb_today))
			print( "requests.get('https://sprinklers?greenhouse=" + field['id'] + "&lt=" + str(fabb_today) + "')" )
		else:
			#r = requests.get('https://sprinklers?field=' + field['id'] + '&lt=' str(fabb_today))
			print( "requests.get('https://sprinklers?field=" + field['id'] + "&lt=" + str(fabb_today) + "')" )

	total_water_saved_today = 0;
	for elem in saved_water_fields:
		total_water_saved_today = total_water_saved_today + elem
	
	table_water = dynamodb.Table('SavedWater')
	element = table_water.get_item(Key={'month-year': month + '-' + year})
	
	if "Item" in element.keys():
		days = element['Item']['days']
	else:
		days = []
		
	days.append(int(total_water_saved_today))
	table_water.update_item(Key={'month-year': month + '-' + year}, UpdateExpression="set days = :days", ExpressionAttributeValues={':days': days})
	print("Amount of water saved today: " + str(total_water_saved_today))

def lambda_handler(event, context):
	process_data()
    
    
