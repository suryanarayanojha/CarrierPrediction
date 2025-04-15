import pandas as pd

class DataProcessor:
    @staticmethod
    def create_feature_dict(planet_positions):
        """Convert form input to feature dictionary"""
        features = {}
        
        # If the input is already structured with planet_house and planet_sign keys
        if isinstance(planet_positions, dict) and any(key.endswith('_house') for key in planet_positions.keys()):
            return planet_positions
            
        # Otherwise, convert from the planet:{'house':X, 'sign':Y} format
        for planet, data in planet_positions.items():
            if isinstance(data, dict) and 'house' in data and 'sign' in data:
                features[f'{planet}_house'] = data['house']
                features[f'{planet}_sign'] = data['sign']
        
        return features

    @staticmethod
    def prepare_visualization_data(confidence_scores):
        """Prepare data for visualization"""
        careers = list(confidence_scores.keys())
        scores = list(confidence_scores.values())
        return careers, scores
