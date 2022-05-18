import boto3
import datetime
import json
import requests
from config import DefaultConfig

client = boto3.client('sqs', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
today = str(datetime.datetime.now().strftime("%d-%m-%Y"))

def get_weather(zone:str) -> dict:
	CONFIG = DefaultConfig()

	url_today = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + zone + "%20italia/today?unitGroup=metric&elements=tempmax%2Ctempmin%2Ctemp%2C" + "humidity%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Ccloudcover%2C" + "solarradiation%2Cconditions%2Cet0&include=days%2Ccurrent%2Calerts&" + "key=" + CONFIG.WEATHER_KEY + "&contentType=json"

	url_yesterday = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + zone + "%20italia/yesterday?unitGroup=metric&elements=tempmax%2Ctempmin%2Ctemp%2C" + "humidity%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Ccloudcover%2C" + "solarradiation%2Cconditions%2Cet0&include=days%2Ccurrent%2Calerts&" + "key=" + CONFIG.WEATHER_KEY + "&contentType=json"

	weather_today = requests.get(url=url_today).json()
	weather_yesterday = requests.get(url=url_yesterday).json()
	weather_info = {
		"yesterday": weather_yesterday,
		"today": weather_today
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
				
	if "Messages" in hum_msg.keys():
		date = temp_msg["Messages"][0]["MessageAttributes"]["date"]["StringValue"]
		if date == today:
			temp = int(temp_msg["Messages"][0]["Body"])
		client.delete_message(QueueUrl='http://localhost:4566/000000000000/temperature', ReceiptHandle=temp_msg["Messages"][0]["ReceiptHandle"])

	if hum == 0 or temp == 0:
		print("--- THERE IS A PROBLEM WITH AT LEAST ONE QUEUE ---")

	return temp, hum	

def process_data():
	weather_info = get_weather("nola")
	soil_temp, soil_hum = get_iot_info()

	f = open('fabbisogni.json')
	fabb_schema = json.load(f)
	f.close()

	mm_yesterday = weather_info["yesterday"]["days"][0]["precip"] 	#mm caduti ieri
	prob_prec_today = weather_info["today"]["days"][0]["precipprob"] 	#probabilità di pioggia
	prob_mm_today = weather_info["today"]["days"][0]["precip"] 	#mm attesi in giornata
	
	day = today.split("-")[0]
	month = today.split("-")[1]
	year = today.split("-")[2]
	
	table = dynamodb.Table('Fields')
	response = table.scan()
	fields = response['Items']
	
	saved_water_fields = []
	
	for field in fields:
		crop_type = field['type']
		mq_field = float(field['mq_available'])
		expected_fabb = float(fabb_schema[crop_type][month]) #fabbisogno quotidiano, lt/m2 al giorno
		fabb_today = expected_fabb

		#si sottraggono la metà dei mm di pioggia caduti ieri
		fabb_today = float(fabb_today - (mm_yesterday/2))

		#simulazione di un possibile piano di irrigazione in base alla probabilità di pioggia
		if prob_prec_today > 20 and prob_prec_today < 40: 
			fabb_today = fabb_today - prob_mm_today/4
		elif prob_prec_today > 40 and prob_prec_today < 80:
			fabb_today = fabb_today - prob_mm_today/3
		elif prob_prec_today > 80 and prob_prec_today < 100:
			fabb_today = fabb_today - prob_mm_today/2

		#aumento dell'irrigazione in base alla temperatura del suolo
		if soil_temp > 19 and soil_temp < 26:
			fabb_today = fabb_today + fabb_today/8
		elif soil_temp > 25 and soil_temp < 31:
			fabb_today = fabb_today + fabb_today/6
		elif soil_temp > 31:	
			fabb_today = fabb_today + fabb_today/4

		#diminuizione dell'irrigazione in base all'umidità del suolo
		if soil_hum > 59 and soil_hum < 71:
			fabb_today = fabb_today - fabb_today/10
		elif soil_hum > 70 and soil_hum < 81:
			fabb_today = fabb_today - fabb_today/8
		elif soil_hum > 80:
			fabb_today = fabb_today - fabb_today/6

		#calcolo quantità d'acqua risparmiata
		if float(expected_fabb - fabb_today) > 0:
			saved_water = float(expected_fabb - fabb_today) 
		else:
			saved_water = 0
		
		saved_water = round(saved_water * mq_field, 2)
		fabb_today = round(fabb_today * mq_field, 2)
		
		saved_water_fields.append(saved_water)
		
		#invio request agli irrigatori IoT
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
	print("quantità d'acqua risparmiata oggi: " + str(total_water_saved_today))

def lambda_handler(event, context):
	process_data()
    
    
