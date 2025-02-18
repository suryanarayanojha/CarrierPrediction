import streamlit as st
import plotly.express as px
from model.career_predictor import CareerPredictor
from utils.astro_utils import AstroUtils
from utils.data_processor import DataProcessor

def initialize_session_state():
    if 'predictor' not in st.session_state:
        st.session_state.predictor = CareerPredictor()

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

def display_prediction(career, confidence_scores):
    st.subheader("Career Prediction Results")
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
    for career, score in confidence_scores.items():
        st.write(f"**{career}**: {score:.2%} compatibility")

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
    
    initialize_session_state()
    
    planet_positions = create_planet_input_form()
    
    if st.button("Predict Career"):
        with st.spinner("Analyzing planetary positions..."):
            # Validate inputs
            is_valid, error_message = AstroUtils.validate_inputs(planet_positions)
            
            if not is_valid:
                st.error(error_message)
            else:
                # Process data and make prediction
                features = DataProcessor.create_feature_dict(planet_positions)
                career, confidence_scores = st.session_state.predictor.predict(features)
                
                # Display results
                display_prediction(career, confidence_scores)

if __name__ == "__main__":
    main()
