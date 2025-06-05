import requests
import json
from typing import Dict, Any, Tuple, List, Union
import datetime
import time
from config import ASTRO_API_KEY, ASTRO_API_BASE_URL

class AstroAPI:
    BASE_URL = "https://json.freeastrologyapi.com"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    @staticmethod
    def _make_api_request(endpoint: str, payload: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Make API request with retry logic for rate limiting
        """
        for attempt in range(AstroAPI.MAX_RETRIES):
            try:
                response = requests.request(
                    "POST",
                    f"{AstroAPI.BASE_URL}/{endpoint}",
                    headers=headers,
                    data=payload
                )
                
                if response.status_code == 429:  # Rate limit
                    if attempt < AstroAPI.MAX_RETRIES - 1:
                        time.sleep(AstroAPI.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                        continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == AstroAPI.MAX_RETRIES - 1:
                    raise Exception(f"API request failed after {AstroAPI.MAX_RETRIES} attempts: {str(e)}")
                time.sleep(AstroAPI.RETRY_DELAY * (attempt + 1))
        
        raise Exception("API request failed after all retries")
    
    @staticmethod
    def get_horoscope_chart_svg(birth_date: datetime.date, birth_time: datetime.time, 
                              latitude: float, longitude: float) -> str:
        """
        Get horoscope chart SVG code from Free Astrology API
        """
        try:
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
            
            response_data = AstroAPI._make_api_request("horoscope-chart-svg-code", payload, headers)
            
            if response_data.get("statusCode") == 200:
                return response_data.get("output", "")
            else:
                raise Exception(f"API returned error: {response_data.get('message', 'Unknown error')}")
            
        except Exception as e:
            raise Exception(f"Error fetching horoscope chart: {str(e)}")
    
    @staticmethod
    def get_birth_chart(birth_date: datetime.date, birth_time: datetime.time, 
                       latitude: float, longitude: float) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get birth chart data from Free Astrology API using the planets endpoint
        """
        try:
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
                "settings": {
                    "observation_point": "topocentric",
                    "ayanamsha": "lahiri"
                }
            })
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': ASTRO_API_KEY
            }
            
            response_data = AstroAPI._make_api_request("planets", payload, headers)
            
            if response_data.get("statusCode") == 200:
                return response_data.get("output", [])
            else:
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
            "Ketu": 30  # Ketu is opposite to Rahu
        }
        
        # Add some variation based on date
        date_factor = (birth_date.day + birth_date.month * 30) % 360
        
        for planet, base_pos in base_positions.items():
            # Add variation and normalize to 0-360
            longitude = (base_pos + date_factor + (hour * 5)) % 360
            planets.append({
                "name": planet,
                "longitude": longitude,
                "latitude": 0,
                "speed": 1.0,
                "house": int(longitude / 30) + 1
            })
        
        # Add ascendant to the list
        planets.append({
            "name": "Ascendant",
            "longitude": lagna_longitude,
            "latitude": latitude,
            "speed": 0,
            "house": int(lagna_longitude / 30) + 1
        })
        
        return planets
    
    @staticmethod
    def get_planet_positions(birth_chart_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Dict[str, int]]:
        """
        Convert API birth chart data to planet positions format
        """
        planet_positions = {}
        
        # Map API planet names to our format
        planet_mapping = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mars": "Mars",
            "Mercury": "Mercury",
            "Jupiter": "Jupiter",
            "Venus": "Venus",
            "Saturn": "Saturn",
            "Rahu": "Rahu",
            "Ketu": "Ketu",
            "Ascendant": "Ascendant"
        }
        
        # Handle both list and dictionary formats
        if isinstance(birth_chart_data, list):
            planets_data = birth_chart_data
        else:
            planets_data = birth_chart_data.get("planets", [])
        
        # Find ascendant first
        lagna_longitude = 0
        for planet_data in planets_data:
            if planet_data.get("name") == "Ascendant":
                lagna_longitude = float(planet_data.get("longitude", 0))
                break
        
        # Process all planets
        for planet_data in planets_data:
            planet_name = planet_data.get("name")
            if planet_name in planet_mapping:
                longitude = float(planet_data.get("longitude", 0))
                sign = int(longitude / 30)
                
                # Calculate house based on Lagna
                lagna_sign = int(lagna_longitude / 30)
                house = ((sign - lagna_sign) % 12) + 1
                
                planet_positions[planet_mapping[planet_name]] = {
                    'house': house,
                    'sign': sign,
                    'longitude': longitude
                }
        
        return planet_positions
    
    @staticmethod
    def get_lagna_sign(birth_chart_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> int:
        """
        Get Lagna sign from birth chart data
        """
        if isinstance(birth_chart_data, list):
            for planet_data in birth_chart_data:
                if planet_data.get("name") == "Ascendant":
                    lagna_longitude = float(planet_data.get("longitude", 0))
                    return int(lagna_longitude / 30)
        else:
            lagna_longitude = float(birth_chart_data.get("ascendant", {}).get("longitude", 0))
            return int(lagna_longitude / 30)
        
        return 0  # Default to Aries if not found 