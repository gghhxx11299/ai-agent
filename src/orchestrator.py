"""Orchestrator for managing AI integrations and data flow"""

import asyncio
import os
import logging
from src.integrations.gemini import GeminiIntegration
from src.integrations.groq import GroqIntegration
from src.integrations.openrouter import OpenRouterIntegration
from src.integrations.web_search import WebSearchIntegration
from src.integrations.regional_data import RegionalDataIntegration
from config.config import Config

# Create a simple console wrapper for production compatibility
class SimpleConsole:
    """Simple console wrapper that works in production"""
    def print(self, *args, **kwargs):
        # Extract text from rich markup if present
        text = ' '.join(str(a) for a in args)
        # Remove rich markup tags
        import re
        text = re.sub(r'\[.*?\]', '', text)
        logging.info(text)
    
    def status(self, *args, **kwargs):
        return self
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

# Initialize console based on environment
try:
    # Check if we're in production (Render, Heroku, etc.)
    is_production = (
        os.environ.get('FLASK_ENV') == 'production' or 
        os.environ.get('RENDER') is not None or
        os.environ.get('DYNO') is not None or
        os.environ.get('PORT') is not None
    )
    
    if is_production:
        # Use simple console in production
        console = SimpleConsole()
        logging.basicConfig(level=logging.INFO)
    else:
        # Use rich console in development
        try:
            from rich.console import Console
            console = Console()
        except ImportError:
            console = SimpleConsole()
except Exception:
    # Fallback to simple console
    console = SimpleConsole()


