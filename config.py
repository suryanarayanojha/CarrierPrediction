import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
ASTRO_API_KEY = os.getenv('ASTRO_API_KEY', '')
ASTRO_API_BASE_URL = "https://freeastrologyapi.com/api" 