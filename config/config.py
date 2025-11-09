"""Configuration management for Multi-AI Agent
Prioritizes environment variables from Render/Production over .env file
"""

import os
import sys

# Only load .env file if it exists and we're not in production
# In production (Render), environment variables are set directly
is_production = (
    os.environ.get('RENDER') is not None or
    os.environ.get('DYNO') is not None or
    os.environ.get('PORT') is not None or
    os.environ.get('FLASK_ENV') == 'production'
)

if not is_production:
    try:
        from dotenv import load_dotenv
        # Try to load .env, but don't fail if it doesn't exist
        load_dotenv(verbose=False)
    except (ImportError, Exception):
        # python-dotenv not installed or .env file doesn't exist - that's okay
        pass


class Config:
    """Application configuration - uses environment variables directly (Render compatible)"""

    # Gemini API Configuration (Primary AI)
    # Gets from environment variable (set in Render dashboard)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

    # Groq API Configuration (Fallback AI #1)
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')

    # OpenRouter API Configuration (Fallback AI #2)
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

    # Web Search Configuration
    # Poe API Configuration (Web Search Bot)
    POE_API_KEY = os.environ.get('POE_API_KEY', '')
    POE_BOT_NAME = os.environ.get('POE_BOT_NAME', 'Web-Search')
    POE_API_URL = os.environ.get('POE_API_URL', 'https://api.poe.com/bot/')
    
    # DuckDuckGo - free, no API key required (fallback)
    # Automatically enabled when duckduckgo-search is installed

    # Weather Configuration (Open-Meteo - free, no API key required)
    OPEN_METEO_URL = os.environ.get('OPEN_METEO_URL', 'https://api.open-meteo.com/v1/forecast')
    GEOCODING_URL = os.environ.get('GEOCODING_URL', 'https://geocoding-api.open-meteo.com/v1/search')

    # Agriculture API Configuration
    AGRICULTURE_API_KEY = os.environ.get('AGRICULTURE_API_KEY', '')
    AGRICULTURE_API_URL = os.environ.get('AGRICULTURE_API_URL', '')

    # Google Earth Engine Configuration
    GEE_API_KEY = os.environ.get('GEE_API_KEY', '')
    GEE_PROJECT_ID = os.environ.get('GEE_PROJECT_ID', '')
    
    # MeshCore Integration (optional)
    MESHCORE_API_KEY = os.environ.get('MESHCORE_API_KEY', '')
    MESHCORE_AGENT_ID = os.environ.get('MESHCORE_AGENT_ID', '')


def validate_config():
    """Validate required configuration (non-blocking, Render-compatible)"""
    has_ai_key = (
        Config.GEMINI_API_KEY or 
        Config.GROQ_API_KEY or 
        Config.OPENROUTER_API_KEY
    )

    if not has_ai_key:
        error_msg = "Warning: No AI API keys configured in environment variables"
        instructions = """
For Render deployment, set environment variables in Render dashboard:
  - GEMINI_API_KEY (recommended, free)
  - GROQ_API_KEY (fast, free)
  - OPENROUTER_API_KEY (multiple models)

For local development, create .env file:
  - GEMINI_API_KEY=your_key_here
  - GROQ_API_KEY=your_key_here
  - OPENROUTER_API_KEY=your_key_here

Get API keys from:
  - Gemini: https://makersuite.google.com/app/apikey
  - Groq: https://console.groq.com/keys
  - OpenRouter: https://openrouter.ai/keys
"""
        # In production, just log warning (don't exit)
        if is_production:
            import logging
            logging.warning(error_msg + instructions)
        else:
            print(error_msg + instructions)
            # Don't exit - allow the app to start and show helpful error messages
            if os.path.exists('.env'):
                print("\nNote: .env file exists but no API keys found in environment variables.")
            else:
                print("\nNote: No .env file found. Create one for local development.")