class Orchestrator:
    """Main orchestrator for AI Agent with Groq and OpenRouter fallbacks"""

    def __init__(self):
        # Initialize AI models in priority order: Gemini -> Groq -> OpenRouter
        self.ai_models = []
        self.current_ai = None
        self.ai_name = "Unknown"

        # Try Gemini first
        if Config.GEMINI_API_KEY:
            try:
                gemini = GeminiIntegration()
                self.ai_models.append(("Gemini", gemini))
                console.print("Gemini initialized")
            except Exception as e:
                console.print(f"Gemini unavailable: {e}")

        # Try Groq second
        if Config.GROQ_API_KEY:
            try:
                groq = GroqIntegration()
                self.ai_models.append(("Groq", groq))
                console.print("Groq initialized")
            except Exception as e:
                console.print(f"Groq unavailable: {e}")

        # Try OpenRouter third
        if Config.OPENROUTER_API_KEY:
            try:
                openrouter = OpenRouterIntegration()
                self.ai_models.append(("OpenRouter", openrouter))
                console.print("OpenRouter initialized")
            except Exception as e:
                console.print(f"OpenRouter unavailable: {e}")

        # Set the current AI to the first available model
        if self.ai_models:
            self.ai_name, self.current_ai = self.ai_models[0]
            console.print(f"Using {self.ai_name} as primary AI")
        else:
            error_msg = "No AI models available. Please configure at least one API key (Gemini, Groq, or OpenRouter)"
            console.print(error_msg)
            # Don't raise in production, allow graceful degradation
            is_production = (
                os.environ.get('FLASK_ENV') == 'production' or 
                os.environ.get('RENDER') is not None or
                os.environ.get('PORT') is not None
            )
            if not is_production:
                raise Exception(error_msg)

        self.web_search = WebSearchIntegration()  # Uses Poe, DuckDuckGo, and Wikipedia with fallbacks
        self.regional_data = RegionalDataIntegration()
        
    async def cleanup(self):
        """Clean up resources (close HTTP clients)"""
        if hasattr(self.regional_data, 'client'):
            await self.regional_data.client.aclose()
        if hasattr(self.web_search, 'client'):
            await self.web_search.client.aclose()
        for name, ai_instance in self.ai_models:
            if hasattr(ai_instance, 'client'):
                await ai_instance.client.aclose()

    async def _safe_ai_call(self, method_name: str, *args, **kwargs):
        """
        Safely call AI methods with automatic fallback through all available models

        Args:
            method_name: Name of the method to call (e.g., 'analyze_query')
            *args, **kwargs: Arguments to pass to the method

        Returns:
            Result from the AI call
        """
        errors = []

        # Try each AI model in order
        for idx, (name, ai_instance) in enumerate(self.ai_models):
            try:
                method = getattr(ai_instance, method_name)
                result = await method(*args, **kwargs)

                # If we succeeded with a fallback model, update current AI
                if idx > 0:
                    console.print(f"Switched to {name} as primary AI")
                    self.ai_name = name
                    self.current_ai = ai_instance
                    # Move successful model to front for future calls
                    self.ai_models.insert(0, self.ai_models.pop(idx))

                return result

            except Exception as e:
                errors.append(f"{name}: {str(e)}")
                if idx < len(self.ai_models) - 1:
                    console.print(f"{name} failed, trying next fallback...")

        # If all models failed, raise combined error
        error_msg = "All AI models failed:\n" + "\n".join(errors)
        raise Exception(error_msg)

    async def process_query(self, query: str) -> str:
        """
        Main query processing pipeline with AI (Gemini with Groq and OpenRouter fallbacks)

        Args:
            query: User's question

        Returns:
            Final synthesized answer from AI
        """
        console.print(f"{self.ai_name} is thinking...")

        # Step 1: AI analyzes the query to determine what data sources are needed
        with console.status("Analyzing your question..."):
            analysis = await self._safe_ai_call('analyze_query', query)

        console.print(f"Understanding: {analysis.get('intent', '')}")
        if analysis.get('location'):
            console.print(f"Location detected: {analysis['location']}")

        # Handle code generation requests
        if analysis.get('needsCodeGeneration'):
            if analysis.get('codeType') == 'pyqgis' or 'pyqgis' in query.lower() or 'satellite' in query.lower():
                console.print("Generating PyQGIS script...")
                with console.status("Creating satellite processing script..."):
                    # Import here to avoid circular dependency
                    from src.utils.code_generator import generate_pyqgis_script, save_script
                    script = generate_pyqgis_script()
                    filepath = save_script(script, 'generated_scripts')

                return f"""I've generated a PyQGIS script for automated satellite imagery processing!

**Script saved to:** {filepath}

**What it does:**
• Loads all satellite images (Landsat/Sentinel-2) from a folder
• Calculates NDVI (vegetation health index)
• Clips images to your regional boundary shapefile
• Exports results as GeoTIFF files

**Next steps:**
1. Open QGIS Desktop
2. Go to Plugins → Python Console
3. Load and run the script (update the file paths first)

The script is fully commented and ready to use. Would you like me to explain any specific part of it?"""

            # For other code requests, use AI
            console.print("Providing coding assistance...")
            return await self._safe_ai_call('answer_directly', query)

        # Check if any external data is needed
        needs_external_data = (
            analysis.get('needsWebSearch') or
            analysis.get('needsWeatherData') or
            analysis.get('needsAgriculturalData')
        )

        # If no external data is needed, AI answers directly using its knowledge
        if not needs_external_data:
            console.print("Answering from knowledge base...")
            return await self._safe_ai_call('answer_directly', query)

        # Step 2: Fetch data from relevant sources
        aggregated_data = {
            'query': query,
            'analysis': analysis,
            'sources': {}
        }

        # Fetch web search results if needed (Poe -> DuckDuckGo -> Wikipedia -> Mock fallback chain)
        if analysis.get('needsWebSearch'):
            keywords = analysis.get('searchKeywords', analysis.get('keywords', [query]))
            with console.status(f"Searching the web for: {', '.join(keywords)}..."):
                try:
                    search_results = await self.web_search.search(query, keywords)
                    aggregated_data['sources']['webSearch'] = search_results

                    source = search_results.get('source', 'unknown')
                    if search_results.get('mock'):
                        console.print("Using mock web search (configure search providers for real results)")
                    elif source == 'poe':
                        console.print("Found information via Poe Web-Search")
                    elif source == 'duckduckgo':
                        console.print("Found information via DuckDuckGo")
                    elif source == 'wikipedia':
                        console.print("Found information via Wikipedia")
                    else:
                        console.print("Found up-to-date information")
                except Exception as e:
                    console.print(f"Web search failed: {e}")

        # Fetch weather data if needed
        if analysis.get('needsWeatherData') and analysis.get('location'):
            with console.status(f"Checking weather for {analysis['location']}..."):
                try:
                    weather_data = await self.regional_data.get_weather_data(analysis['location'])
                    aggregated_data['sources']['weather'] = weather_data
                    console.print("Weather data retrieved")
                except Exception as e:
                    console.print(f"Weather data unavailable: {e}")

        # Fetch agricultural data if needed
        if analysis.get('needsAgriculturalData') and analysis.get('location'):
            with console.status(f"Fetching agricultural data for {analysis['location']}..."):
                try:
                    agri_data = await self.regional_data.get_agricultural_data(analysis['location'])
                    soil_data = await self.regional_data.get_soil_data(analysis['location'])
                    aggregated_data['sources']['agriculture'] = agri_data
                    aggregated_data['sources']['soil'] = soil_data
                    console.print("Agricultural data retrieved")
                except Exception as e:
                    console.print(f"Agricultural data unavailable: {e}")

        # Step 3: AI synthesizes all data into a natural, conversational response
        with console.status(f"{self.ai_name} is crafting your answer..."):
            final_response = await self._safe_ai_call('synthesize_response', query, aggregated_data)

        console.print("Ready!")
        return final_response
