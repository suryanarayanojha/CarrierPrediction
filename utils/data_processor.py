import pandas as pd

class DataProcessor:
    @staticmethod
    def create_feature_dict(planet_positions):
        """Convert form input to feature dictionary"""
        features = {}
        for planet, data in planet_positions.items():
            features[f'{planet}_house'] = data['house']
            features[f'{planet}_sign'] = data['sign']
        return features

    @staticmethod
    def prepare_visualization_data(confidence_scores):
        """Prepare data for visualization"""
        careers = list(confidence_scores.keys())
        scores = list(confidence_scores.values())
        return careers, scores
