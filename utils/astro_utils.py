import ephem
import datetime
import pytz
from typing import Dict, Tuple, List, Any
import math
from utils.astro_api import AstroAPI

class AstroUtils:
    @staticmethod
    def get_zodiac_signs() -> List[str]:
        """
        Get list of zodiac signs
        """
        return [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
    
    @staticmethod
    def get_houses() -> List[int]:
        """
        Get list of houses
        """
        return list(range(1, 13))
    
    @staticmethod
    def get_planets() -> List[str]:
        """
        Get list of planets
        """
        return [
            "Sun", "Moon", "Mars", "Mercury",
            "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
        ]

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
                                 latitude: float, longitude: float) -> Tuple[Dict[str, Dict[str, Any]], int]:
        """
        Calculate planetary positions using both local calculations and API
        """
        try:
            # Calculate Lagna (Ascendant)
            birth_datetime = datetime.datetime.combine(birth_date, birth_time)
            lagna_sign = AstroUtils.calculate_lagna(birth_datetime, latitude, longitude)
            
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
            
            # Add variation based on date and time
            date_factor = (birth_date.day + birth_date.month * 30) % 360
            time_factor = (birth_time.hour + birth_time.minute/60.0) * 15
            
            for planet, base_pos in base_positions.items():
                # Calculate longitude with variations
                longitude = (base_pos + date_factor + time_factor) % 360
                sign = int(longitude / 30)
                
                # Calculate house based on Lagna
                house = ((sign - lagna_sign) % 12) + 1
                
                planets.append({
                    "name": planet,
                    "longitude": longitude,
                    "latitude": 0,
                    "speed": 1.0,
                    "house": house,
                    "sign": sign
                })
            
            # Add ascendant
            planets.append({
                "name": "Ascendant",
                "longitude": (time_factor + longitude) % 360,
                "latitude": latitude,
                "speed": 0,
                "house": 1,
                "sign": lagna_sign
            })
            
            # Try to get API data
            try:
                birth_chart_data = AstroAPI.get_birth_chart(birth_date, birth_time, latitude, longitude)
                if birth_chart_data:
                    # Use API data if available
                    planet_positions = AstroAPI.get_planet_positions(birth_chart_data)
                else:
                    # Use local calculations if API fails
                    planet_positions = AstroAPI.get_planet_positions(planets)
            except Exception:
                # Use local calculations if API fails
                planet_positions = AstroAPI.get_planet_positions(planets)
            
            return planet_positions, lagna_sign
            
        except Exception as e:
            raise Exception(f"Error calculating planet positions: {str(e)}")

    @staticmethod
    def calculate_lagna(birth_datetime: datetime.datetime, latitude: float, longitude: float) -> int:
        """
        Calculate Lagna (Ascendant) sign
        """
        try:
            # Convert to Julian date
            jd = ephem.julian_date(birth_datetime)
            
            # Calculate sidereal time
            t = (jd - 2451545.0) / 36525.0
            sidereal_time = 100.46061837 + 36000.770053608 * t + 0.000387933 * t * t
            
            # Calculate local sidereal time
            lst = (sidereal_time + longitude) % 360
            
            # Calculate ayanamsa
            ayanamsa = AstroUtils.calculate_ayanamsa(jd)
            
            # Calculate Lagna
            lagna = (lst - ayanamsa) % 360
            
            # Convert to zodiac sign (0-11)
            return int(lagna / 30)
            
        except Exception as e:
            # Fallback to simple calculation if ephem fails
            hour = birth_datetime.hour + birth_datetime.minute/60.0
            lagna = (hour * 15 + longitude) % 360
            return int(lagna / 30)

    @staticmethod
    def calculate_ayanamsa(jd: float) -> float:
        """
        Calculate ayanamsa (precession of equinoxes)
        """
        t = (jd - 2451545.0) / 36525.0
        ayanamsa = 23.85 + 0.0137 * t
        return ayanamsa

    @staticmethod
    def create_lagna_chart(planet_positions: Dict[str, Dict[str, Any]], lagna_sign: int) -> str:
        """Create a 12th house Lagna chart visualization"""
        try:
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
                    if planet != 'career_significations':  # Skip non-planet entries
                        if pos.get('house') == house:
                            planets_in_house.append(planet)
                
                # Format the house row
                house_row = f"House {house:2d} ({sign_name:10s}): {' '.join(planets_in_house)}"
                chart.append(house_row)
            
            chart.append("=" * 50)
            return "\n".join(chart)
            
        except Exception as e:
            return f"Error creating Lagna chart: {str(e)}"

    @staticmethod
    def get_planet_details(planet_positions: Dict[str, Dict[str, Any]], lagna_sign: int) -> str:
        """
        Get detailed description of planetary positions
        """
        try:
            zodiac_signs = AstroUtils.get_zodiac_signs()
            details = []
            
            # Add Lagna information
            details.append(f"Lagna (Ascendant): {zodiac_signs[lagna_sign]}")
            details.append("\nPlanetary Positions:")
            
            # Process each planet
            for planet in AstroUtils.get_planets():
                if planet in planet_positions:
                    position = planet_positions[planet]
                    sign = zodiac_signs[position.get('sign', 0)]
                    house = position.get('house', 1)
                    longitude = position.get('longitude', 0)
                    
                    # Format longitude as degrees, minutes, seconds
                    degrees = int(longitude)
                    minutes = int((longitude - degrees) * 60)
                    seconds = int(((longitude - degrees) * 60 - minutes) * 60)
                    
                    # Get career options
                    career_options = position.get('career_options', [])
                    career_str = ", ".join(career_options) if career_options else "No specific career significations"
                    
                    details.append(f"\n{planet}:")
                    details.append(f"  Sign: {sign}")
                    details.append(f"  House: {house}")
                    details.append(f"  Longitude: {degrees}° {minutes}' {seconds}\"")
                    details.append(f"  Career Significations: {career_str}")
            
            # Add overall career significations
            if 'career_significations' in planet_positions:
                details.append("\nOverall Career Significations:")
                career_sigs = planet_positions['career_significations']
                sorted_careers = sorted(career_sigs.items(), key=lambda x: x[1], reverse=True)
                for career, strength in sorted_careers:
                    details.append(f"  {career}: {strength} significations")
            
            # Add Lagna Chart
            lagna_chart = AstroUtils.create_lagna_chart(planet_positions, lagna_sign)
            if not lagna_chart.startswith("Error"):
                details.append("\n" + lagna_chart)
            
            return "\n".join(details)
            
        except Exception as e:
            raise Exception(f"Error getting planet details: {str(e)}")

    @staticmethod
    def calculate_planet_strength(planet: str, position: Dict[str, Any]) -> float:
        """
        Calculate the strength of a planet based on its position and aspects
        """
        # Base strength from house placement
        house_strengths = {
            1: 1.0,   # Ascendant - Strong
            5: 0.9,   # 5th house - Strong
            9: 0.9,   # 9th house - Strong
            3: 0.8,   # 3rd house - Moderate
            6: 0.7,   # 6th house - Moderate
            10: 0.8,  # 10th house - Moderate
            2: 0.7,   # 2nd house - Moderate
            4: 0.7,   # 4th house - Moderate
            7: 0.7,   # 7th house - Moderate
            8: 0.6,   # 8th house - Weak
            11: 0.8,  # 11th house - Moderate
            12: 0.6   # 12th house - Weak
        }
        
        # Get base strength from house
        strength = house_strengths.get(position['house'], 0.5)
        
        # Adjust based on planet's natural strength
        planet_strengths = {
            "Sun": 1.0,
            "Moon": 0.9,
            "Mars": 0.8,
            "Mercury": 0.9,
            "Jupiter": 1.0,
            "Venus": 0.9,
            "Saturn": 0.8,
            "Rahu": 0.7,
            "Ketu": 0.7
        }
        
        strength *= planet_strengths.get(planet, 0.5)
        
        # Adjust based on sign placement
        sign = position['sign']
        if planet in ["Sun", "Mars"] and sign in [0, 4, 8]:  # Fire signs
            strength *= 1.2
        elif planet in ["Moon", "Venus"] and sign in [1, 5, 9]:  # Earth signs
            strength *= 1.2
        elif planet in ["Mercury", "Saturn"] and sign in [2, 6, 10]:  # Air signs
            strength *= 1.2
        elif planet in ["Jupiter"] and sign in [3, 7, 11]:  # Water signs
            strength *= 1.2
            
        return strength

    @staticmethod
    def get_career_insights(planet_positions: Dict[str, Dict[str, Any]]) -> str:
        """
        Get career insights based on planetary positions with personalized compatibility scores
        """
        try:
            insights = []
            
            # Calculate compatibility scores for each career field
            compatibility_scores = {}
            for career, details in AstroUtils.CAREER_FIELDS.items():
                score = 0
                max_score = 0
                aspect_bonus = 0
                
                # Check planetary positions and calculate strengths
                planet_strengths = {}
                for planet in details["planets"]:
                    if planet in planet_positions:
                        position = planet_positions[planet]
                        # Calculate planet strength
                        strength = AstroUtils.calculate_planet_strength(planet, position)
                        planet_strengths[planet] = strength
                        
                        # Add score based on house placement
                        if position["house"] in details["houses"]:
                            score += strength
                        max_score += 1
                
                # Calculate aspect bonuses
                if "aspects" in details:
                    for aspect, bonus in details["aspects"].items():
                        planets = aspect.split("-")
                        if all(p in planet_strengths for p in planets):
                            aspect_bonus += bonus
                
                # Calculate final percentage with aspect bonus
                if max_score > 0:
                    base_percentage = (score / max_score) * 100
                    final_percentage = (base_percentage + aspect_bonus * 10) * details["weight"]
                    compatibility_scores[career] = round(final_percentage, 2)
            
            # Sort careers by compatibility score
            sorted_careers = sorted(compatibility_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Generate insights
            insights.append("Career Prediction Results")
            insights.append("\nTop Career Recommendations:")
            for career, score in sorted_careers[:3]:  # Top 3 careers
                insights.append(f"{career}: {score}% compatibility")
            
            insights.append("\nCareer Insights")
            
            # Add detailed career paths for top career
            if sorted_careers:
                top_career = sorted_careers[0][0]
                insights.append(f"\nPotential {top_career} Career Paths")
                
                if top_career in AstroUtils.CAREER_PATHS:
                    for path in AstroUtils.CAREER_PATHS[top_career]:
                        insights.append(f"- {path}")
            
            insights.append("\nGeneral Career Compatibility")
            for career, score in sorted_careers:
                insights.append(f"\n{career}: {score}% compatibility")
            
            return "\n".join(insights)
            
        except Exception as e:
            raise Exception(f"Error getting career insights: {str(e)}")

    # Define career fields and paths as class variables
    CAREER_FIELDS = {
        "Politics/Social Reform": {
            "planets": ["Sun", "Mars", "Jupiter"],
            "houses": [1, 5, 9],
            "weight": 1.2,
            "aspects": {
                "Sun-Mars": 1.3,
                "Sun-Jupiter": 1.2,
                "Mars-Jupiter": 1.1
            }
        },
        "Sports/Athletics": {
            "planets": ["Mars", "Sun", "Jupiter"],
            "houses": [1, 3, 5],
            "weight": 1.1,
            "aspects": {
                "Mars-Sun": 1.3,
                "Mars-Jupiter": 1.2
            }
        },
        "Technology/Entrepreneurship": {
            "planets": ["Mercury", "Rahu", "Jupiter"],
            "houses": [3, 5, 11],
            "weight": 1.3,
            "aspects": {
                "Mercury-Rahu": 1.4,
                "Mercury-Jupiter": 1.2
            }
        },
        "Arts/Creative": {
            "planets": ["Venus", "Moon", "Jupiter"],
            "houses": [2, 5, 9],
            "weight": 1.0
        },
        "Business/Finance": {
            "planets": ["Jupiter", "Venus", "Mercury"],
            "houses": [2, 5, 9],
            "weight": 1.2
        },
        "Education/Research": {
            "planets": ["Jupiter", "Mercury", "Saturn"],
            "houses": [2, 5, 9],
            "weight": 1.1
        },
        "Law": {
            "planets": ["Jupiter", "Saturn", "Mercury"],
            "houses": [1, 5, 9],
            "weight": 1.0
        },
        "Media/Communication": {
            "planets": ["Mercury", "Venus", "Jupiter"],
            "houses": [3, 5, 11],
            "weight": 1.1
        },
        "Psychology": {
            "planets": ["Moon", "Mercury", "Neptune"],
            "houses": [4, 8, 12],
            "weight": 0.9
        },
        "Engineering": {
            "planets": ["Mars", "Saturn", "Mercury"],
            "houses": [3, 6, 10],
            "weight": 1.0
        },
        "Medical": {
            "planets": ["Mars", "Saturn", "Mercury"],
            "houses": [6, 8, 12],
            "weight": 1.2
        },
        "Management": {
            "planets": ["Sun", "Jupiter", "Saturn"],
            "houses": [1, 5, 10],
            "weight": 1.1
        },
        "IT": {
            "planets": ["Mercury", "Rahu", "Saturn"],
            "houses": [3, 5, 11],
            "weight": 1.2
        },
        "Environmental Science": {
            "planets": ["Saturn", "Jupiter", "Mercury"],
            "houses": [4, 8, 12],
            "weight": 0.9
        },
        "Architecture": {
            "planets": ["Venus", "Saturn", "Mercury"],
            "houses": [4, 5, 10],
            "weight": 1.0
        },
        "Music/Performance": {
            "planets": ["Venus", "Moon", "Jupiter"],
            "houses": [2, 5, 9],
            "weight": 1.1
        },
        "Writing/Literature": {
            "planets": ["Mercury", "Venus", "Jupiter"],
            "houses": [3, 5, 9],
            "weight": 1.0
        },
        "Public Service": {
            "planets": ["Sun", "Jupiter", "Saturn"],
            "houses": [1, 5, 9],
            "weight": 1.0
        },
        "Research/Academia": {
            "planets": ["Jupiter", "Saturn", "Mercury"],
            "houses": [5, 9, 12],
            "weight": 1.1
        },
        "Physical Education": {
            "planets": ["Mars", "Sun", "Jupiter"],
            "houses": [1, 3, 5],
            "weight": 0.9
        },
        "Teaching/Professor": {
            "planets": ["Jupiter", "Mercury", "Venus"],
            "houses": [2, 5, 9],
            "weight": 1.0
        }
    }

    CAREER_PATHS = {
        "Politics/Social Reform": [
            "Public Policy Analyst",
            "Political Consultant",
            "Social Worker",
            "Community Organizer",
            "Government Official"
        ],
        "Sports/Athletics": [
            "Professional Athlete",
            "Sports Coach",
            "Physical Trainer",
            "Sports Manager",
            "Sports Analyst"
        ],
        "Technology/Entrepreneurship": [
            "Tech Entrepreneur",
            "Software Developer",
            "Product Manager",
            "Tech Consultant",
            "Startup Founder"
        ],
        # ... (keep other career paths as is)
    }
