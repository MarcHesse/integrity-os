"""
WIKIPEDIA CRAWLER - ROBUST VERSION
==================================

Crawls Wikipedia API with proper error handling, rate limiting, and retry logic.

Features:
- Automatic retry on failures (3 attempts)
- Exponential backoff
- User-Agent header
- Proper error handling
- Graph integration

Usage:
    from crawlers.wikipedia_crawler import WikipediaCrawler
    
    crawler = WikipediaCrawler(graph)
    stats = crawler.crawl_topic('Python_(programming_language)', max_pages=10)
"""

import requests
import json
from typing import Dict, List, Optional
import time
from datetime import datetime
from urllib.parse import unquote  # Add URL decoding


class WikipediaCrawler:
    """
    Robust Wikipedia crawler with automatic retry and error handling
    """
    
    def __init__(self, graph, language='en', verbose=True):
        """
        Initialize crawler
        
        Args:
            graph: CausalGraph instance to populate
            language: Wikipedia language code (default: 'en')
            verbose: Print progress messages
        """
        self.graph = graph
        self.language = language
        self.verbose = verbose
        
        # API endpoint
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        
        # Cache to avoid duplicate requests
        self.crawled_pages = set()
        self.failed_pages = set()
        
        # Rate limiting (be nice to Wikipedia!)
        self.request_delay = 2.0  # Increased to 2 seconds
        self.last_request_time = 0
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 5.0  # Initial retry delay
        
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict, attempt: int = 1) -> Optional[Dict]:
        """
        Make API request with retry logic
        
        Args:
            params: API parameters
            attempt: Current attempt number
            
        Returns:
            JSON response or None on failure
        """
        headers = {
            'User-Agent': 'IntegrityOS-Research/1.0 (Educational; info@marchesse.de)'
        }
        
        try:
            self._rate_limit()
            
            response = requests.get(
                self.api_url,
                params=params,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 429:  # Too many requests
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    if self.verbose:
                        print(f"   Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return self._make_request(params, attempt + 1)
                return None
            
            if response.status_code != 200:
                if attempt < self.max_retries:
                    if self.verbose:
                        print(f"   HTTP {response.status_code}, retrying...")
                    time.sleep(self.retry_delay)
                    return self._make_request(params, attempt + 1)
                return None
            
            return response.json()
            
        except requests.Timeout:
            if attempt < self.max_retries:
                if self.verbose:
                    print(f"   Timeout, retrying (attempt {attempt}/{self.max_retries})...")
                time.sleep(self.retry_delay)
                return self._make_request(params, attempt + 1)
            return None
            
        except requests.ConnectionError:
            if attempt < self.max_retries:
                if self.verbose:
                    print(f"   Connection error, retrying...")
                time.sleep(self.retry_delay * 2)
                return self._make_request(params, attempt + 1)
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"   Unexpected error: {e}")
            return None
    
    def crawl_topic(self, start_page: str, max_pages: int = 10, max_depth: int = 1) -> Dict:
        """
        Crawl a Wikipedia topic and related pages
        
        Args:
            start_page: Starting Wikipedia page title
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum link depth to follow
            
        Returns:
            Statistics dictionary
        """
        if self.verbose:
            print(f"\\n🕷️  Wikipedia Crawler")
            print(f"   Topic: {start_page}")
            print(f"   Max Pages: {max_pages}, Max Depth: {max_depth}\\n")
        
        stats = {
            'pages_crawled': 0,
            'entities_added': 0,
            'relations_added': 0,
            'failed': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # BFS queue: (page_title, depth)
        queue = [(start_page, 0)]
        
        while queue and stats['pages_crawled'] < max_pages:
            current_page, depth = queue.pop(0)
            
            # Skip if already crawled or too deep
            if current_page in self.crawled_pages or depth > max_depth:
                continue
            
            if self.verbose:
                print(f"[{stats['pages_crawled']+1}/{max_pages}] {current_page} (depth {depth})")
            
            # Crawl page
            result = self._crawl_page(current_page)
            
            if result['success']:
                stats['pages_crawled'] += 1
                stats['entities_added'] += result['entities_added']
                stats['relations_added'] += result['relations_added']
                
                self.crawled_pages.add(current_page)
                
                # Add linked pages to queue (if not too deep)
                if depth < max_depth:
                    for link in result.get('links', [])[:5]:  # Top 5 links
                        if link not in self.crawled_pages:
                            queue.append((link, depth + 1))
            else:
                stats['failed'] += 1
                self.failed_pages.add(current_page)
                if self.verbose:
                    print(f"   ✗ Failed: {result.get('error', 'Unknown')}")
        
        stats['end_time'] = datetime.now().isoformat()
        
        if self.verbose:
            print(f"\\n✅ Crawl Complete!")
            print(f"   Pages: {stats['pages_crawled']}")
            print(f"   Entities: {stats['entities_added']}")
            print(f"   Relations: {stats['relations_added']}")
            print(f"   Failed: {stats['failed']}\\n")
        
        return stats
    
    def _crawl_page(self, page_title: str) -> Dict:
        """
        Crawl a single Wikipedia page
        
        Args:
            page_title: Wikipedia page title (may be URL-encoded)
            
        Returns:
            Result dictionary with success status and data
        """
        # URL-decode the title (handles C%2B%2B -> C++)
        page_title = unquote(page_title)
        
        params = {
            'action': 'parse',
            'page': page_title,
            'format': 'json',
            'prop': 'text|links|categories',
            'redirects': 1
        }
        
        data = self._make_request(params)
        
        if not data:
            return {'success': False, 'error': 'Request failed'}
        
        if 'error' in data:
            return {'success': False, 'error': data['error'].get('info', 'API error')}
        
        parse_data = data.get('parse', {})
        if not parse_data:
            return {'success': False, 'error': 'No parse data'}
        
        title = parse_data.get('title', page_title)
        links_data = parse_data.get('links', [])
        categories = parse_data.get('categories', [])
        
        # Extract links (main namespace only)
        links = []
        for link in links_data:
            link_title = link.get('*', '')
            ns = link.get('ns', 0)
            
            # Only main namespace (0), no special pages
            if ns == 0 and ':' not in link_title and not link_title.startswith('List of'):
                links.append(link_title)
        
        # Add to graph
        entities_added = 0
        relations_added = 0
        
        # Main node
        node_id = title.replace(' ', '_')
        
        if not self.graph.semantic.has_node(node_id):
            # Extract category info
            category_names = [cat.get('*', '').replace('Category:', '') 
                            for cat in categories[:3]]  # Top 3 categories
            
            self.graph.semantic.add_node(node_id,
                node_type='wikipedia_page',
                title=title,
                source='wikipedia',
                categories=category_names,
                crawled_at=datetime.now().isoformat()
            )
            entities_added += 1
        
        # Add links as nodes and edges
        for link in links[:10]:  # Limit to 10 links per page
            link_id = link.replace(' ', '_')
            
            # Add link node
            if not self.graph.semantic.has_node(link_id):
                self.graph.semantic.add_node(link_id,
                    node_type='wikipedia_page',
                    title=link,
                    source='wikipedia'
                )
                entities_added += 1
            
            # Add edge
            if not self.graph.semantic.has_edge(node_id, link_id):
                self.graph.semantic.add_edge(node_id, link_id,
                    relation='links_to',
                    confidence=0.7,
                    source='wikipedia'
                )
                relations_added += 1
        
        return {
            'success': True,
            'entities_added': entities_added,
            'relations_added': relations_added,
            'links': links
        }
    
    def get_statistics(self) -> Dict:
        """Get crawler statistics"""
        return {
            'pages_crawled': len(self.crawled_pages),
            'pages_failed': len(self.failed_pages),
            'success_rate': len(self.crawled_pages) / max(len(self.crawled_pages) + len(self.failed_pages), 1)
        }


# Test function
def test_crawler():
    """Test the Wikipedia crawler"""
    import sys
    sys.path.insert(0, '..')
    
    from core.causal_graph import CausalGraph
    
    print("\\n" + "="*60)
    print("WIKIPEDIA CRAWLER TEST")
    print("="*60)
    
    graph = CausalGraph()
    initial_nodes = graph.get_statistics()['semantic_nodes']
    
    print(f"\\nInitial nodes: {initial_nodes}")
    
    crawler = WikipediaCrawler(graph, verbose=True)
    
    # Test single page
    print("\\nTest 1: Single page (Python)")
    stats = crawler.crawl_topic('Python_(programming_language)', max_pages=1, max_depth=0)
    
    final_nodes = graph.get_statistics()['semantic_nodes']
    print(f"\\nFinal nodes: {final_nodes}")
    print(f"Nodes added: {final_nodes - initial_nodes}")
    
    if stats['pages_crawled'] > 0:
        print("\\n✅ Test PASSED - Crawler is working!")
    else:
        print("\\n❌ Test FAILED - No pages crawled")
    
    return stats


if __name__ == "__main__":
    test_crawler()
