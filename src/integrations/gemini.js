import { GoogleGenerativeAI } from '@google/generative-ai';
import { config } from '../../config/config.js';

class GeminiIntegration {
  constructor() {
    this.genAI = new GoogleGenerativeAI(config.gemini.apiKey);
    this.model = this.genAI.getGenerativeModel({ model: config.gemini.model });
  }

  /**
   * Analyze a query to determine what data sources should be called
   * @param {string} query - User's question
   * @returns {Promise<Object>} - Analysis with data sources needed
   */
  async analyzeQuery(query) {
    const prompt = `You are an intelligent query analyzer. Analyze this user query and determine what data sources are needed.

User Query: "${query}"

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
{
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
}`;

    try {
      const result = await this.model.generateContent(prompt);
      const text = result.response.text();

      // Extract JSON from response (handling markdown code blocks)
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      return JSON.parse(text);
    } catch (error) {
      console.error('Error analyzing query:', error.message);
      // Return default analysis if parsing fails
      return {
        intent: query,
        needsWebSearch: query.toLowerCase().includes('latest') || query.toLowerCase().includes('recent'),
        needsWeatherData: false,
        needsAgriculturalData: false,
        location: null,
        timeframe: null,
        searchKeywords: query.split(' ').filter(w => w.length > 3).slice(0, 5),
        requiresCurrentData: false,
      };
    }
  }

  /**
   * Synthesize a final answer from aggregated data using Gemini as the conversational interface
   * @param {string} query - Original user query
   * @param {Object} data - Aggregated data from various sources
   * @returns {Promise<string>} - Synthesized response
   */
  async synthesizeResponse(query, data) {
    const hasWebData = data.sources?.webSearch?.success;
    const hasWeatherData = data.sources?.weather?.success;
    const hasAgriData = data.sources?.agriculture?.success;

    let contextInfo = '';

    if (hasWebData) {
      contextInfo += '\n**Web Search Results:**\n';
      if (data.sources.webSearch.results?.summary) {
        contextInfo += data.sources.webSearch.results.summary + '\n';
      }
      if (data.sources.webSearch.results?.sources) {
        data.sources.webSearch.results.sources.forEach((source, idx) => {
          contextInfo += `${idx + 1}. ${source.title}: ${source.snippet}\n`;
        });
      }
    }

    if (hasWeatherData) {
      contextInfo += '\n**Weather Data:**\n';
      contextInfo += `Location: ${data.sources.weather.location}\n`;
      contextInfo += `Temperature: ${data.sources.weather.current.temperature}°C\n`;
      contextInfo += `Conditions: ${data.sources.weather.current.description}\n`;
      contextInfo += `Humidity: ${data.sources.weather.current.humidity}%\n`;
    }

    if (hasAgriData) {
      contextInfo += '\n**Agricultural Data:**\n';
      contextInfo += JSON.stringify(data.sources.agriculture.data, null, 2) + '\n';
    }

    const prompt = `You are Gemini, a friendly AI assistant having a natural conversation with a user. You have access to real-time data sources and can provide up-to-date, accurate information.

The user asked: "${query}"

${contextInfo ? `I've gathered this real-time information for you:\n${contextInfo}` : 'I can answer this from my general knowledge.'}

**Instructions for your response:**
- Have a natural, conversational tone - like you're chatting with a friend
- Synthesize the data into a clear, coherent answer
- When you have current data (from web search, weather, etc.), mention it naturally
  Example: "According to recent reports..." or "The latest weather data shows..."
- Be specific and helpful
- Use formatting (bullet points, sections) when it makes the answer clearer
- If multiple sources provided data, weave them together smoothly
- Be encouraging and supportive

Provide your response in a natural, friendly way:`;

    try {
      const result = await this.model.generateContent(prompt);
      return result.response.text();
    } catch (error) {
      console.error('Error synthesizing response:', error.message);
      return `I encountered an error while processing your query: ${error.message}`;
    }
  }

  /**
   * Answer query directly using Gemini's knowledge (when no external data is needed)
   * @param {string} query - User's question
   * @returns {Promise<string>} - Direct answer
   */
  async answerDirectly(query) {
    const prompt = `You are Gemini, a friendly and knowledgeable AI assistant. You specialize in agriculture, weather, regional information, and general knowledge. You're conversational, helpful, and provide accurate information.

User asks: ${query}

Provide a natural, conversational response as if you're having a friendly chat. Be informative but not overly formal. Use bullet points or sections when it helps clarity.

Your response:`;

    try {
      const result = await this.model.generateContent(prompt);
      return result.response.text();
    } catch (error) {
      console.error('Error in direct answer:', error.message);
      return `I'm sorry, I encountered an error while processing your question: ${error.message}`;
    }
  }

  /**
   * Simple chat completion for general queries
   * @param {string} message - User message
   * @returns {Promise<string>} - AI response
   */
  async chat(message) {
    try {
      const result = await this.model.generateContent(message);
      return result.response.text();
    } catch (error) {
      console.error('Error in chat:', error.message);
      return `Error: ${error.message}`;
    }
  }
}

export default GeminiIntegration;
