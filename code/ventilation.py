import boto3
import requests
from config import DefaultConfig

def get_weather() -> dict:
	CONFIG = DefaultConfig()

	url_today = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + CONFIG.FIELDS_LOC + "%20italia/today?unitGroup=metric&elements=tempmax%2Ctempmin%2Ctemp%2C" + "humidity%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Ccloudcover%2C" + "solarradiation%2Cconditions%2Cet0&include=days%2Ccurrent%2Calerts&" + "key=" + CONFIG.WEATHER_KEY + "&contentType=json"

	weather_today = requests.get(url=url_today).json()
	
	return weather_today
    
def get_iot_info():
	temp = 0
	client = boto3.client('sqs', endpoint_url='http://localhost:4566')
	temp_msg = client.receive_message(QueueUrl='http://localhost:4566/000000000000/ventilation', AttributeNames=['All'], MessageAttributeNames=['date'])
				
	if "Messages" in temp_msg.keys():
		temp = int(temp_msg["Messages"][0]["Body"])
		client.delete_message(QueueUrl='http://localhost:4566/000000000000/ventilation', ReceiptHandle=temp_msg["Messages"][0]["ReceiptHandle"])

	if temp == 0:
		print("\n--- THERE IS A PROBLEM WITH AT LEAST ONE QUEUE ---\n")

	return temp	

def process_data():
	weather_info = get_weather()
	air_temp = get_iot_info()
	
	wea_temp = weather_info["days"][0]["temp"]
	
	if int(air_temp) >= int(wea_temp)*2:
		#r = requests.get('https://enablefans')
		print("requests.get('https://enablefans')")
		print("Outside temp: " + str(wea_temp) + ".\tInside temp: " + str(air_temp) + ".")
	else:
		print("Air temperature is ok.\tOutside temp: " + str(wea_temp) + ".\tInside temp: " + str(air_temp) + ".")
	
def lambda_handler(event, context):
	process_data()
    
    
