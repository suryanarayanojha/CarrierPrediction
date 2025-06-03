import streamlit as st
import plotly.express as px
import traceback
from model.career_predictor import CareerPredictor
from utils.astro_utils import AstroUtils
from utils.data_processor import DataProcessor
from utils.famous_personalities import FamousPersonalities
import pandas as pd
import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from utils.lagna_chart_plot import plot_north_indian_chart

def initialize_session_state():
    if 'predictor' not in st.session_state:
        try:
            st.session_state.predictor = CareerPredictor()
        except Exception as e:
            st.error(f"Error initializing predictor: {str(e)}")
            st.session_state.predictor = None

def create_planet_input_form():
    planet_positions = {}
    zodiac_signs = AstroUtils.get_zodiac_signs()
    houses = AstroUtils.get_houses()
    
    st.subheader("Enter Planetary Positions")
    cols = st.columns(2)
    
    for idx, planet in enumerate(AstroUtils.get_planets()):
        with cols[idx % 2]:
            st.write(f"### {planet}")
            house = st.selectbox(
                f"{planet} House",
                houses,
                key=f"{planet}_house"
            )
            sign = st.selectbox(
                f"{planet} Sign",
                range(len(zodiac_signs)),
                format_func=lambda x: zodiac_signs[x],
                key=f"{planet}_sign"
            )
            planet_positions[planet] = {'house': house, 'sign': sign}
    
    return planet_positions

def display_prediction(career, confidence_scores, top_careers=None, planet_positions=None):
    try:
        st.subheader("Career Prediction Results")
        
        if top_careers:
            st.write("### Top Career Recommendations:")
            for i, (career_name, score) in enumerate(top_careers):
                st.write(f"{i+1}. **{career_name}**: {score:.2%} compatibility")
        else:
            st.write(f"### Recommended Career Path: {career}")
        
        # Create confidence score visualization
        careers, scores = DataProcessor.prepare_visualization_data(confidence_scores)
        fig = px.bar(
            x=careers,
            y=scores,
            title="Career Confidence Scores",
            labels={'x': 'Career Options', 'y': 'Confidence Score'}
        )
        st.plotly_chart(fig)

        # Display career insights
        st.subheader("Career Insights")
        
        # Display teaching and research potential
        if planet_positions:
            st.write("### Teaching and Research Potential")
            teaching_insights = AstroUtils.get_career_insights(planet_positions)
            st.write(teaching_insights)
            
            # Add specific education career paths
            st.write("\n### Potential Education Career Paths")
            education_careers = {
                "Teaching Faculty": {
                    "Primary/Secondary Education": ["School Teacher", "Subject Specialist", "Educational Counselor"],
                    "Higher Education": ["Professor", "Associate Professor", "Assistant Professor", "Lecturer"],
                    "Specialized Teaching": ["Research Guide", "Mentor", "Educational Consultant"]
                },
                "Non-Teaching Faculty": {
                    "Administration": ["Academic Administrator", "Department Head", "Dean", "Registrar"],
                    "Research": ["Research Scientist", "Research Associate", "Postdoctoral Researcher"],
                    "Support Services": ["Librarian", "Lab Technician", "Academic Coordinator"]
                }
            }
            
            for category, subcategories in education_careers.items():
                st.write(f"#### {category}")
                for subcategory, roles in subcategories.items():
                    st.write(f"**{subcategory}:**")
                    for role in roles:
                        st.write(f"- {role}")
        
        # Display general career insights
        st.write("\n### General Career Compatibility")
        for career, score in confidence_scores.items():
            st.write(f"**{career}**: {score:.2%} compatibility")
            
    except Exception as e:
        st.error(f"Error displaying prediction: {str(e)}")
        st.write("Something went wrong while displaying the prediction results. Please try again.")

