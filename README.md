# Vedic Astrology Career Predictor

This application combines traditional Vedic astrology with modern machine learning to predict suitable career paths based on birth chart planetary positions.

## Features
- Input planetary positions from birth charts
- Career prediction with confidence scores
- Compare predictions with famous personalities
- Visual representation of results
- Detailed career insights

## Local Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CareerAstroPredictor
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Streamlit server:
```bash
streamlit run app.py
```

2. Open your web browser and go to:
```
http://localhost:8501
```

## Usage

1. Enter planetary positions:
   - Select house positions (1-12)
   - Select zodiac signs for each planet
   
2. Or choose a famous personality's chart:
   - Select from the dropdown menu
   - View their birth details
   - Compare predictions with actual achievements

3. Click "Predict Career" to see results:
   - Recommended career paths
   - Confidence scores
   - Career insights
   - Comparison charts (for famous personalities)

## Project Structure
```
CareerAstroPredictor/
├── app.py                 # Main Streamlit application
├── model/
│   └── career_predictor.py    # Career prediction model
├── utils/
│   ├── astro_utils.py         # Astrological calculations
│   ├── data_processor.py      # Data processing utilities
│   └── sample_data.py         # Sample birth charts
└── requirements.txt       # Project dependencies
```

## Troubleshooting

1. If you see "ModuleNotFoundError":
   - Make sure you've activated the virtual environment
   - Reinstall dependencies: `pip install -r requirements.txt`

2. If the app is slow to load:
   - First load may take time due to model initialization
   - Subsequent loads will be faster due to caching

3. If you see display issues:
   - Try clearing your browser cache
   - Restart the Streamlit server

## Contributing
Feel free to submit issues and enhancement requests! #   C a r r i e r P r e d i c t i o n  
 #   C a r r i e r P r e d i c t i o n  
 #   C a r r i e r P r e d i c t i o n  
 #   C a r r i e r P r e d i c t i o n  
 