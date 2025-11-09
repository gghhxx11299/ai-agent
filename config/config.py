"""Configuration management for Gemini Regional Agent"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Gemini API Configuration (Primary AI)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-2.5-flash'  # Using latest available Gemini 2.5 Flash model

    # Groq API Configuration (Fallback AI #1)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    # OpenRouter API Configuration (Fallback AI #2)
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

    # Web Search Configuration
    # Poe API Configuration (Web Search Bot)
    POE_API_KEY = os.getenv('POE_API_KEY')
    POE_BOT_NAME = os.getenv('POE_BOT_NAME', 'Web-Search')  # Poe bot for web search
    POE_API_URL = 'https://api.poe.com/bot/'
    
    # DuckDuckGo - free, no API key required (fallback)
    # Automatically enabled when duckduckgo-search is installed

    # Weather Configuration (Open-Meteo - free, no API key required)
    OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'
    GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'

    # Agriculture API Configuration
    AGRICULTURE_API_KEY = os.getenv('AGRICULTURE_API_KEY')
    AGRICULTURE_API_URL = os.getenv('AGRICULTURE_API_URL')

    # Google Earth Engine Configuration
    GEE_API_KEY = os.getenv('GEE_API_KEY')
    GEE_PROJECT_ID = os.getenv('GEE_PROJECT_ID')


def validate_config():
    """Validate required configuration (non-blocking in production)"""
    import os
    has_ai_key = Config.GEMINI_API_KEY or Config.GROQ_API_KEY or Config.OPENROUTER_API_KEY

    if not has_ai_key:
        error_msg = "❌ Error: No AI API keys configured"
        instructions = """
Please configure at least one of the following:

  Option 1 - Gemini (Recommended - FREE):
    1. Get API key from: https://makersuite.google.com/app/apikey
    2. Add to .env: GEMINI_API_KEY=your_key_here

  Option 2 - Groq (Fast & Free):
    1. Get API key from: https://console.groq.com/keys
    2. Add to .env: GROQ_API_KEY=your_key_here

  Option 3 - OpenRouter (Multiple Models):
    1. Get API key from: https://openrouter.ai/keys
    2. Add to .env: OPENROUTER_API_KEY=your_key_here

  You can configure multiple keys for automatic fallback!
"""
        # In production, just log warning instead of exiting
        is_production = (
            os.environ.get('FLASK_ENV') == 'production' or 
            os.environ.get('RENDER') is not None or
            os.environ.get('PORT') is not None
        )
        
        if is_production:
            import logging
            logging.warning(error_msg + instructions)
        else:
            print(error_msg + instructions)
            sys.exit(1)