def display_famous_personality_prediction():
    st.subheader("Test Model with Famous Personalities")
    
    try:
        personalities = FamousPersonalities.get_personalities()
        
        # Calculate overall model accuracy
        st.write("### Model Accuracy Statistics")
        with st.expander("View Model Accuracy Details", expanded=True):
            total_predictions = len(personalities)
            exact_matches = 0
            partial_matches = 0
            total_confidence = 0
            
            accuracy_data = []
            
            for person, data in personalities.items():
                features = DataProcessor.create_feature_dict(data['planet_positions'])
                career, confidence_scores, top_careers = st.session_state.predictor.predict(features)
                actual_career = data['actual_career']
                
                # Check for exact match
                if career == actual_career:
                    exact_matches += 1
                    match_type = "Exact Match"
                    accuracy = 100
                else:
                    # Check for partial matches in top 3
                    top_career_names = [c for c, _ in top_careers]
                    matched = False
                    for pred_career in top_career_names:
                        if (pred_career.lower() in actual_career.lower() or 
                            actual_career.lower() in pred_career.lower()):
                            partial_matches += 1
                            matched = True
                            match_type = "Partial Match"
                            # Calculate accuracy based on position in top 3
                            position = top_career_names.index(pred_career) + 1
                            accuracy = 100 - (position - 1) * 20  # 100% for 1st, 80% for 2nd, 60% for 3rd
                            break
                    
                    if not matched:
                        match_type = "No Match"
                        accuracy = max(confidence_scores[career] * 100, 20)  # At least 20% accuracy
                
                # Get confidence score for actual career
                confidence = confidence_scores.get(actual_career, 0) * 100
                total_confidence += confidence
                
                # Store accuracy data
                accuracy_data.append({
                    "Name": person,
                    "Actual Career": actual_career,
                    "Predicted Career": career,
                    "Match Type": match_type,
                    "Accuracy": accuracy,
                    "Confidence": confidence
                })
            
            # Calculate overall statistics
            exact_match_rate = (exact_matches / total_predictions) * 100
            partial_match_rate = (partial_matches / total_predictions) * 100
            overall_match_rate = ((exact_matches + partial_matches) / total_predictions) * 100
            avg_confidence = total_confidence / total_predictions
            
            # Display overall statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Overall Accuracy",
                    f"{overall_match_rate:.1f}%",
                    help="Percentage of predictions that were either exact or partial matches"
                )
            
            with col2:
                st.metric(
                    "Exact Match Rate",
                    f"{exact_match_rate:.1f}%",
                    help="Percentage of predictions that exactly matched the actual career"
                )
            
            with col3:
                st.metric(
                    "Average Confidence",
                    f"{avg_confidence:.1f}%",
                    help="Average confidence score across all predictions"
                )
            
            # Display detailed accuracy table
            st.write("### Detailed Accuracy Analysis")
            accuracy_df = pd.DataFrame(accuracy_data)
            
            # Add color coding based on match type
            def color_match_type(val):
                if val == "Exact Match":
                    return 'background-color: #90EE90'
                elif val == "Partial Match":
                    return 'background-color: #FFE4B5'
                else:
                    return 'background-color: #FFB6C1'
            
            # Style the dataframe
            styled_df = accuracy_df.style.apply(lambda x: [color_match_type(val) if i == 3 else '' 
                                                         for i, val in enumerate(x)], axis=1)
            
            st.dataframe(styled_df)
            
            # Display accuracy distribution chart
            st.write("### Accuracy Distribution")
            fig = px.histogram(
                accuracy_df,
                x="Accuracy",
                nbins=10,
                title="Distribution of Prediction Accuracy",
                labels={'Accuracy': 'Accuracy (%)', 'count': 'Number of Predictions'}
            )
            st.plotly_chart(fig)
        
        # Continue with individual personality selection
        selected_person = st.selectbox(
            "Select a Famous Personality",
            list(personalities.keys())
        )
        
        if selected_person:
            person_data = personalities[selected_person]
            
            # Display person's details
            st.write(f"### {selected_person}")
            st.write(f"**Birth Date:** {person_data['birth_date']}")
            st.write(f"**Actual Career:** {person_data['actual_career']}")
            st.write(f"**Achievements:** {person_data['achievements']}")
            
            # Make prediction using their planetary positions
            if st.button("Predict Career for Selected Personality"):
                with st.spinner("Analyzing planetary positions..."):
                    try:
                        features = DataProcessor.create_feature_dict(person_data['planet_positions'])
                        career, confidence_scores, top_careers = st.session_state.predictor.predict(features)
                        
                        # Display results with comparison
                        st.subheader("Model Prediction Results")
                        
                        # Display top 3 career recommendations
                        st.write("### Top Career Recommendations:")
                        for i, (career_name, score) in enumerate(top_careers):
                            st.write(f"{i+1}. **{career_name}**: {score:.2%} compatibility")
                        
                        st.write(f"**Actual Career:** {person_data['actual_career']}")
                        
                        # Create confidence score visualization
                        careers, scores = DataProcessor.prepare_visualization_data(confidence_scores)
                        fig = px.bar(
                            x=careers,
                            y=scores,
                            title="Career Confidence Scores",
                            labels={'x': 'Career Options', 'y': 'Confidence Score'}
                        )
                        st.plotly_chart(fig)
                        
                        # Display model accuracy analysis
                        st.subheader("Model Accuracy Analysis")
                        
                        # Check if any of the top 3 careers match the actual career
                        top_career_names = [career_name for career_name, _ in top_careers]
                        actual_career = person_data['actual_career']
                        
                        # Check for partial matches
                        matches = []
                        for top_career in top_career_names:
                            if (top_career.lower() in actual_career.lower() or 
                                actual_career.lower() in top_career.lower()):
                                matches.append(top_career)
                        
                        if matches:
                            st.success(f"✅ Model prediction aligns with actual career! Matches: {', '.join(matches)}")
                            
                            match_rank = top_career_names.index(matches[0]) + 1
                            if match_rank == 1:
                                st.success("Perfect match! The model's top recommendation matches the actual career.")
                            elif match_rank == 2:
                                st.info("Good match! The model's second recommendation matches the actual career.")
                            else:
                                st.info(f"Partial match. The model's {match_rank}rd recommendation matches the actual career.")
                        else:
                            st.warning("⚠️ Model prediction differs from actual career")
                            
                            # Find the closest match
                            closest_match = None
                            highest_score = 0
                            
                            for career_option, score in confidence_scores.items():
                                if (career_option.lower() in actual_career.lower() or 
                                    actual_career.lower() in career_option.lower()):
                                    if score > highest_score:
                                        highest_score = score
                                        closest_match = career_option
                            
                            if closest_match:
                                st.info(f"Closest match in all options: **{closest_match}** with {highest_score:.2%} confidence")
                        
                        # Display career insights
                        display_prediction(career, confidence_scores, top_careers, person_data['planet_positions'])
                    except Exception as e:
                        st.error(f"Error during prediction: {str(e)}")
                        st.write("Something went wrong during the prediction. Please try again or select a different personality.")
    except Exception as e:
        st.error(f"Error loading personalities: {str(e)}")
        st.write("Something went wrong while loading the famous personalities. Please refresh the page and try again.")

