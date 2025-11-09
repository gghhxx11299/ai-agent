"""Gemini AI integration for conversational interface"""

import json
import re
import google.generativeai as genai
from config.config import Config
from src.utils.json_parser import safe_json_loads, safe_extract_json_from_text


class GeminiIntegration:
    """Gemini AI integration for query analysis and response synthesis"""

    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    async def analyze_query(self, query: str) -> dict:
        """
        Analyze a query to determine what data sources should be called

        Args:
            query: User's question

        Returns:
            Dictionary with analysis results including data source needs
        """
        prompt = f"""You are an intelligent query analyzer. Analyze this user query and determine what data sources are needed.

User Query: "{query}"

Determine if the query needs:
1. **Web Search**: Recent news, current events, latest information, trends, or anything requiring up-to-date internet data
2. **Weather Data**: Current weather, forecasts, temperature, precipitation, climate information
3. **Agricultural Data**: Crop information, farming advice, soil data, planting recommendations
4. **Code Generation**: Requests to generate scripts, code, or automate GIS/satellite processing tasks

Extract:
- Intent: What the user is asking for
- Location: Any geographic location mentioned
- Timeframe: Time period if mentioned
- Search Keywords: 3-5 specific keywords for web search (if needed) - focus on main topics, technical terms, and specifics
- Code Request: Detect if user wants to generate code (PyQGIS, Python scripts, etc.)

Return ONLY a JSON object in this exact format:
{{
  "intent": "brief description",
  "needsWebSearch": true/false,
  "needsWeatherData": true/false,
  "needsAgriculturalData": true/false,
  "needsCodeGeneration": true/false,
  "codeType": "pyqgis/python/general or null",
  "location": "location name or null",
  "timeframe": "timeframe or null",
  "searchKeywords": ["keyword1", "keyword2", "keyword3"],
  "requiresCurrentData": true/false
}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text if hasattr(response, 'text') and response.text else str(response)

            # Safely parse JSON with EOF error handling
            parsed_json = safe_extract_json_from_text(text)
            if parsed_json:
                return parsed_json

            # Fallback to safe JSON parsing
            parsed_json = safe_json_loads(text)
            if parsed_json:
                return parsed_json

        except Exception as e:
            import logging
            logging.warning(f"Error analyzing query with Gemini: {e}")
        
        # Return default analysis if parsing fails
        return {
            "intent": query,
            "needsWebSearch": "latest" in query.lower() or "recent" in query.lower() or "current" in query.lower(),
            "needsWeatherData": any(word in query.lower() for word in ['weather', 'temperature', 'rain', 'forecast', 'climate']),
            "needsAgriculturalData": any(word in query.lower() for word in ['crop', 'farm', 'agriculture', 'soil', 'planting']),
            "needsCodeGeneration": any(word in query.lower() for word in ['code', 'script', 'generate', 'python', 'pyqgis']),
            "codeType": 'pyqgis' if 'pyqgis' in query.lower() or 'qgis' in query.lower() else ('python' if 'python' in query.lower() else None),
            "location": None,
            "timeframe": None,
            "searchKeywords": [w for w in query.split() if len(w) > 3][:5],
            "requiresCurrentData": False,
        }

    async def synthesize_response(self, query: str, data: dict) -> str:
        """
        Synthesize a final answer from aggregated data using Gemini

        Args:
            query: Original user query
            data: Aggregated data from various sources

        Returns:
            Synthesized response as a string
        """
        has_web_data = data.get('sources', {}).get('webSearch', {}).get('success', False)
        has_weather_data = data.get('sources', {}).get('weather', {}).get('success', False)
        has_agri_data = data.get('sources', {}).get('agriculture', {}).get('success', False)

        context_info = ''

        if has_web_data:
            web_data = data['sources']['webSearch']
            context_info += '\n**Web Search Results:**\n'
            if web_data.get('results', {}).get('summary'):
                context_info += web_data['results']['summary'] + '\n'
            if web_data.get('results', {}).get('sources'):
                for idx, source in enumerate(web_data['results']['sources'], 1):
                    context_info += f"{idx}. {source['title']}: {source['snippet']}\n"

        if has_weather_data:
            weather = data['sources']['weather']
            context_info += '\n**Weather Data:**\n'
            context_info += f"Location: {weather['location']}\n"
            context_info += f"Temperature: {weather['current']['temperature']}°C\n"
            context_info += f"Conditions: {weather['current']['description']}\n"
            context_info += f"Humidity: {weather['current']['humidity']}%\n"

        if has_agri_data:
            agri_data = data['sources']['agriculture']['data']
            context_info += '\n**Agricultural Data:**\n'
            context_info += json.dumps(agri_data, indent=2) + '\n'

        # Build the context message
        if context_info:
            context_msg = f"I've gathered this real-time information for you:\n{context_info}"
        else:
            context_msg = "I can answer this from my general knowledge."

        prompt = f"""You are Gemini, a friendly AI assistant having a natural conversation with a user. You have access to real-time data sources and can provide up-to-date, accurate information.

The user asked: "{query}"

{context_msg}

**Instructions for your response:**
- Have a natural, conversational tone - like you're chatting with a friend
- Synthesize the data into a clear, coherent answer
- When you have current data (from web search, weather, etc.), mention it naturally
  Example: "According to recent reports..." or "The latest weather data shows..."
- Be specific and helpful
- Use formatting (bullet points, sections) when it makes the answer clearer
- If multiple sources provided data, weave them together smoothly
- Be encouraging and supportive

Provide your response in a natural, friendly way:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text
            return str(response)
        except Exception as e:
            import logging
            logging.error(f"Error synthesizing response with Gemini: {e}")
            return f"I encountered an error while processing your query. Please try again or rephrase your question."

    async def answer_directly(self, query: str) -> str:
        """
        Answer query directly using Gemini's knowledge (when no external data is needed)

        Args:
            query: User's question

        Returns:
            Direct answer as a string
        """
        prompt = f"""You are Gemini, a friendly and knowledgeable AI assistant. You specialize in agriculture, weather, regional information, and general knowledge. You're conversational, helpful, and provide accurate information.

User asks: {query}

Provide a natural, conversational response as if you're having a friendly chat. Be informative but not overly formal. Use bullet points or sections when it helps clarity.

Your response:"""

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text
            return str(response)
        except Exception as e:
            import logging
            logging.error(f"Error in direct answer with Gemini: {e}")
            return f"I'm sorry, I encountered an error while processing your question. Please try again."
