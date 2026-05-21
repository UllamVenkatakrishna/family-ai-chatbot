import requests
from datetime import date, timedelta


def get_coordinates(city):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(geo_url, params=params)
    data = response.json()

    if "results" not in data:
        return None

    location = data["results"][0]

    return {
        "name": location["name"],
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"]
    }


def get_weather(city):
    location = get_coordinates(city)

    if location is None:
        return f"Sorry, I could not find weather for {city}."

    latitude = location["latitude"]
    longitude = location["longitude"]

    today = date.today()
    past_start = today - timedelta(days=5)
    future_end = today + timedelta(days=5)

    # Current + upcoming 5 days
    forecast_url = "https://api.open-meteo.com/v1/forecast"

    forecast_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "start_date": str(today),
        "end_date": str(future_end),
        "timezone": "auto"
    }

    forecast_response = requests.get(forecast_url, params=forecast_params)
    forecast_data = forecast_response.json()

    # Past 5 days historical weather
    archive_url = "https://archive-api.open-meteo.com/v1/archive"

    archive_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "start_date": str(past_start),
        "end_date": str(today - timedelta(days=1)),
        "timezone": "auto"
    }

    archive_response = requests.get(archive_url, params=archive_params)
    archive_data = archive_response.json()

    current = forecast_data["current"]
    forecast_daily = forecast_data["daily"]
    archive_daily = archive_data["daily"]

    result = f"""
Weather report for {location["name"]}, {location["country"]}

CURRENT WEATHER:
Temperature: {current["temperature_2m"]}°C
Humidity: {current["relative_humidity_2m"]}%
Rain: {current["precipitation"]} mm
Wind: {current["wind_speed_10m"]} km/h


LAST 5 DAYS:
"""

    for i in range(len(archive_daily["time"])):
        result += f"""
{archive_daily["time"][i]}:
Max: {archive_daily["temperature_2m_max"][i]}°C
Min: {archive_daily["temperature_2m_min"][i]}°C
Rain: {archive_daily["precipitation_sum"][i]} mm
Wind: {archive_daily["wind_speed_10m_max"][i]} km/h
"""

    result += """

TODAY + UPCOMING 5 DAYS:
"""

    for i in range(len(forecast_daily["time"])):
        result += f"""
{forecast_daily["time"][i]}:
Max: {forecast_daily["temperature_2m_max"][i]}°C
Min: {forecast_daily["temperature_2m_min"][i]}°C
Rain: {forecast_daily["precipitation_sum"][i]} mm
Wind: {forecast_daily["wind_speed_10m_max"][i]} km/h
"""

    return result