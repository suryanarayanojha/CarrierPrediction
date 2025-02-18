import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class CareerPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.career_options = ['Engineering', 'Management', 'IT', 'Medical']
        
    def preprocess_features(self, data):
        """Convert astrological data to numerical features"""
        features = []
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            features.append(data[f'{planet}_house'])
            features.append(data[f'{planet}_sign'])
        return features

    def train(self, X, y):
        """Train the model with preprocessed data"""
        self.model.fit(X, self.label_encoder.fit_transform(y))

    def predict(self, features):
        """Predict career based on astrological features"""
        features_processed = self.preprocess_features(features)
        prediction = self.model.predict([features_processed])
        probabilities = self.model.predict_proba([features_processed])[0]
        
        predicted_career = self.label_encoder.inverse_transform(prediction)[0]
        confidence_scores = dict(zip(self.career_options, probabilities))
        
        return predicted_career, confidence_scores
