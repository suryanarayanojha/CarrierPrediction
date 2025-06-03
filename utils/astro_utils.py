import ephem
import datetime
import pytz
from typing import Dict, Tuple
import math

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
        return ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

    @staticmethod
    def calculate_ayanamsa(jd):
        """Calculate ayanamsa (precession of equinoxes)"""
        t = (jd - 2451545.0) / 36525.0
        ayanamsa = 23.85 + 0.0137 * t
        return ayanamsa

    @staticmethod
    def calculate_lagna(birth_datetime, latitude, longitude):
        """Calculate Lagna (Ascendant)"""
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        observer.date = birth_datetime
        
        # Calculate sidereal time
        sidereal_time = observer.sidereal_time()
        
        # Convert to degrees
        lst_degrees = math.degrees(float(sidereal_time))
        
        # Calculate Lagna
        ayanamsa = AstroUtils.calculate_ayanamsa(ephem.julian_date(birth_datetime))
        lagna = (lst_degrees + longitude - ayanamsa) % 360
        
        # Convert to zodiac sign (0-11)
        sign = int(lagna / 30)
        
        return sign

    @staticmethod
    def calculate_planet_positions(birth_date: datetime.date, birth_time: datetime.time, 
                                 latitude: float, longitude: float) -> Tuple[Dict[str, Dict[str, int]], int]:
        """
        Calculate planetary positions based on birth details
        Returns a tuple of (planet_positions dictionary, lagna_sign)
        """
        # Create observer for the birth location
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        
        # Combine date and time
        birth_datetime = datetime.datetime.combine(birth_date, birth_time)
        observer.date = birth_datetime
        
        # Calculate Lagna
        lagna_sign = AstroUtils.calculate_lagna(birth_datetime, latitude, longitude)
        
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
        
        # Calculate Rahu and Ketu positions
        moon = ephem.Moon()
        moon.compute(observer)
        moon_longitude = math.degrees(float(moon.hlon))
        rahu_longitude = (moon_longitude + 180) % 360
        ketu_longitude = (moon_longitude + 180) % 360
        
        # Add Rahu and Ketu
        planets['Rahu'] = {'longitude': rahu_longitude}
        planets['Ketu'] = {'longitude': ketu_longitude}
        
        for planet_name, planet in planets.items():
            if planet_name in ['Rahu', 'Ketu']:
                longitude = planet['longitude']
            else:
                planet.compute(observer)
                longitude = math.degrees(float(planet.hlon))
            
            # Convert longitude to zodiac sign (0-11)
            sign = int(longitude / 30)
            
            # Calculate house based on Lagna
            house = ((sign - lagna_sign) % 12) + 1
            
            planet_positions[planet_name] = {
                'house': house,
                'sign': sign,
                'longitude': longitude
            }
        
        return planet_positions, lagna_sign

    @staticmethod
    def create_lagna_chart(planet_positions: Dict[str, Dict[str, int]], lagna_sign: int) -> str:
        """Create a 12th house Lagna chart visualization"""
        zodiac_signs = AstroUtils.get_zodiac_signs()
        houses = AstroUtils.get_houses()
        
        # Create the chart structure
        chart = []
        chart.append("=" * 50)
        chart.append("12th HOUSE LAGNA CHART")
        chart.append("=" * 50)
        
        # Create house rows
        for house in houses:
            # Calculate the sign for this house
            sign_num = (lagna_sign + house - 1) % 12
            sign_name = zodiac_signs[sign_num]
            
            # Find planets in this house
            planets_in_house = []
            for planet, pos in planet_positions.items():
                if pos['house'] == house:
                    planets_in_house.append(planet)
            
            # Format the house row
            house_row = f"House {house:2d} ({sign_name:10s}): {' '.join(planets_in_house)}"
            chart.append(house_row)
        
        chart.append("=" * 50)
        return "\n".join(chart)

    @staticmethod
    def get_planet_details(planet_positions: Dict[str, Dict[str, int]], lagna_sign: int) -> str:
        """Generate a detailed description of planetary positions"""
        details = []
        zodiac_signs = AstroUtils.get_zodiac_signs()
        
        # Add Lagna (Ascendant) information
        lagna_sign_name = zodiac_signs[lagna_sign]
        details.append(f"Lagna (Ascendant): {lagna_sign_name}")
        details.append("\nPlanetary Positions:")
        
        for planet, position in planet_positions.items():
            sign = zodiac_signs[position['sign']]
            house = position['house']
            longitude = position['longitude']
            degrees = int(longitude % 30)
            minutes = int((longitude % 1) * 60)
            details.append(f"{planet}: {sign} {degrees}° {minutes}' (House {house})")
        
        # Add Lagna Chart
        details.append("\n" + AstroUtils.create_lagna_chart(planet_positions, lagna_sign))
        
        return "\n".join(details)

    @staticmethod
    def get_career_insights(planet_positions: Dict[str, Dict[str, int]]) -> str:
        """Generate career insights based on planetary positions"""
        insights = []
        zodiac_signs = AstroUtils.get_zodiac_signs()
        
        # Analyze teaching potential
        if (planet_positions['Jupiter']['house'] in [2, 5, 9] or 
            planet_positions['Mercury']['house'] in [2, 5, 9]):
            insights.append("Strong potential for teaching and education:")
            if planet_positions['Jupiter']['house'] in [2, 5, 9]:
                insights.append("- Natural teaching abilities")
                insights.append("- Good at explaining complex concepts")
            if planet_positions['Mercury']['house'] in [2, 5, 9]:
                insights.append("- Excellent communication skills")
                insights.append("- Ability to adapt teaching methods")
        
        # Analyze research potential
        if (planet_positions['Saturn']['house'] in [3, 6, 9] or 
            planet_positions['Mars']['house'] in [3, 6, 9]):
            insights.append("\nStrong research capabilities:")
            if planet_positions['Saturn']['house'] in [3, 6, 9]:
                insights.append("- Methodical approach to research")
                insights.append("- Attention to detail")
            if planet_positions['Mars']['house'] in [3, 6, 9]:
                insights.append("- Innovative thinking")
                insights.append("- Problem-solving abilities")
        
        # Analyze leadership potential
        if (planet_positions['Sun']['house'] in [1, 5, 9] or 
            planet_positions['Mars']['house'] in [1, 5, 9]):
            insights.append("\nLeadership qualities:")
            insights.append("- Natural leadership abilities")
            insights.append("- Good at managing teams")
            insights.append("- Decision-making skills")
        
        return "\n".join(insights)
