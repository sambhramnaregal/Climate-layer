import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

def get_weather(lat, lon):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "direct_radiation_instant",
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"],
        "wind_speed_unit": "ms",
    }
    
    try:
        responses = openmeteo.weather_api(url, params=params)
        
        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        
        # Process current data. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_precipitation = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()
        current_wind_direction_10m = current.Variables(4).Value()
        
        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_direct_radiation_instant = hourly.Variables(0).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        
        hourly_data["direct_radiation_instant"] = hourly_direct_radiation_instant
        
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        
        # Convert dataframe to a list of dicts for JSON serialization, maybe just take head(24) for now or similar
        # Since the user wants to show it, let's return the first 24 hours as an example
        hourly_list = hourly_dataframe.head(24).astype(str).to_dict(orient='records')

        result = {
            "metadata": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude(),
                "elevation": response.Elevation(),
                "utc_offset_seconds": response.UtcOffsetSeconds()
            },
            "current": {
                "time": current.Time(),
                "temperature_2m": current_temperature_2m,
                "relative_humidity_2m": current_relative_humidity_2m,
                "precipitation": current_precipitation,
                "wind_speed_10m": current_wind_speed_10m,
                "wind_direction_10m": current_wind_direction_10m
            },
            "hourly": hourly_list
        }
        
        return result

    except Exception as e:
        return {"error": str(e)}