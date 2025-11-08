"""Orchestrator for managing AI integrations and data flow"""

import asyncio
from rich.console import Console
from rich.spinner import Spinner
from rich import print as rprint
from src.integrations.gemini import GeminiIntegration
from src.integrations.groq import GroqIntegration
from src.integrations.openrouter import OpenRouterIntegration
from src.integrations.poe import PoeIntegration
from src.integrations.regional_data import RegionalDataIntegration
from config.config import Config

console = Console()


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
                console.print("[green]✓ Gemini initialized[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Gemini unavailable: {e}[/yellow]")

        # Try Groq second
        if Config.GROQ_API_KEY:
            try:
                groq = GroqIntegration()
                self.ai_models.append(("Groq", groq))
                console.print("[green]✓ Groq initialized[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Groq unavailable: {e}[/yellow]")

        # Try OpenRouter third
        if Config.OPENROUTER_API_KEY:
            try:
                openrouter = OpenRouterIntegration()
                self.ai_models.append(("OpenRouter", openrouter))
                console.print("[green]✓ OpenRouter initialized[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  OpenRouter unavailable: {e}[/yellow]")

        # Set the current AI to the first available model
        if self.ai_models:
            self.ai_name, self.current_ai = self.ai_models[0]
            console.print(f"[cyan]🤖 Using {self.ai_name} as primary AI[/cyan]\n")
        else:
            raise Exception("No AI models available. Please configure at least one API key (Gemini, Groq, or OpenRouter)")

        self.poe = PoeIntegration()
        self.regional_data = RegionalDataIntegration()

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
                    console.print(f"[yellow]⚠️  Switched to {name} as primary AI[/yellow]")
                    self.ai_name = name
                    self.current_ai = ai_instance
                    # Move successful model to front for future calls
                    self.ai_models.insert(0, self.ai_models.pop(idx))

                return result

            except Exception as e:
                errors.append(f"{name}: {str(e)}")
                if idx < len(self.ai_models) - 1:
                    console.print(f"[yellow]⚠️  {name} failed, trying next fallback...[/yellow]")

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
        console.print(f"\n[blue]🤖 {self.ai_name} is thinking...[/blue]\n")

        # Step 1: AI analyzes the query to determine what data sources are needed
        with console.status("[cyan]Analyzing your question..."):
            analysis = await self._safe_ai_call('analyze_query', query)

        console.print(f"[dim]💭 Understanding: {analysis['intent']}[/dim]")
        if analysis.get('location'):
            console.print(f"[dim]📍 Location detected: {analysis['location']}[/dim]")

        # Handle code generation requests
        if analysis.get('needsCodeGeneration'):
            if analysis.get('codeType') == 'pyqgis' or 'pyqgis' in query.lower() or 'satellite' in query.lower():
                console.print("[dim]🛰️  Generating PyQGIS script...[/dim]\n")
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
            console.print("[dim]💡 Providing coding assistance...[/dim]\n")
            return await self._safe_ai_call('answer_directly', query)

        # Check if any external data is needed
        needs_external_data = (
            analysis.get('needsWebSearch') or
            analysis.get('needsWeatherData') or
            analysis.get('needsAgriculturalData')
        )

        # If no external data is needed, AI answers directly using its knowledge
        if not needs_external_data:
            console.print("[dim]💡 Answering from knowledge base...[/dim]\n")
            return await self._safe_ai_call('answer_directly', query)

        # Step 2: Fetch data from relevant sources
        aggregated_data = {
            'query': query,
            'analysis': analysis,
            'sources': {}
        }

        # Fetch web search results if needed (Poe serves as Gemini's real-time data source)
        if analysis.get('needsWebSearch'):
            keywords = analysis.get('searchKeywords', analysis.get('keywords', [query]))
            with console.status(f"🔍 Searching the web for: {', '.join(keywords)}..."):
                try:
                    search_results = await self.poe.search(query, keywords)
                    aggregated_data['sources']['webSearch'] = search_results

                    if search_results.get('mock'):
                        console.print("[yellow]⚠️  Using mock web search (install duckduckgo-search for real results)[/yellow]")
                    else:
                        console.print("[green]✓[/green] Found up-to-date information")
                except Exception as e:
                    console.print(f"[red]✗[/red] Web search failed: {e}")

        # Fetch weather data if needed
        if analysis.get('needsWeatherData') and analysis.get('location'):
            with console.status(f"🌤️  Checking weather for {analysis['location']}..."):
                try:
                    weather_data = await self.regional_data.get_weather_data(analysis['location'])
                    aggregated_data['sources']['weather'] = weather_data
                    console.print("[green]✓[/green] Weather data retrieved")
                except Exception as e:
                    console.print(f"[red]✗[/red] Weather data unavailable: {e}")

        # Fetch agricultural data if needed
        if analysis.get('needsAgriculturalData') and analysis.get('location'):
            with console.status(f"🌾 Fetching agricultural data for {analysis['location']}..."):
                try:
                    agri_data = await self.regional_data.get_agricultural_data(analysis['location'])
                    soil_data = await self.regional_data.get_soil_data(analysis['location'])
                    aggregated_data['sources']['agriculture'] = agri_data
                    aggregated_data['sources']['soil'] = soil_data
                    console.print("[green]✓[/green] Agricultural data retrieved")
                except Exception as e:
                    console.print(f"[red]✗[/red] Agricultural data unavailable: {e}")

        # Step 3: AI synthesizes all data into a natural, conversational response
        with console.status(f"✨ {self.ai_name} is crafting your answer..."):
            final_response = await self._safe_ai_call('synthesize_response', query, aggregated_data)

        console.print("[green]✓ Ready![/green]")
        return final_response
