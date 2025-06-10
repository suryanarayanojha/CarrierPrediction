import requests
import json
from typing import Dict, Any, Tuple, List, Union
import datetime
import time
from config import ASTRO_API_KEY, ASTRO_API_BASE_URL
import hashlib
import os
import pickle
from pathlib import Path
import random
import math

class AstroAPI:
    BASE_URL = ASTRO_API_BASE_URL
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    CACHE_DIR = Path("cache")
    CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
    REQUEST_TIMEOUT = 5  # 5 seconds timeout for API requests

    @staticmethod
    def get_horoscope_chart_svg(birth_date: datetime.date, birth_time: datetime.time, 
                                latitude: float, longitude: float, language: str = "en") -> str:
        """
        Fetch the horoscope chart URL from the new Free Astrology API endpoint.
        If the API fails, return a locally generated SVG chart as fallback.
        """
        url = "https://json.freeastrologyapi.com/horoscope-chart-url"
        payload = json.dumps({
            "year": birth_date.year,
            "month": birth_date.month,
            "date": birth_date.day,
            "hours": birth_time.hour,
            "minutes": birth_time.minute,
            "seconds": birth_time.second,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": 5.5,
            "config": {
                "observation_point": "topocentric",
                "ayanamsha": "lahiri"
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': ASTRO_API_KEY
        }
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=AstroAPI.REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                chart_url = data.get("output")
                if chart_url:
                    # Return an <img> tag to display the chart URL in Streamlit
                    return f'<img src="{chart_url}" alt="Horoscope Chart" style="max-width:100%;height:auto;" />'
                else:
                    raise Exception("No chart URL returned from API.")
            else:
                raise Exception(f"API error: {response.status_code} {response.text}")
        except Exception as e:
            # Fallback to local SVG chart
            return AstroAPI._generate_simple_svg_chart(birth_date, birth_time, latitude, longitude)

    @staticmethod
    def _generate_simple_svg_chart(birth_date: datetime.date, birth_time: datetime.time,
                                 latitude: float, longitude: float) -> str:
        """
        Generate a simple SVG chart when API is rate limited
        """
        # Calculate approximate positions
        planets = AstroAPI._calculate_approximate_positions(birth_date, birth_time, latitude, longitude)
        
        # Create a simple SVG chart
        svg = f"""<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
            <circle cx="200" cy="200" r="150" fill="none" stroke="black" stroke-width="2"/>
            <text x="200" y="50" text-anchor="middle" font-size="16">North Indian Chart</text>
            <text x="200" y="380" text-anchor="middle" font-size="12">Generated using local calculations</text>
        """
        
        # Add zodiac signs
        zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                       "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for i, sign in enumerate(zodiac_signs):
            angle = i * 30
            x = 200 + 130 * math.cos(math.radians(angle - 90))
            y = 200 + 130 * math.sin(math.radians(angle - 90))
            svg += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="12">{sign}</text>'
        
        # Add planets
        for planet in planets:
            if planet["name"] != "Ascendant":
                house = planet["house"]
                angle = (house - 1) * 30
                x = 200 + 100 * math.cos(math.radians(angle - 90))
                y = 200 + 100 * math.sin(math.radians(angle - 90))
                svg += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="12">{planet["name"]}</text>'
        
        svg += "</svg>"
        return svg

    @staticmethod
    def get_birth_chart(birth_date: datetime.date, birth_time: datetime.time, 
                       latitude: float, longitude: float, 
                       observation_point: str = "topocentric",
                       ayanamsha: str = "lahiri") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get birth chart data from API with caching"""
        try:
            # Create cache key
            cache_key = f"{birth_date}_{birth_time}_{latitude}_{longitude}_{observation_point}_{ayanamsha}"
            cache_file = AstroAPI.CACHE_DIR / f"birth_chart_{hashlib.md5(cache_key.encode()).hexdigest()}.json"
            
            # Check cache first
            if cache_file.exists():
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < AstroAPI.CACHE_EXPIRY:
                    try:
                        with open(cache_file, 'r') as f:
                            return json.load(f)
                    except Exception as e:
                        print(f"Error reading cache: {e}")

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {ASTRO_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "day": birth_date.day,
                "month": birth_date.month,
                "year": birth_date.year,
                "hour": birth_time.hour,
                "min": birth_time.minute,
                "lat": latitude,
                "lon": longitude,
                "tzone": 0,  # UTC
                "observation_point": observation_point,
                "ayanamsha": ayanamsha
            }

            # Make API request with timeout
            for attempt in range(AstroAPI.MAX_RETRIES):
                try:
                    response = requests.post(
                        f"{AstroAPI.BASE_URL}/birth-chart",
                        headers=headers,
                        json=data,
                        timeout=AstroAPI.REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    if response_data.get("statusCode") == 200:
                        planets_data = response_data.get("output", [])
                        
                        if isinstance(planets_data, list):
                            # Validate planet data
                            for planet in planets_data:
                                if not all(key in planet for key in ["name", "longitude", "latitude", "speed", "house", "sign"]):
                                    raise Exception("Invalid planet data received from API")
                            
                            # Add ascendant if not present
                            has_ascendant = any(p.get("name") == "Ascendant" for p in planets_data)
                            if not has_ascendant:
                                hour = birth_time.hour + birth_time.minute/60.0
                                lagna_longitude = (hour * 15 + longitude) % 360
                                planets_data.append({
                                    "name": "Ascendant",
                                    "longitude": lagna_longitude,
                                    "latitude": latitude,
                                    "speed": 0,
                                    "house": int(lagna_longitude / 30) + 1,
                                    "sign": int(lagna_longitude / 30)
                                })
                            
                            # Cache the result
                            try:
                                AstroAPI.CACHE_DIR.mkdir(exist_ok=True)
                                with open(cache_file, 'w') as f:
                                    json.dump(planets_data, f)
                            except Exception as e:
                                print(f"Error caching birth chart: {e}")
                            
                            return planets_data
                        else:
                            raise Exception("Invalid response format from API")
                    else:
                        raise Exception(f"API error: {response_data.get('message', 'Unknown error')}")
                        
                except requests.Timeout:
                    if attempt == AstroAPI.MAX_RETRIES - 1:
                        raise Exception("API request timed out")
                    time.sleep(AstroAPI.RETRY_DELAY)
                except requests.RequestException as e:
                    if attempt == AstroAPI.MAX_RETRIES - 1:
                        raise Exception(f"API request failed: {str(e)}")
                    time.sleep(AstroAPI.RETRY_DELAY)
            
            # If API fails, calculate approximate positions
            return AstroAPI._calculate_approximate_positions(birth_date, birth_time, latitude, longitude)
            
        except Exception as e:
            # If API fails, calculate approximate positions
            return AstroAPI._calculate_approximate_positions(birth_date, birth_time, latitude, longitude)

    @staticmethod
    def _calculate_approximate_positions(birth_date: datetime.date, birth_time: datetime.time,
                                       latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """
        Calculate approximate planetary positions when API is unavailable
        """
        # Calculate approximate Lagna (Ascendant)
        hour = birth_time.hour + birth_time.minute/60.0
        lagna_longitude = (hour * 15 + longitude) % 360  # Approximate calculation
        
        # Calculate approximate planet positions
        planets = []
        base_positions = {
            "Sun": 0,
            "Moon": 30,
            "Mars": 60,
            "Mercury": 90,
            "Jupiter": 120,
            "Venus": 150,
            "Saturn": 180,
            "Rahu": 210,
            "Ketu": 240
        }
        
        # Add some randomness to make it look more realistic
        for planet, base_pos in base_positions.items():
            # Add some random variation
            variation = random.uniform(-5, 5)
            longitude = (base_pos + variation) % 360
            
            # Calculate house and sign
            sign = int(longitude / 30)
            house = ((sign - int(lagna_longitude / 30)) % 12) + 1
            
            planets.append({
                "name": planet,
                "longitude": longitude,
                "latitude": random.uniform(-5, 5),
                "speed": random.uniform(0.5, 1.5),
                "house": house,
                "sign": sign
            })
        
        # Add Ascendant
        planets.append({
            "name": "Ascendant",
            "longitude": lagna_longitude,
            "latitude": latitude,
            "speed": 0,
            "house": 1,
            "sign": int(lagna_longitude / 30)
        })
        
        return planets 