def get_coordinates_from_location(country, state, district):
    """Get coordinates from location details using geocoding"""
    try:
        # Create a geocoder instance
        geolocator = Nominatim(user_agent="career_astro_predictor")
        
        # Construct the location string
        location_str = f"{district}, {state}, {country}"
        
        # Get location
        location = geolocator.geocode(location_str)
        
        if location:
            return location.latitude, location.longitude
        else:
            st.warning("Could not find exact coordinates. Using default coordinates.")
            return 0.0, 0.0
            
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        st.error(f"Error getting coordinates: {str(e)}")
        return 0.0, 0.0

def create_birth_details_form():
    st.subheader("Enter Birth Details")
    
    # Date of Birth
    dob = st.date_input(
        "Date of Birth",
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date.today()
    )
    
    # Time of Birth
    birth_time = st.time_input("Time of Birth")
    
    # Birth Place
    st.subheader("Birth Place Details")
    
    # Country
    country = st.text_input("Country", "India")
    
    # State
    state = st.text_input("State")
    
    # District
    district = st.text_input("District")
    
    # Get coordinates from location
    latitude, longitude = get_coordinates_from_location(country, state, district)
    
    # Display coordinates
    st.write(f"Coordinates: Latitude {latitude:.6f}, Longitude {longitude:.6f}")
    
    # Allow manual coordinate adjustment if needed
    st.write("You can adjust the coordinates manually if needed:")
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=float(latitude),
            step=0.000001,
            format="%.6f"
        )
    with col2:
        longitude = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=float(longitude),
            step=0.000001,
            format="%.6f"
        )
    
    return dob, birth_time, latitude, longitude

def main():
    st.set_page_config(
        page_title="Vedic Astrology Career Predictor",
        page_icon="🌟",
        layout="wide"
    )
    
    st.title("🌟 Vedic Astrology Career Predictor")
    st.write("""
    This application combines traditional Vedic astrology with modern machine learning 
    to predict suitable career paths. Enter the planetary positions from your birth chart 
    to receive career recommendations.
    """)
    
    try:
        initialize_session_state()
        
        if st.session_state.predictor is None:
            st.error("Failed to initialize prediction model. Please refresh the page and try again.")
            return
        
        # Create tabs for different input methods
        tab1, tab2, tab3 = st.tabs(["Manual Input", "Birth Details", "Famous Personalities"])
        
        with tab1:
            st.header("Manual Planetary Positions")
            planet_positions = create_planet_input_form()
            
            if st.button("Predict Career"):
                try:
                    features = DataProcessor.create_feature_dict(planet_positions)
                    career, confidence_scores, top_careers = st.session_state.predictor.predict(features)
                    display_prediction(career, confidence_scores, top_careers, planet_positions)
                except Exception as e:
                    st.error(f"Error making prediction: {str(e)}")
        
        with tab2:
            st.header("Birth Details Input")
            dob, birth_time, latitude, longitude = create_birth_details_form()
            
            if st.button("Generate Kundli and Predict"):
                try:
                    # Calculate planetary positions and Lagna
                    planet_positions, lagna_sign = AstroUtils.calculate_planet_positions(
                        dob, birth_time, latitude, longitude
                    )
                    
                    # Display Lagna chart (North Indian style)
                    st.subheader("Lagna Chart (North Indian Style)")
                    fig = plot_north_indian_chart(planet_positions, lagna_sign)
                    st.pyplot(fig)
                    
                    # Display Kundli details with Lagna chart
                    st.subheader("Generated Kundli (Details)")
                    st.write(AstroUtils.get_planet_details(planet_positions, lagna_sign))
                    
                    # Add a separator
                    st.markdown("---")
                    
                    # Make prediction
                    st.subheader("Career Prediction")
                    features = DataProcessor.create_feature_dict(planet_positions)
                    career, confidence_scores, top_careers = st.session_state.predictor.predict(features)
                    display_prediction(career, confidence_scores, top_careers, planet_positions)
                    
                except Exception as e:
                    st.error(f"Error generating Kundli: {str(e)}")
                    st.error(traceback.format_exc())
        
        with tab3:
            display_famous_personality_prediction()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        st.write("An unexpected error occurred. Please refresh the page and try again.")

if __name__ == "__main__":
    main()
