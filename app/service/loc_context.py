import requests
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather_info_by_lat_lng(lat: float, lng: float, lang: str = "kr") -> dict:
    try:
        apikey = os.getenv("OPENWEATHERMAP_API_KEY")
        
        if not apikey:
            raise HTTPException(
                status_code=500,
                detail="Weather API key not found in environment variables."
            )
        
        api_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={apikey}&lang={lang}&units=metric"
        
        result = requests.get(api_url)

        if result.status_code != 200:
            raise HTTPException(
                status_code=result.status_code,
                detail=f"Weather API Error: {result.text}",
            )

        return result.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather service error: {str(e)}")
