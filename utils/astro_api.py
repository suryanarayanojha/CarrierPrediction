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
    BASE_URL = ASTRO_API_BASE_URL  # Use the URL from config
    MAX_RETRIES = 3  # Reduced from 5
    RETRY_DELAY = 2  # Reduced from 5
    CACHE_DIR = Path("cache")
    CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
    REQUEST_TIMEOUT = 5  # 5 seconds timeout for API requests
    
    # Career significators for each planet
    CAREER_SIGNIFICATORS = {
        "Sun": ["Leadership", "Government", "Administration", "Politics"],
        "Moon": ["Psychology", "Counseling", "Healthcare", "Education"],
        "Mars": ["Engineering", "Military", "Sports", "Law Enforcement"],
        "Mercury": ["Business", "Communication", "Technology", "Writing"],
        "Jupiter": ["Teaching", "Law", "Finance", "Consulting"],
        "Venus": ["Arts", "Entertainment", "Fashion", "Design"],
        "Saturn": ["Science", "Research", "Construction", "Manufacturing"],
        "Rahu": ["Innovation", "Technology", "Entrepreneurship", "Media"],
        "Ketu": ["Spirituality", "Research", "Analysis", "Investigation"]
    }
    
    # House significations for career
    HOUSE_SIGNIFICATIONS = {
        1: ["Self-employment", "Entrepreneurship", "Leadership"],
        2: ["Finance", "Banking", "Accounting"],
        3: ["Communication", "Media", "Writing"],
        4: ["Real Estate", "Agriculture", "Property"],
        5: ["Education", "Entertainment", "Creativity"],
        6: ["Healthcare", "Service", "Technical"],
        7: ["Partnership", "Consulting", "Diplomacy"],
        8: ["Research", "Investigation", "Analysis"],
        9: ["Teaching", "Law", "Philosophy"],
        10: ["Career", "Profession", "Business"],
        11: ["Technology", "Innovation", "Networking"],
        12: ["Spirituality", "Research", "Analysis"]
    }
    
    @staticmethod
    def _get_cache_key(endpoint: str, payload: str) -> str:
        """Generate a cache key from endpoint and payload"""
        key = f"{endpoint}_{payload}"
        return hashlib.md5(key.encode()).hexdigest()
    
    @staticmethod
    def _get_cached_response(cache_key: str) -> Union[Dict[str, Any], None]:
        """Get cached response if available and not expired"""
        if not AstroAPI.CACHE_DIR.exists():
            return None
            
        cache_file = AstroAPI.CACHE_DIR / f"{cache_key}.pkl"
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                if time.time() - cache_data['timestamp'] < AstroAPI.CACHE_EXPIRY:
                    return cache_data['data']
        except:
            pass
        return None
    
    @staticmethod
    def _save_to_cache(cache_key: str, data: Dict[str, Any]):
        """Save response to cache"""
        if not AstroAPI.CACHE_DIR.exists():
            AstroAPI.CACHE_DIR.mkdir(parents=True)
            
        cache_file = AstroAPI.CACHE_DIR / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'timestamp': time.time(),
                    'data': data
                }, f)
        except:
            pass
    
    @staticmethod
    def _make_api_request(endpoint: str, payload: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Make API request with retry logic for rate limiting and caching
        """
        if not ASTRO_API_KEY:
            raise ValueError("ASTRO_API_KEY is not set. Please check your .env file.")

        # Try to get from cache first
        cache_key = AstroAPI._get_cache_key(endpoint, payload)
        cached_response = AstroAPI._get_cached_response(cache_key)
        if cached_response:
            return cached_response
            
        for attempt in range(AstroAPI.MAX_RETRIES):
            try:
                response = requests.request(
                    "POST",
                    f"{AstroAPI.BASE_URL}/{endpoint}",
                    headers=headers,
                    data=payload,
                    timeout=AstroAPI.REQUEST_TIMEOUT
                )
                
                if response.status_code == 429:  # Rate limit
                    if attempt < AstroAPI.MAX_RETRIES - 1:
                        delay = AstroAPI.RETRY_DELAY * (2 ** attempt) + (random.random() * 2)
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception("Rate limit exceeded after maximum retries")
                
                response.raise_for_status()
                response_data = response.json()
                
                if response_data.get("statusCode") != 200:
                    error_msg = response_data.get("message", "Unknown error")
                    raise Exception(f"API error: {error_msg}")
                
                # Cache successful response
                AstroAPI._save_to_cache(cache_key, response_data)
                return response_data
                
            except requests.exceptions.Timeout:
                if attempt == AstroAPI.MAX_RETRIES - 1:
                    raise Exception("API request timed out after maximum retries")
                time.sleep(AstroAPI.RETRY_DELAY * (2 ** attempt))
            except requests.exceptions.RequestException as e:
                if attempt == AstroAPI.MAX_RETRIES - 1:
                    raise Exception(f"API request failed after {AstroAPI.MAX_RETRIES} attempts: {str(e)}")
                time.sleep(AstroAPI.RETRY_DELAY * (2 ** attempt))
        
        raise Exception("API request failed after all retries")
    
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
    def get_planet_positions(birth_chart_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Convert API birth chart data to planet positions format and calculate career significations
        """
        planet_positions = {}
        career_significations = {}
        
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
                
                # Get career significations
                career_options = []
                if planet_name in AstroAPI.CAREER_SIGNIFICATORS:
                    career_options.extend(AstroAPI.CAREER_SIGNIFICATORS[planet_name])
                if house in AstroAPI.HOUSE_SIGNIFICATIONS:
                    career_options.extend(AstroAPI.HOUSE_SIGNIFICATIONS[house])
                
                planet_positions[planet_mapping[planet_name]] = {
                    'house': house,
                    'sign': sign,
                    'longitude': longitude,
                    'career_options': list(set(career_options))  # Remove duplicates
                }
                
                # Add to career significations
                for career in career_options:
                    if career not in career_significations:
                        career_significations[career] = 0
                    career_significations[career] += 1
        
        # Add career significations to the result
        planet_positions['career_significations'] = career_significations
        
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