import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
    AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
    AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")
    
    def __init__(self):
        # Validate required environment variables
        if not self.AMADEUS_CLIENT_ID or not self.AMADEUS_CLIENT_SECRET:
            logger.warning("Missing Amadeus API credentials in environment variables!")
            logger.warning("Please ensure AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET are set in your .env file")
            logger.warning("Register at https://developers.amadeus.com/ to get valid credentials")

settings = Settings()
