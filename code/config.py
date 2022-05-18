import os

class DefaultConfig:
    WEATHER_KEY = os.environ.get("WeatherKey", "XXXXXXXX")
