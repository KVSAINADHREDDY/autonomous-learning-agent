"""
Search tools for gathering learning content.
Supports Tavily (primary), SerpAPI, and DuckDuckGo (fallback).
"""
import os
from typing import List, Dict, Any

# Try importing search libraries
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False


class TavilySearch:
    """Tavily API search - Best quality, 100 free searches/month."""
    
    def __init__(self):
        """Initialize Tavily search."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment")
        
        if not TAVILY_AVAILABLE:
            raise ImportError("tavily-python not installed. Run: pip install tavily-python")
        
        self.client = TavilyClient(api_key=api_key)
        print("✅ Tavily search initialized")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using Tavily API.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with title, url, and content
        """
        try:
            # Tavily search with content extraction
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
            
            results = []
            
            # Add the AI-generated answer if available
            if response.get("answer"):
                results.append({
                    "title": "AI Summary",
                    "url": "",
                    "content": response["answer"],
                    "snippet": response["answer"][:200]
                })
            
            # Add search results
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "snippet": result.get("content", "")[:200] if result.get("content") else ""
                })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []


class DuckDuckGoSearch:
    """DuckDuckGo search - Free, no API key needed."""
    
    def __init__(self):
        """Initialize DuckDuckGo search."""
        if not DUCKDUCKGO_AVAILABLE:
            raise ImportError("duckduckgo-search not installed. Run: pip install duckduckgo-search")
        self.ddgs = DDGS()
        print("✅ DuckDuckGo search initialized")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "content": result.get("body", ""),
                    "snippet": result.get("body", "")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []


def get_search_tool():
    """Get the best available search tool."""
    # Try Tavily first (best quality)
    try:
        return TavilySearch()
    except (ValueError, ImportError) as e:
        print(f"Tavily not available: {e}")
    
    # Fallback to DuckDuckGo
    try:
        return DuckDuckGoSearch()
    except ImportError as e:
        print(f"DuckDuckGo not available: {e}")
    
    return None


def search_for_learning_content(
    topic: str,
    objectives: List[str],
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for learning content using available search tools.
    
    Creates multiple diverse queries for comprehensive coverage.
    
    Args:
        topic: The learning topic
        objectives: List of learning objectives
        max_results: Maximum total results to return
        
    Returns:
        List of search results with title, url, content, and snippet
    """
    # Create diverse queries
    queries = [
        f"{topic} tutorial beginner guide",
        f"{topic} explained simply with examples",
        f"what is {topic} definition concepts",
    ]
    
    # Add objective-specific queries
    if objectives:
        queries.append(f"{topic} {objectives[0]}")
    
    # Get search tool
    search_tool = get_search_tool()
    
    if not search_tool:
        print("⚠️ No search tools available")
        return []
    
    all_results = []
    seen_urls = set()
    
    for query in queries:
        print(f"🔍 Searching: {query}")
        results = search_tool.search(query, max_results=max(2, max_results // len(queries)))
        
        for result in results:
            url = result.get('url', '')
            # Deduplicate by URL
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            
            all_results.append(result)
            
            if len(all_results) >= max_results:
                break
        
        if len(all_results) >= max_results:
            break
    
    print(f"📚 Found {len(all_results)} unique results")
    return all_results[:max_results]
