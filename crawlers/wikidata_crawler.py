"""
WIKIDATA CRAWLER - STRUCTURED DATA SOURCE
==========================================

Uses Wikidata Query Service (SPARQL) for structured knowledge extraction.
More reliable than Wikipedia parsing, returns clean entity-relationship data.

Features:
- SPARQL queries for structured data
- Entity metadata (labels, descriptions, properties)
- Relationships with confidence
- No HTML parsing needed
- Built-in rate limiting

Usage:
    from crawlers.wikidata_crawler import WikidataCrawler
    
    crawler = WikidataCrawler(graph)
    stats = crawler.crawl_entity('Q28865')  # Python (programming language)
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime


class WikidataCrawler:
    """
    Wikidata SPARQL crawler for structured knowledge extraction
    """
    
    def __init__(self, graph, verbose=True):
        """
        Initialize Wikidata crawler
        
        Args:
            graph: CausalGraph instance to populate
            verbose: Print progress messages
        """
        self.graph = graph
        self.verbose = verbose
        
        # Wikidata endpoints
        self.sparql_url = "https://query.wikidata.org/sparql"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData"
        
        # Cache
        self.crawled_entities = set()
        self.entity_cache = {}
        
        # Rate limiting
        self.request_delay = 1.5
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def _sparql_query(self, query: str) -> Optional[List[Dict]]:
        """
        Execute SPARQL query
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of result bindings or None on failure
        """
        headers = {
            'User-Agent': 'IntegrityOS-Research/1.0 (Educational; info@marchesse.de)',
            'Accept': 'application/json'
        }
        
        try:
            self._rate_limit()
            
            response = requests.get(
                self.sparql_url,
                params={'query': query, 'format': 'json'},
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                if self.verbose:
                    print(f"   SPARQL error: HTTP {response.status_code}")
                return None
            
            data = response.json()
            return data.get('results', {}).get('bindings', [])
            
        except Exception as e:
            if self.verbose:
                print(f"   SPARQL exception: {e}")
            return None
    
    def search_entity(self, search_term: str, language='en') -> Optional[str]:
        """
        Search for Wikidata entity ID by name
        
        Args:
            search_term: Entity name to search
            language: Language code
            
        Returns:
            Wikidata entity ID (e.g., 'Q28865') or None
        """
        # Build SPARQL query
        query = '''
        SELECT ?item ?itemLabel WHERE {{
            ?item rdfs:label "{}"@{}.
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{}". }}
        }}
        LIMIT 1
        '''.format(search_term, language, language)
        
        results = self._sparql_query(query)
        
        if not results:
            return None
        
        entity_uri = results[0].get('item', {}).get('value', '')
        # Extract Q-ID from URI
        if '/Q' in entity_uri:
            return 'Q' + entity_uri.split('/Q')[1]
        
        return None
    
    def crawl_entity(self, entity_id: str, max_relations: int = 20) -> Dict:
        """
        Crawl a Wikidata entity and its relationships
        
        Args:
            entity_id: Wikidata entity ID (e.g., 'Q28865')
            max_relations: Maximum relationships to extract
            
        Returns:
            Statistics dictionary
        """
        if self.verbose:
            print(f"\n🔍 Wikidata Crawler")
            print(f"   Entity: {entity_id}\n")
        
        stats = {
            'entities_added': 0,
            'relations_added': 0,
            'properties_extracted': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Get entity data
        entity_data = self._get_entity_data(entity_id)
        
        if not entity_data:
            if self.verbose:
                print(f"   ✗ Failed to fetch entity data")
            return stats
        
        # Add main entity to graph
        if self._add_entity_to_graph(entity_id, entity_data):
            stats['entities_added'] += 1
        
        # Get relationships
        relations = self._get_entity_relations(entity_id, max_relations)
        
        for rel in relations:
            # Add related entity
            related_id = rel['related_entity']
            related_data = self._get_entity_data(related_id)
            
            if related_data and self._add_entity_to_graph(related_id, related_data):
                stats['entities_added'] += 1
            
            # Add edge
            if self._add_relation_to_graph(entity_id, related_id, rel):
                stats['relations_added'] += 1
        
        self.crawled_entities.add(entity_id)
        stats['end_time'] = datetime.now().isoformat()
        
        if self.verbose:
            print(f"\n✅ Crawl Complete!")
            print(f"   Entities: {stats['entities_added']}")
            print(f"   Relations: {stats['relations_added']}\n")
        
        return stats
    
    def _get_entity_data(self, entity_id: str) -> Optional[Dict]:
        """Get entity metadata"""
        
        # Check cache
        if entity_id in self.entity_cache:
            return self.entity_cache[entity_id]
        
        # Build query
        query = '''
        SELECT ?label ?description WHERE {{
            wd:{} rdfs:label ?label.
            OPTIONAL {{ wd:{} schema:description ?description. }}
            FILTER(LANG(?label) = "en")
            FILTER(LANG(?description) = "en")
        }}
        LIMIT 1
        '''.format(entity_id, entity_id)
        
        results = self._sparql_query(query)
        
        if not results:
            return None
        
        data = {
            'id': entity_id,
            'label': results[0].get('label', {}).get('value', entity_id),
            'description': results[0].get('description', {}).get('value', '')
        }
        
        self.entity_cache[entity_id] = data
        return data
    
    def _get_entity_relations(self, entity_id: str, limit: int = 20) -> List[Dict]:
        """Get entity relationships"""
        
        query = '''
        SELECT ?property ?propertyLabel ?value ?valueLabel WHERE {{
            wd:{} ?property ?value.
            ?prop wikibase:directClaim ?property.
            FILTER(STRSTARTS(STR(?value), "http://www.wikidata.org/entity/Q"))
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {}
        '''.format(entity_id, limit)
        
        results = self._sparql_query(query)
        
        if not results:
            return []
        
        relations = []
        for result in results:
            value_uri = result.get('value', {}).get('value', '')
            if '/Q' in value_uri:
                related_id = 'Q' + value_uri.split('/Q')[1]
                relations.append({
                    'property': result.get('propertyLabel', {}).get('value', 'related_to'),
                    'related_entity': related_id,
                    'related_label': result.get('valueLabel', {}).get('value', related_id)
                })
        
        return relations
    
    def _add_entity_to_graph(self, entity_id: str, entity_data: Dict) -> bool:
        """Add entity to graph"""
        
        node_id = f"WD_{entity_id}"
        
        if self.graph.semantic.has_node(node_id):
            return False
        
        self.graph.semantic.add_node(node_id,
            node_type='wikidata_entity',
            wikidata_id=entity_id,
            label=entity_data.get('label', entity_id),
            description=entity_data.get('description', ''),
            source='wikidata',
            crawled_at=datetime.now().isoformat()
        )
        
        return True
    
    def _add_relation_to_graph(self, entity_id: str, related_id: str, relation: Dict) -> bool:
        """Add relationship to graph"""
        
        node_a = f"WD_{entity_id}"
        node_b = f"WD_{related_id}"
        
        if not (self.graph.semantic.has_node(node_a) and self.graph.semantic.has_node(node_b)):
            return False
        
        if self.graph.semantic.has_edge(node_a, node_b):
            return False
        
        self.graph.semantic.add_edge(node_a, node_b,
            relation=relation['property'],
            confidence=0.9,  # Wikidata is highly reliable
            source='wikidata'
        )
        
        return True
    
    def crawl_topic_batch(self, topic_queries: List[Tuple[str, str]], max_per_topic: int = 5) -> Dict:
        """
        Crawl multiple topics
        
        Args:
            topic_queries: List of (search_term, expected_type) tuples
            max_per_topic: Max relations per topic
            
        Returns:
            Aggregate statistics
        """
        if self.verbose:
            print(f"\n🚀 Batch Crawl - {len(topic_queries)} topics\n")
        
        total_stats = {
            'topics_processed': 0,
            'entities_added': 0,
            'relations_added': 0
        }
        
        for search_term, _ in topic_queries:
            if self.verbose:
                print(f"Searching: {search_term}")
            
            entity_id = self.search_entity(search_term)
            
            if not entity_id:
                if self.verbose:
                    print(f"   ✗ Not found\n")
                continue
            
            if self.verbose:
                print(f"   Found: {entity_id}")
            
            stats = self.crawl_entity(entity_id, max_relations=max_per_topic)
            
            total_stats['topics_processed'] += 1
            total_stats['entities_added'] += stats['entities_added']
            total_stats['relations_added'] += stats['relations_added']
        
        if self.verbose:
            print(f"\n✅ Batch Complete!")
            print(f"   Topics: {total_stats['topics_processed']}/{len(topic_queries)}")
            print(f"   Entities: {total_stats['entities_added']}")
            print(f"   Relations: {total_stats['relations_added']}\n")
        
        return total_stats


# Test function
def test_wikidata():
    """Test Wikidata crawler"""
    import sys
    sys.path.insert(0, '..')
    
    from core.causal_graph import CausalGraph
    
    print("\n" + "="*60)
    print("WIKIDATA CRAWLER TEST")
    print("="*60)
    
    graph = CausalGraph()
    initial_nodes = graph.get_statistics()['semantic_nodes']
    
    print(f"\nInitial nodes: {initial_nodes}")
    
    crawler = WikidataCrawler(graph, verbose=True)
    
    # Test: Search and crawl Python
    print("\nTest: Python (programming language)")
    entity_id = crawler.search_entity("Python")
    
    if entity_id:
        print(f"Found entity: {entity_id}")
        stats = crawler.crawl_entity(entity_id, max_relations=5)
    else:
        print("Entity not found - trying direct ID")
        stats = crawler.crawl_entity('Q28865', max_relations=5)  # Python's known ID
    
    final_nodes = graph.get_statistics()['semantic_nodes']
    print(f"\nFinal nodes: {final_nodes}")
    print(f"Nodes added: {final_nodes - initial_nodes}")
    
    if stats['entities_added'] > 0:
        print("\n✅ Test PASSED - Wikidata crawler is working!")
    else:
        print("\n❌ Test FAILED - No entities added")
    
    return stats


if __name__ == "__main__":
    test_wikidata()
