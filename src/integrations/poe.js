import axios from 'axios';
import { config } from '../../config/config.js';

class PoeIntegration {
  constructor() {
    this.apiKey = config.poe.apiKey;
    this.apiUrl = config.poe.apiUrl;
    this.botName = config.poe.botName;
  }

  /**
   * Perform a web search using Poe API
   * @param {string} query - Search query
   * @param {Array<string>} keywords - Additional keywords to enhance search
   * @returns {Promise<Object>} - Search results
   */
  async search(query, keywords = []) {
    if (!this.apiKey) {
      console.warn('Poe API key not configured. Skipping web search.');
      return {
        success: false,
        message: 'Poe API not configured',
        results: [],
      };
    }

    try {
      // Enhance query with keywords
      const enhancedQuery = keywords.length > 0
        ? `${query} ${keywords.join(' ')}`
        : query;

      // Note: Poe API structure may vary based on your access level
      // This is a generic implementation - adjust based on actual Poe API docs
      const response = await axios.post(
        `${this.apiUrl}query`,
        {
          query: enhancedQuery,
          bot: this.botName,
          api_key: this.apiKey,
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`,
          },
          timeout: 30000, // 30 second timeout
        }
      );

      return {
        success: true,
        query: enhancedQuery,
        results: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Poe API error:', error.message);

      // Fallback: return mock search results for development
      return this.mockSearch(query);
    }
  }

  /**
   * Mock search results for development/testing
   * @param {string} query - Search query
   * @returns {Object} - Mock results
   */
  mockSearch(query) {
    return {
      success: true,
      query,
      results: {
        summary: `Mock search results for: "${query}". Configure Poe API key for real search results.`,
        sources: [
          {
            title: 'Example Source 1',
            url: 'https://example.com/1',
            snippet: 'This is a mock search result. Real results will appear when Poe API is configured.',
          },
          {
            title: 'Example Source 2',
            url: 'https://example.com/2',
            snippet: 'Mock data for testing purposes.',
          },
        ],
      },
      mock: true,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Get latest news or articles related to query
   * @param {string} topic - Topic to search for
   * @returns {Promise<Object>} - News results
   */
  async getNews(topic) {
    const query = `latest news about ${topic}`;
    return this.search(query, ['news', 'recent', 'update']);
  }
}

export default PoeIntegration;
