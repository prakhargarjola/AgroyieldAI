import requests

FALLBACK_WEATHER = {
    "temp_avg": 28,
    "temp_max": 35,
    "temp_min": 20,
    "humidity": 60,
    "rainfall": 120,
    "source": "fallback"
}

API_KEY = "212cf88a35df9361001a127c1918a095"

def get_weather_data(district, year=None):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={district},IN&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        if response.status_code != 200 or "main" not in data:
            return FALLBACK_WEATHER
        main = data["main"]
        rainfall = 0.0
        if "rain" in data and "1h" in data["rain"]:
            rainfall = data["rain"]["1h"]
        elif "rain" in data and "3h" in data["rain"]:
            rainfall = data["rain"]["3h"]
        return {
            "temp_avg": round((main["temp"] + main["feels_like"]) / 2, 2),
            "temp_max": main["temp_max"],
            "temp_min": main["temp_min"],
            "humidity": main["humidity"],
            "rainfall": rainfall,
            "source": "openweather"
        }
    except:
        return FALLBACK_WEATHER
