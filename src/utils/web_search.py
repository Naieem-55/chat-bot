"""Web search utility for fallback when no relevant documents found."""

import requests
from typing import List, Dict, Optional
import logging
import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebSearcher:
    """Search the web for information when local documents don't have answers."""

    def __init__(self, max_results: int = 5):
        """
        Initialize web searcher.

        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_duckduckgo(self, query: str) -> List[Dict]:
        """
        Search using DuckDuckGo HTML (no API key needed).

        Args:
            query: Search query

        Returns:
            List of search results with title, snippet, and url
        """
        try:
            # Use DuckDuckGo HTML search
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"DuckDuckGo search failed with status {response.status_code}")
                return []

            # Parse results from HTML
            results = self._parse_duckduckgo_html(response.text)
            return results[:self.max_results]

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    def _parse_duckduckgo_html(self, html: str) -> List[Dict]:
        """
        Parse DuckDuckGo HTML search results.

        Args:
            html: HTML content from DuckDuckGo

        Returns:
            List of parsed search results
        """
        results = []

        # Find all result blocks
        # DuckDuckGo HTML format: <a class="result__a" href="...">title</a>
        # and <a class="result__snippet">snippet</a>

        # Pattern for result links
        link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*(?:<[^>]*>[^<]*</[^>]*>)*[^<]*)</a>'

        links = re.findall(link_pattern, html)
        snippets = re.findall(snippet_pattern, html)

        for i, (url, title) in enumerate(links):
            snippet = snippets[i] if i < len(snippets) else ""
            # Clean up HTML tags from snippet
            snippet = re.sub(r'<[^>]+>', '', snippet)
            snippet = snippet.strip()

            if url and title:
                # DuckDuckGo uses redirect URLs, extract actual URL
                if 'uddg=' in url:
                    actual_url = re.search(r'uddg=([^&]+)', url)
                    if actual_url:
                        from urllib.parse import unquote
                        url = unquote(actual_url.group(1))

                results.append({
                    'title': title.strip(),
                    'snippet': snippet,
                    'url': url,
                    'source': 'web_search'
                })

        return results

    def search(self, query: str) -> List[Dict]:
        """
        Perform web search.

        Args:
            query: Search query

        Returns:
            List of search results
        """
        logger.info(f"Performing web search for: {query}")
        results = self.search_duckduckgo(query)
        logger.info(f"Found {len(results)} web results")
        return results

    def format_results_as_context(self, results: List[Dict]) -> str:
        """
        Format search results as context for the LLM.

        Args:
            results: List of search results

        Returns:
            Formatted context string
        """
        if not results:
            return "No web search results found."

        context_parts = []
        for i, result in enumerate(results, 1):
            context_part = f"[Web Result {i}] {result['title']}\n"
            if result['snippet']:
                context_part += f"{result['snippet']}\n"
            context_part += f"Source: {result['url']}"
            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    def get_search_metadata(self, results: List[Dict]) -> List[Dict]:
        """
        Get metadata from search results for display.

        Args:
            results: List of search results

        Returns:
            List of metadata dictionaries
        """
        metadata = []
        for result in results:
            metadata.append({
                'source': result['url'],
                'category': 'Web Search',
                'relevance_score': 0.8,  # Default score for web results
                'excerpt': result['snippet'][:200] + '...' if len(result['snippet']) > 200 else result['snippet'],
                'full_text': result['snippet'],
                'title': result['title'],
                'is_web_result': True
            })
        return metadata


# Global instance
web_searcher = WebSearcher()


def search_web(query: str) -> tuple:
    """
    Convenience function to search web and get formatted results.

    Args:
        query: Search query

    Returns:
        Tuple of (context_string, metadata_list, raw_results)
    """
    results = web_searcher.search(query)
    context = web_searcher.format_results_as_context(results)
    metadata = web_searcher.get_search_metadata(results)
    return context, metadata, results
