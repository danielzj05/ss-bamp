"""
Configuration loader for environment variables.
Loads the Gemini API key from .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
