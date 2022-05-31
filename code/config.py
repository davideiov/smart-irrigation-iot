import os

class DefaultConfig:
    WEATHER_KEY = os.environ.get("WeatherKey", "")
    EMAIL_FARMER = os.environ.get("EmailFarmer", "farmer@example.com")
    FIELDS_LOC = os.environ.get("FieldsLoc", "nola")
    BOT_USE = os.environ.get("BotUse", "false")
    BOT_TOKEN = os.environ.get("BotToken", "")
    BOT_ID = os.environ.get("BotId", "")
