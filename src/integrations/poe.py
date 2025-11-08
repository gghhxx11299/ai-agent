"""Web search integration using DuckDuckGo (free, no API key required)"""

from datetime import datetime

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("⚠️  ddgs not installed. Install with: pip install ddgs")


class PoeIntegration:
    """Web search integration using DuckDuckGo (free, no API key needed)"""

    def __init__(self):
        self.search_enabled = DDGS_AVAILABLE

    async def search(self, query: str, keywords: list = None) -> dict:
        """
        Perform a web search using DuckDuckGo

        Args:
            query: Search query
            keywords: Additional keywords to enhance search

        Returns:
            Dictionary with search results
        """
        if not self.search_enabled:
            print("⚠️  DuckDuckGo search not available. Using mock search.")
            return self._mock_search(query)

        try:
            # Enhance query with keywords
            enhanced_query = query
            if keywords:
                enhanced_query = f"{query} {' '.join(keywords[:3])}"  # Limit to 3 keywords

            # Use DuckDuckGo search
            with DDGS() as ddgs:
                results = list(ddgs.text(enhanced_query, max_results=5))

            if not results:
                return self._mock_search(query)

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', '')
                })

            # Create summary from top results
            summary = f"Found {len(formatted_results)} relevant sources about {query}. "
            if formatted_results:
                summary += f"Top result: {formatted_results[0]['snippet'][:150]}..."

            return {
                'success': True,
                'query': enhanced_query,
                'results': {
                    'summary': summary,
                    'sources': formatted_results
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Web search error: {e}")
            return self._mock_search(query)

    def _mock_search(self, query: str) -> dict:
        """
        Mock search results for development/testing

        Args:
            query: Search query

        Returns:
            Dictionary with mock results
        """
        return {
            'success': True,
            'query': query,
            'results': {
                'summary': f'Mock search results for: "{query}". Configure Poe API key for real search results.',
                'sources': [
                    {
                        'title': 'Example Source 1',
                        'url': 'https://example.com/1',
                        'snippet': 'This is a mock search result. Real results will appear when Poe API is configured.'
                    },
                    {
                        'title': 'Example Source 2',
                        'url': 'https://example.com/2',
                        'snippet': 'Mock data for testing purposes.'
                    }
                ]
            },
            'mock': True,
            'timestamp': datetime.now().isoformat()
        }

    async def get_news(self, topic: str) -> dict:
        """
        Get latest news or articles related to topic

        Args:
            topic: Topic to search for

        Returns:
            Dictionary with news results
        """
        query = f"latest news about {topic}"
        return await self.search(query, ['news', 'recent', 'update'])
