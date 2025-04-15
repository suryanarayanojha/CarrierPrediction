import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from utils.famous_personalities import FamousPersonalities

class CareerPredictor:
    def __init__(self):
        try:
            self.model = RandomForestClassifier(n_estimators=300, random_state=42, max_depth=15)
            self.label_encoder = LabelEncoder()
            self.career_options = [
                'Physics/Science', 'Technology/Entrepreneurship', 'Politics/Social Reform',
                'Engineering', 'Management', 'IT', 'Medical', 'Arts/Creative',
                'Business/Finance', 'Education/Research', 'Law', 'Media/Communication',
                'Psychology', 'Environmental Science', 'Architecture', 'Music/Performance',
                'Sports/Athletics', 'Writing/Literature', 'Public Service', 'Research/Academia',
                'Physical Education'  # Added this to the official list
            ]
            self._initialize_model()
        except Exception as e:
            print(f"Error initializing model: {e}")
            # Provide a fallback
            self.model = None
            self.label_encoder = LabelEncoder()
            self.career_options = [
                'Physics/Science', 'Technology/Entrepreneurship', 'Politics/Social Reform',
                'Engineering', 'Management', 'IT', 'Medical', 'Arts/Creative'
            ]

    def _get_astrological_rules(self, features):
        """Apply traditional astrological rules for career prediction"""
        # Convert data to normalized format if needed
        normalized_features = {}
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            # If data is in planet dictionary format
            if planet in features and isinstance(features[planet], dict) and 'house' in features[planet]:
                normalized_features[f'{planet}_house'] = features[planet]['house']
                normalized_features[f'{planet}_sign'] = features[planet]['sign']
            # If data is already in normalized format
            elif f'{planet}_house' in features:
                normalized_features[f'{planet}_house'] = features[f'{planet}_house']
                normalized_features[f'{planet}_sign'] = features[f'{planet}_sign']
            else:
                # Default values if data is missing
                normalized_features[f'{planet}_house'] = 1
                normalized_features[f'{planet}_sign'] = 0
        
        rules_score = {}
        
        # Initialize scores for each career - use .copy() to avoid reference issues
        all_careers = self.career_options.copy()
        if 'Physical Education' not in all_careers:
            all_careers.append('Physical Education')
        
        for career in all_careers:
            rules_score[career] = 0
            
        # Ensure all careers used in rules exist in the rules_score dictionary
        for career in ['Management', 'Politics/Social Reform', 'Business/Finance', 'Public Service',
                      'Arts/Creative', 'Music/Performance', 'Writing/Literature', 'Sports/Athletics',
                      'IT', 'Engineering', 'Media/Communication', 'Education/Research', 'Research/Academia',
                      'Law', 'Physics/Science', 'Technology/Entrepreneurship', 'Medical', 'Psychology',
                      'Environmental Science', 'Architecture', 'Physical Education']:
            if career not in rules_score:
                rules_score[career] = 0
        
        # Sun in 10th house - Career success and recognition
        if normalized_features['Sun_house'] == 10:
            rules_score['Management'] += 3
            rules_score['Politics/Social Reform'] += 3
            rules_score['Business/Finance'] += 3
            rules_score['Public Service'] += 2
        
        # Sun in 5th house - Creative expression and leadership
        if normalized_features['Sun_house'] == 5:
            rules_score['Arts/Creative'] += 3
            rules_score['Music/Performance'] += 3
            rules_score['Writing/Literature'] += 2
            rules_score['Sports/Athletics'] += 2
        
        # Mercury in 3rd or 6th house - Communication and technical skills
        if normalized_features['Mercury_house'] in [3, 6]:
            rules_score['IT'] += 3
            rules_score['Engineering'] += 3
            rules_score['Media/Communication'] += 3
            rules_score['Writing/Literature'] += 2
        
        # Mercury in 9th house - Higher education and philosophy
        if normalized_features['Mercury_house'] == 9:
            rules_score['Education/Research'] += 3
            rules_score['Research/Academia'] += 3
            rules_score['Law'] += 2
            rules_score['Writing/Literature'] += 2
        
        # Jupiter in 5th or 9th house - Education and wisdom
        if normalized_features['Jupiter_house'] in [5, 9]:
            rules_score['Education/Research'] += 3
            rules_score['Law'] += 3
            rules_score['Physics/Science'] += 3
            rules_score['Research/Academia'] += 2
        
        # Jupiter in 2nd house - Financial success and abundance
        if normalized_features['Jupiter_house'] == 2:
            rules_score['Business/Finance'] += 3
            rules_score['Management'] += 2
            rules_score['Technology/Entrepreneurship'] += 2
        
        # Mars in 1st or 10th house - Leadership and initiative
        if normalized_features['Mars_house'] in [1, 10]:
            rules_score['Technology/Entrepreneurship'] += 3
            rules_score['Business/Finance'] += 3
            rules_score['Politics/Social Reform'] += 3
            rules_score['Sports/Athletics'] += 2
        
        # Mars in 6th house - Service and technical work
        if normalized_features['Mars_house'] == 6:
            rules_score['Engineering'] += 3
            rules_score['IT'] += 3
            rules_score['Medical'] += 2
            rules_score['Public Service'] += 2
        
        # Venus in 5th or 7th house - Creative and artistic abilities
        if normalized_features['Venus_house'] in [5, 7]:
            rules_score['Arts/Creative'] += 3
            rules_score['Media/Communication'] += 3
            rules_score['Music/Performance'] += 3
            rules_score['Writing/Literature'] += 2
        
        # Venus in 2nd house - Financial acumen and luxury
        if normalized_features['Venus_house'] == 2:
            rules_score['Business/Finance'] += 3
            rules_score['Management'] += 2
            rules_score['Architecture'] += 2
        
        # Saturn in 6th or 8th house - Technical and analytical skills
        if normalized_features['Saturn_house'] in [6, 8]:
            rules_score['Engineering'] += 3
            rules_score['IT'] += 3
            rules_score['Medical'] += 3
            rules_score['Architecture'] += 2
        
        # Saturn in 10th house - Career discipline and authority
        if normalized_features['Saturn_house'] == 10:
            rules_score['Management'] += 3
            rules_score['Public Service'] += 3
            rules_score['Law'] += 2
            rules_score['Education/Research'] += 2
        
        # Moon in 4th or 7th house - Emotional intelligence and service
        if normalized_features['Moon_house'] in [4, 7]:
            rules_score['Medical'] += 3
            rules_score['Education/Research'] += 3
            rules_score['Politics/Social Reform'] += 3
            rules_score['Psychology'] += 3
        
        # Moon in 5th house - Creative expression and entertainment
        if normalized_features['Moon_house'] == 5:
            rules_score['Arts/Creative'] += 3
            rules_score['Music/Performance'] += 3
            rules_score['Writing/Literature'] += 2
        
        # Additional planetary aspects and combinations
        # Sun-Mercury conjunction - Communication and leadership
        if normalized_features['Sun_house'] == normalized_features['Mercury_house']:
            rules_score['Media/Communication'] += 2
            rules_score['Writing/Literature'] += 2
            rules_score['Politics/Social Reform'] += 2
        
        # Jupiter-Saturn combination - Education and discipline
        if normalized_features['Jupiter_house'] == normalized_features['Saturn_house']:
            rules_score['Education/Research'] += 2
            rules_score['Law'] += 2
            rules_score['Research/Academia'] += 2
        
        # Mars-Venus combination - Creative action and passion
        if normalized_features['Mars_house'] == normalized_features['Venus_house']:
            rules_score['Arts/Creative'] += 2
            rules_score['Music/Performance'] += 2
            rules_score['Sports/Athletics'] += 2
        
        # Special career indicators
        # Environmental Science - Jupiter in 4th house
        if normalized_features['Jupiter_house'] == 4:
            rules_score['Environmental Science'] += 3
            rules_score['Public Service'] += 2
        
        # Psychology - Moon in 8th house
        if normalized_features['Moon_house'] == 8:
            rules_score['Psychology'] += 3
            rules_score['Medical'] += 2
        
        # Architecture - Saturn in 4th house
        if normalized_features['Saturn_house'] == 4:
            rules_score['Architecture'] += 3
            rules_score['Engineering'] += 2
        
        # Sports/Athletics - Mars in 5th house
        if normalized_features['Mars_house'] == 5:
            rules_score['Sports/Athletics'] += 3
            rules_score['Physical Education'] += 2
        
        return rules_score

    def _initialize_model(self):
        """Initialize the model with famous personalities data and astrological rules"""
        X = []
        y = []
        
        # Get famous personalities data
        personalities = FamousPersonalities.get_personalities()
        
        # Create training data from famous personalities
        for person, data in personalities.items():
            # Planet positions are already properly formatted for our model
            features = self.preprocess_features(data['planet_positions'])
            X.append(features)
            y.append(data['actual_career'])
        
        # Add synthetic data with astrological rules
        np.random.seed(42)
        n_samples = 2000  # Increased sample size
        
        for _ in range(n_samples):
            # Create normalized format directly for synthetic data
            features = {}
            for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                features[f'{planet}_house'] = np.random.randint(1, 13)
                features[f'{planet}_sign'] = np.random.randint(0, 12)
            
            # Apply astrological rules to determine career
            rules_score = self._get_astrological_rules(features)
            
            # Select top 3 careers based on rules
            top_careers = sorted(rules_score.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Randomly select one of the top 3 careers with higher probability for higher scores
            total_score = sum(score for _, score in top_careers)
            if total_score > 0:
                probs = [score/total_score for _, score in top_careers]
                career = np.random.choice([career for career, _ in top_careers], p=probs)
            else:
                career = np.random.choice(self.career_options)
            
            # Use standard format for features
            X.append(self.preprocess_features(features))
            y.append(career)
        
        # Train the model
        self.train(X, y)

    def preprocess_features(self, data):
        """Convert astrological data to numerical features"""
        features = []
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            # Check if data is already structured with planet as key and house/sign as nested dict
            if planet in data and isinstance(data[planet], dict) and 'house' in data[planet] and 'sign' in data[planet]:
                features.append(data[planet]['house'])
                features.append(data[planet]['sign'])
            # Check if data is structured with planet_house and planet_sign as keys
            elif f'{planet}_house' in data and f'{planet}_sign' in data:
                features.append(data[f'{planet}_house'])
                features.append(data[f'{planet}_sign'])
            else:
                # Default values if data is missing
                features.append(1)  # Default house
                features.append(0)  # Default sign
        return features

    def train(self, X, y):
        """Train the model with preprocessed data"""
        try:
            # Make sure all career options are in the training data
            career_set = set(y)
            for career in self.career_options:
                if career not in career_set:
                    # Add dummy samples for missing careers
                    X.append([1] * len(X[0]))  # Simple dummy feature vector
                    y.append(career)
            
            # Fit the label encoder to include all possible careers
            self.label_encoder.fit(self.career_options)
            
            # Train the model
            encoded_y = self.label_encoder.transform(y)
            self.model.fit(X, encoded_y)
            
            print(f"Model trained with {len(X)} samples")
            print(f"Career labels encoded: {list(self.label_encoder.classes_)}")
        except Exception as e:
            print(f"Error during model training: {e}")
            # Create a simple fallback model
            self.model = RandomForestClassifier(n_estimators=10, random_state=42)
            dummy_x = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]] * len(self.career_options)
            dummy_y = list(range(len(self.career_options)))
            self.model.fit(dummy_x, dummy_y)
            print("Using fallback model due to training error")

    def predict(self, features):
        """Predict career based on astrological features"""
        try:
            # Ensure features are in the correct format for processing
            features_processed = self.preprocess_features(features)
            
            # Check if model is initialized
            if self.model is None:
                raise ValueError("Model not properly initialized")
            
            # Get model predictions
            prediction = self.model.predict([features_processed])
            probabilities = self.model.predict_proba([features_processed])[0]
            
            # Get astrological rules scores
            rules_score = self._get_astrological_rules(features)
            
            # Normalize rules scores
            max_rules_score = max(rules_score.values()) if rules_score.values() else 1
            normalized_rules_score = {career: score/max_rules_score for career, score in rules_score.items()}
            
            # Combine model predictions with astrological rules
            combined_scores = {}
            for career in self.career_options:
                try:
                    # Check if career exists in label encoder
                    if career in self.label_encoder.classes_:
                        model_score = probabilities[self.label_encoder.transform([career])[0]]
                    else:
                        # Model wasn't trained on this career
                        model_score = 0.1
                    
                    # Ensure career exists in normalized_rules_score
                    if career in normalized_rules_score:
                        rules_weight = normalized_rules_score[career]
                    else:
                        rules_weight = 0.0
                        
                    combined_scores[career] = 0.6 * model_score + 0.4 * rules_weight
                except Exception as e:
                    print(f"Error processing career {career}: {e}")
                    combined_scores[career] = 0.1  # Default score for error cases
            
            # Get top 3 career predictions
            top_careers = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            predicted_career = top_careers[0][0]
            
            return predicted_career, combined_scores, top_careers
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            # Return fallback predictions based on astrological rules only
            try:
                rules_score = self._get_astrological_rules(features)
                
                # Normalize and prepare basic prediction
                max_rules_score = max(rules_score.values()) if rules_score.values() else 1
                normalized_scores = {career: score/max_rules_score for career, score in rules_score.items()}
                
                # Ensure we only return scores for careers in self.career_options
                filtered_scores = {k: v for k, v in normalized_scores.items() if k in self.career_options}
                
                # If filtered_scores is empty, provide default scores
                if not filtered_scores:
                    filtered_scores = {career: 0.1 for career in self.career_options}
                
                top_careers = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                predicted_career = top_careers[0][0]
                
                return predicted_career, filtered_scores, top_careers
            except Exception as inner_e:
                print(f"Fallback prediction also failed: {inner_e}")
                # Ultimate fallback - just return default values
                default_career = self.career_options[0]
                default_scores = {career: 0.1 for career in self.career_options}
                default_top_careers = [(default_career, 0.1), 
                                     (self.career_options[1], 0.05), 
                                     (self.career_options[2], 0.03)]
                
                return default_career, default_scores, default_top_careers