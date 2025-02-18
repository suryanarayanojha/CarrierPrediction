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
