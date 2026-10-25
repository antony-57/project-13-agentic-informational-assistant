from schema import AgentState
import requests

def fetch_weather(state: AgentState):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url = "https://api.open-meteo.com/v1/forecast"

    city = state["city_name"]
    forecast_type = state["forecast_type"]

    geo_params = {
        "name": city,
        "language": "english",
        "count": 1,
        "format": "json"
    }
    try:
        coordinates = requests.get(geo_url, params= geo_params)
        coordinates.raise_for_status()

        geo_data = coordinates.json()

    except requests.exceptions.HTTPError as e:
        print(f"API returned an HTTP error: {e}")

    except requests.exceptions.Timeout:
        print("The weather service took too long to respond.")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the weather service.")

    if "results" in geo_data:
        location = geo_data["results"][0]
        country = location.get("country")
        latitude = location.get("latitude")
        longitude = location.get("longitude")

    else:
        return {
        "success": False,
        "tool_result": geo_data,
        "error": geo_data.get(
            "error",
            f"No locations found for '{city}'."
        ),
        "final_response": (
            f"I couldn't find the location '{city}'. "
            "Please check the spelling or try another city."
        )
    }

    weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snowfall",
            73: "Moderate snowfall",
            75: "Heavy snowfall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            97: "Heavy thunderstorm",
            99: "Thunderstorm with heavy hail"
        }

    if forecast_type == "current":
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m", 
                "relative_humidity_2m", 
                "apparent_temperature", 
                "precipitation", 
                "wind_speed_10m", 
                "weather_code", 
                "cloud_cover", 
                "wind_gusts_10m"
            ]
        }

        response = requests.get(forecast_url, params= params)
        response.raise_for_status()

        data = response.json()
        current = data["current"]
        weather_description = weather_codes.get(current["weather_code"],"Unknown weather conditions")

        weather_data = {
                "city": city,
                "country": country,
                "time": current["time"],
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"],
                "feels_like": current["apparent_temperature"],
                "precipitation": current["precipitation"],
                "wind_speed": current["wind_speed_10m"],
                "weather_description": weather_description,
                "cloud_cover": current["cloud_cover"],
                "wind_gusts": current["wind_gusts_10m"]
            }

        return {
                "success": True,
                "tool_result": weather_data
            }

    elif forecast_type == "hourly":
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "temperature_2m", 
                "apparent_temperature", 
                "precipitation_probability", 
                "precipitation", 
                "weather_code", 
                "wind_speed_10m", 
                "relative_humidity_2m", 
                "visibility"
            ]
        }

        response = requests.get(forecast_url, params= params)
        response.raise_for_status()

        data = response.json()
        hourly = data["hourly"]
        
        weather_description = []

        for code in hourly["weather_code"]:
            weather_description.append(weather_codes[code])

        weather_data = {
                "city": city,
                "country": country,
                "time": hourly["time"],
                "temperature": hourly["temperature_2m"],
                "feels_like": hourly["apparent_temperature"],
                "precipitation_probability": hourly["precipitation_probability"],
                "precipitation": hourly["precipitation"],
                "weather_description": weather_description,
                "wind_speed": hourly["wind_speed_10m"],
                "humidity": hourly["relative_humidity_2m"],
                "visibility": hourly["visibility"]
            }

        return {
                "success": True,
                "tool_result": weather_data
            }

    elif forecast_type == "daily":
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_probability_max",
                "precipitation_sum",
                "wind_speed_10m_max",
                "sunrise",
                "sunset"
            ]
        }

        response = requests.get(forecast_url, params= params)
        response.raise_for_status()

        data = response.json()
        daily = data["daily"]
        
        weather_description = []
        
        for code in daily["weather_code"]:
            weather_description.append(weather_codes[code])

        weather_data = {
                "city": city,
                "country": country,
                "dates": daily["time"],
                "weather_description": weather_description,
                "temperature_max": daily["temperature_2m_max"],
                "temperature_min": daily["temperature_2m_min"],
                "feels_like(max)": daily["apparent_temperature_max"],
                "feels_like(min)": daily["apparent_temperature_min"],
                "precipitation_probability_max": daily["precipitation_probability_max"],
                "precipitation_sum": daily["precipitation_sum"],
                "wind_speed": daily["wind_speed_10m_max"],
                "sunrise": daily["sunrise"],
                "sunset": daily["sunset"]
            }

        return {
                "success": True,
                "tool_result": weather_data
            }

    else:
        return {
            "success": False,
            "error": f"Invalid forecast type: '{forecast_type}'."
        }

