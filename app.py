import streamlit as st
import plotly.express as px
import traceback
from model.career_predictor import CareerPredictor
from utils.astro_utils import AstroUtils
from utils.data_processor import DataProcessor
from utils.famous_personalities import FamousPersonalities
from utils.astro_api import AstroAPI
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

        # Remove all these sections as requested
        # st.subheader("Career Insights")
        # 
        # if planet_positions:
        #     st.write("### Teaching and Research Potential")
        #     teaching_insights = AstroUtils.get_career_insights(planet_positions)
        #     st.write(teaching_insights)
        #     
        #     st.write("\n### Potential Education Career Paths")
        #     education_careers = {
        #         "Teaching Faculty": {
        #             "Primary/Secondary Education": ["School Teacher", "Subject Specialist", "Educational Counselor"],
        #             "Higher Education": ["Professor", "Associate Professor", "Assistant Professor", "Lecturer"],
        #             "Specialized Teaching": ["Research Guide", "Mentor", "Educational Consultant"]
        #         },
        #         "Non-Teaching Faculty": {
        #             "Administration": ["Academic Administrator", "Department Head", "Dean", "Registrar"],
        #             "Research": ["Research Scientist", "Research Associate", "Postdoctoral Researcher"],
        #             "Support Services": ["Librarian", "Lab Technician", "Academic Coordinator"]
        #         }
        #     }
        #     
        #     for category, subcategories in education_careers.items():
        #         st.write(f"#### {category}")
        #         for subcategory, roles in subcategories.items():
        #             st.write(f"**{subcategory}:**")
        #             for role in roles:
        #                 st.write(f"- {role}")
        # 
        # st.write("\n### General Career Compatibility")
        # for career, score in confidence_scores.items():
        #     st.write(f"**{career}**: {score:.2%} compatibility")
            
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
    
    # Time of Birth with manual adjustment
    st.subheader("Time of Birth")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hour = st.number_input(
            "Hour (0-23)",
            min_value=0,
            max_value=23,
            value=12,
            step=1
        )
    
    with col2:
        minute = st.number_input(
            "Minute (0-59)",
            min_value=0,
            max_value=59,
            value=0,
            step=1
        )
    
    with col3:
        second = st.number_input(
            "Second (0-59)",
            min_value=0,
            max_value=59,
            value=0,
            step=1
        )
    
    birth_time = datetime.time(hour, minute, second)
    
    # Display the selected time
    st.write(f"Selected Time: {birth_time.strftime('%I:%M:%S %p')}")
    
    # Birth Place
    st.subheader("Birth Place Details")
    
    # Country
    country = st.text_input("Country", "India")
    
    # List of Indian states and union territories
    indian_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
        "Uttarakhand", "West Bengal"
    ]
    
    # Union Territories
    union_territories = [
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]
    
    # Combine states and UTs for the dropdown
    all_states_uts = ["Select State/UT"] + indian_states + union_territories
    
    # State dropdown
    state_index = st.selectbox(
        "State/Union Territory",
        range(len(all_states_uts)),
        format_func=lambda x: all_states_uts[x]
    )
    
    state = all_states_uts[state_index] if state_index > 0 else ""
    
    # Dictionary mapping states to all districts
    cities_by_state = {
        "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
        "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kamle", "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang"],
        "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
        "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"],
        "Chhattisgarh": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"],
        "Goa": ["North Goa", "South Goa"],
        "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
        "Haryana": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
        "Himachal Pradesh": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"],
        "Jharkhand": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahebganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"],
        "Karnataka": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"],
        "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"],
        "Madhya Pradesh": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"],
        "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"],
        "Manipur": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"],
        "Meghalaya": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"],
        "Mizoram": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saiha", "Saitual", "Serchhip"],
        "Nagaland": ["Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Peren", "Phek", "Tuensang", "Wokha", "Zunheboto"],
        "Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"],
        "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Pathankot", "Patiala", "Rupnagar", "Sahibzada Ajit Singh Nagar", "Sangrur", "Shahid Bhagat Singh Nagar", "Sri Muktsar Sahib", "Tarn Taran"],
        "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
        "Sikkim": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"],
        "Tamil Nadu": ["Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"],
        "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Komaram Bheem", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"],
        "Tripura": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
        "Uttar Pradesh": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
        "Uttarakhand": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"],
        "West Bengal": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"],
        "Andaman and Nicobar Islands": ["Nicobar", "North and Middle Andaman", "South Andaman"],
        "Chandigarh": ["Chandigarh"],
        "Dadra and Nagar Haveli and Daman and Diu": ["Dadra and Nagar Haveli", "Daman", "Diu"],
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
        "Jammu and Kashmir": ["Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"],
        "Ladakh": ["Kargil", "Leh"],
        "Lakshadweep": ["Lakshadweep"],
        "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"]
    }
    
    # District/City dropdown (dependent on state selection)
    district_options = ["Select District/City"]
    if state and state in cities_by_state:
        district_options.extend(cities_by_state[state])
    
    district_index = st.selectbox(
        "District/City",
        range(len(district_options)),
        format_func=lambda x: district_options[x]
    )
    
    district = district_options[district_index] if district_index > 0 else ""
    
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

def display_birth_chart(birth_date, birth_time, latitude, longitude):
    """Display birth chart using Free Astrology API"""
    try:
        # Get horoscope chart SVG
        svg_code = AstroAPI.get_horoscope_chart_svg(birth_date, birth_time, latitude, longitude)
        
        # Display the SVG chart
        st.markdown("### Birth Chart")
        st.markdown(svg_code, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error generating birth chart: {str(e)}")

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
                    # Display birth chart
                    display_birth_chart(dob, birth_time, latitude, longitude)
                    
                    # Calculate planetary positions and Lagna
                    planet_positions, lagna_sign = AstroUtils.calculate_planet_positions(
                        dob, birth_time, latitude, longitude
                    )
                    
                    # Comment out or remove these two lines to hide Kundali details
                    # st.subheader("Generated Kundli (Details)")
                    # st.write(AstroUtils.get_planet_details(planet_positions, lagna_sign))
                    
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
