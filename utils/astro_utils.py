import ephem
import datetime
import pytz
from typing import Dict, Tuple

class AstroUtils:
    @staticmethod
    def get_zodiac_signs():
        return [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 
            'Leo', 'Virgo', 'Libra', 'Scorpio', 
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]

    @staticmethod
    def get_houses():
        return list(range(1, 13))  # 1 to 12 houses

    @staticmethod
    def get_planets():
        return ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

    @staticmethod
    def validate_inputs(planet_positions):
        """Validate astrological input data"""
        is_valid = True
        message = ""
        
        for planet, data in planet_positions.items():
            if data['house'] not in range(1, 13):
                is_valid = False
                message = f"Invalid house position for {planet}"
                break
                
            if data['sign'] not in range(12):
                is_valid = False
                message = f"Invalid zodiac sign for {planet}"
                break
                
        return is_valid, message

    @staticmethod
    def calculate_planet_positions(birth_date: datetime.date, birth_time: datetime.time, 
                                 latitude: float, longitude: float) -> Dict[str, Dict[str, int]]:
        """
        Calculate planetary positions based on birth details
        Returns a dictionary with planet positions in houses and signs
        """
        # Create observer for the birth location
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        
        # Combine date and time
        birth_datetime = datetime.datetime.combine(birth_date, birth_time)
        observer.date = birth_datetime
        
        # Initialize planet positions
        planet_positions = {}
        
        # Calculate positions for each planet
        planets = {
            'Sun': ephem.Sun(),
            'Moon': ephem.Moon(),
            'Mars': ephem.Mars(),
            'Mercury': ephem.Mercury(),
            'Jupiter': ephem.Jupiter(),
            'Venus': ephem.Venus(),
            'Saturn': ephem.Saturn()
        }
        
        for planet_name, planet in planets.items():
            # Calculate planet position
            planet.compute(observer)
            
            # Convert longitude to zodiac sign (0-11)
            sign = int(planet.hlon / 30)
            
            # Calculate house (simplified calculation)
            # This is a basic calculation and might need refinement
            house = int((planet.hlon - observer.sidereal_time() * 15) / 30) % 12 + 1
            
            planet_positions[planet_name] = {
                'house': house,
                'sign': sign
            }
        
        return planet_positions

    @staticmethod
    def get_planet_details(planet_positions: Dict[str, Dict[str, int]]) -> str:
        """Generate a detailed description of planetary positions"""
        details = []
        zodiac_signs = AstroUtils.get_zodiac_signs()
        
        for planet, position in planet_positions.items():
            sign = zodiac_signs[position['sign']]
            house = position['house']
            details.append(f"{planet} is in {sign} (House {house})")
        
        return "\n".join(details)
