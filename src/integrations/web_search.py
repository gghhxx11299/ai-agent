"""Web search integration with multiple fallbacks: Poe Web-Search bot, DuckDuckGo, and Wikipedia"""

import httpx
import json
from datetime import datetime
from config.config import Config

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False


class WebSearchIntegration:
    """Web search integration with multiple fallback options"""

    def __init__(self):
        self.ddgs_enabled = DDGS_AVAILABLE
        self.wikipedia_enabled = WIKIPEDIA_AVAILABLE
        self.poe_api_key = Config.POE_API_KEY
        self.poe_bot_name = Config.POE_BOT_NAME
        self.poe_api_url = Config.POE_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _search_wikipedia(self, query: str) -> dict:
        """
        Search Wikipedia for information (run in executor since wikipedia is synchronous)
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with Wikipedia search results
        """
        if not self.wikipedia_enabled:
            return None
            
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            def _sync_wikipedia_search():
                try:
                    # Search Wikipedia
                    search_results = wikipedia.search(query, results=3)
                    
                    if not search_results:
                        return None
                        
                    # Get page content for first result
                    try:
                        page = wikipedia.page(search_results[0], auto_suggest=False)
                        summary = wikipedia.summary(search_results[0], sentences=3, auto_suggest=False)
                        
                        return {
                            'success': True,
                            'source': 'wikipedia',
                            'query': query,
                            'results': {
                                'summary': summary,
                                'sources': [{
                                    'title': page.title,
                                    'url': page.url,
                                    'snippet': summary[:200] + '...'
                                }]
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                    except wikipedia.DisambiguationError as e:
                        # Try first option from disambiguation
                        try:
                            page = wikipedia.page(e.options[0], auto_suggest=False)
                            summary = wikipedia.summary(e.options[0], sentences=3, auto_suggest=False)
                            return {
                                'success': True,
                                'source': 'wikipedia',
                                'query': query,
                                'results': {
                                    'summary': summary,
                                    'sources': [{
                                        'title': page.title,
                                        'url': page.url,
                                        'snippet': summary[:200] + '...'
                                    }]
                                },
                                'timestamp': datetime.now().isoformat()
                            }
                        except Exception:
                            return None
                    except Exception:
                        return None
                except Exception as e:
                    print(f"Wikipedia search error: {e}")
                    return None
            
            return await loop.run_in_executor(None, _sync_wikipedia_search)
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return None

    async def _search_poe_bot(self, query: str, keywords: list = None) -> dict:
        """
        Search using Poe's Web-Search bot via API
        
        Args:
            query: Search query
            keywords: Additional keywords
            
        Returns:
            Dictionary with search results from Poe bot
        """
        if not self.poe_api_key:
            return None
            
        try:
            # Enhance query with keywords
            enhanced_query = query
            if keywords:
                enhanced_query = f"{query} {' '.join(keywords[:3])}"
            
            # Poe API endpoint - try different formats
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Try different Poe API formats
            payloads = [
                {
                    'message': enhanced_query,
                    'bot': self.poe_bot_name,
                    'api_key': self.poe_api_key
                },
                {
                    'query': enhanced_query,
                    'bot': self.poe_bot_name,
                    'api_key': self.poe_api_key
                },
                {
                    'message': enhanced_query,
                    'bot_handle': self.poe_bot_name.lower().replace('-', '_'),
                    'api_key': self.poe_api_key
                }
            ]
            
            for payload in payloads:
                try:
                    # Try with API key in header
                    headers_with_auth = headers.copy()
                    headers_with_auth['Authorization'] = f'Bearer {self.poe_api_key}'
                    
                    response = await self.client.post(
                        f"{self.poe_api_url}query",
                        headers=headers_with_auth,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        # Safe JSON parsing
                        try:
                            data = response.json()
                        except (ValueError, json.JSONDecodeError):
                            # Try to parse as text
                            response_text = response.text if hasattr(response, 'text') else str(response.content)
                            from src.utils.json_parser import safe_json_loads
                            data = safe_json_loads(response_text) or {}
                        
                        # Parse Poe response - handle different response formats
                        text_response = ''
                        if isinstance(data, dict):
                            text_response = data.get('text', '') or data.get('response', '') or data.get('message', '')
                            if isinstance(text_response, dict):
                                text_response = text_response.get('text', '') or str(text_response)
                        else:
                            text_response = str(data)
                        
                        if text_response:
                            return {
                                'success': True,
                                'source': 'poe',
                                'query': enhanced_query,
                                'results': {
                                    'summary': text_response[:500] if len(text_response) > 500 else text_response,
                                    'sources': [{
                                        'title': f"Poe Web-Search: {enhanced_query}",
                                        'url': '',
                                        'snippet': text_response[:300] if len(text_response) > 300 else text_response
                                    }]
                                },
                                'timestamp': datetime.now().isoformat()
                            }
                except Exception as e:
                    continue
            
            # If all formats failed, return None
            return None
                
        except Exception as e:
            print(f"Poe bot search error: {e}")
            return None

    async def _search_duckduckgo(self, query: str, keywords: list = None) -> dict:
        """
        Search using DuckDuckGo
        
        Args:
            query: Search query
            keywords: Additional keywords
            
        Returns:
            Dictionary with DuckDuckGo search results
        """
        if not self.ddgs_enabled:
            return None
            
        try:
            # Enhance query with keywords
            enhanced_query = query
            if keywords:
                enhanced_query = f"{query} {' '.join(keywords[:3])}"
            
            # Use DuckDuckGo search (synchronous, but fast)
            import asyncio
            loop = asyncio.get_event_loop()
            
            def _sync_ddgs_search():
                with DDGS() as ddgs:
                    return list(ddgs.text(enhanced_query, max_results=5))
            
            results = await loop.run_in_executor(None, _sync_ddgs_search)
            
            if not results:
                return None
                
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
                'source': 'duckduckgo',
                'query': enhanced_query,
                'results': {
                    'summary': summary,
                    'sources': formatted_results
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return None

    async def search(self, query: str, keywords: list = None) -> dict:
        """
        Perform a web search with multiple fallbacks:
        1. Poe Web-Search bot (if API key available)
        2. DuckDuckGo (if available)
        3. Wikipedia (if available)
        4. Mock results (fallback)
        
        Args:
            query: Search query
            keywords: Additional keywords to enhance search
            
        Returns:
            Dictionary with search results
        """
        # Try Poe bot first (best results)
        if self.poe_api_key:
            result = await self._search_poe_bot(query, keywords)
            if result and result.get('success'):
                return result
        
        # Try DuckDuckGo second
        if self.ddgs_enabled:
            result = await self._search_duckduckgo(query, keywords)
            if result and result.get('success'):
                return result
        
        # Try Wikipedia third
        if self.wikipedia_enabled:
            result = await self._search_wikipedia(query)
            if result and result.get('success'):
                return result
        
        # Fallback to mock results
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
            'source': 'mock',
            'query': query,
            'results': {
                'summary': f'Mock search results for: "{query}". Configure search providers for real results.',
                'sources': [
                    {
                        'title': 'Example Source 1',
                        'url': 'https://example.com/1',
                        'snippet': 'This is a mock search result. Configure Poe API key, install ddgs, or install wikipedia package for real results.'
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


# Backward compatibility alias
PoeIntegration = WebSearchIntegration
