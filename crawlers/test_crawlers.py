"""
CRAWLER TEST SUITE
==================

Comprehensive tests for both Wikipedia and Wikidata crawlers.

Run: python test_crawlers.py
"""

import sys
sys.path.insert(0, '..')

from core.causal_graph import CausalGraph
from crawlers.wikipedia_crawler import WikipediaCrawler
from crawlers.wikidata_crawler import WikidataCrawler
import time


def print_header(title):
    """Print formatted header"""
    print("\\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\\n")


def test_wikipedia_crawler():
    """Test Wikipedia crawler"""
    print_header("TEST 1: WIKIPEDIA CRAWLER")
    
    graph = CausalGraph()
    initial_stats = graph.get_statistics()
    
    print(f"Initial Graph:")
    print(f"  Nodes: {initial_stats['semantic_nodes']}")
    print(f"  Edges: {initial_stats['semantic_edges']}\\n")
    
    crawler = WikipediaCrawler(graph, verbose=True)
    
    # Test 1: Single page
    print("Test 1a: Single page (Python)")
    stats1 = crawler.crawl_topic('Python_(programming_language)', max_pages=1, max_depth=0)
    
    time.sleep(2)
    
    # Test 2: With links
    print("\\nTest 1b: With links (max_depth=1)")
    stats2 = crawler.crawl_topic('Java_(programming_language)', max_pages=5, max_depth=1)
    
    final_stats = graph.get_statistics()
    
    print(f"\\nFinal Graph:")
    print(f"  Nodes: {final_stats['semantic_nodes']}")
    print(f"  Edges: {final_stats['semantic_edges']}")
    print(f"  Nodes Added: {final_stats['semantic_nodes'] - initial_stats['semantic_nodes']}")
    print(f"  Edges Added: {final_stats['semantic_edges'] - initial_stats['semantic_edges']}")
    
    # Validation
    success = (
        stats1['pages_crawled'] > 0 and
        stats2['pages_crawled'] > 0 and
        final_stats['semantic_nodes'] > initial_stats['semantic_nodes']
    )
    
    if success:
        print("\\n✅ WIKIPEDIA CRAWLER: PASSED")
    else:
        print("\\n❌ WIKIPEDIA CRAWLER: FAILED")
    
    return success, final_stats['semantic_nodes'] - initial_stats['semantic_nodes']


def test_wikidata_crawler():
    """Test Wikidata crawler"""
    print_header("TEST 2: WIKIDATA CRAWLER")
    
    graph = CausalGraph()
    initial_stats = graph.get_statistics()
    
    print(f"Initial Graph:")
    print(f"  Nodes: {initial_stats['semantic_nodes']}")
    print(f"  Edges: {initial_stats['semantic_edges']}\\n")
    
    crawler = WikidataCrawler(graph, verbose=True)
    
    # Test 1: Direct entity ID
    print("Test 2a: Direct entity (Python - Q28865)")
    stats1 = crawler.crawl_entity('Q28865', max_relations=5)
    
    time.sleep(2)
    
    # Test 2: Search and crawl
    print("\\nTest 2b: Search entity (JavaScript)")
    entity_id = crawler.search_entity("JavaScript")
    if entity_id:
        stats2 = crawler.crawl_entity(entity_id, max_relations=5)
    else:
        print("   Search failed, using known ID Q2005")
        stats2 = crawler.crawl_entity('Q2005', max_relations=5)
    
    time.sleep(2)
    
    # Test 3: Batch crawl
    print("\\nTest 2c: Batch crawl")
    topics = [
        ("C++", "programming_language"),
        ("Rust", "programming_language"),
    ]
    stats3 = crawler.crawl_topic_batch(topics, max_per_topic=3)
    
    final_stats = graph.get_statistics()
    
    print(f"\\nFinal Graph:")
    print(f"  Nodes: {final_stats['semantic_nodes']}")
    print(f"  Edges: {final_stats['semantic_edges']}")
    print(f"  Nodes Added: {final_stats['semantic_nodes'] - initial_stats['semantic_nodes']}")
    print(f"  Edges Added: {final_stats['semantic_edges'] - initial_stats['semantic_edges']}")
    
    # Validation
    success = (
        stats1['entities_added'] > 0 and
        stats2['entities_added'] > 0 and
        final_stats['semantic_nodes'] > initial_stats['semantic_nodes']
    )
    
    if success:
        print("\\n✅ WIKIDATA CRAWLER: PASSED")
    else:
        print("\\n❌ WIKIDATA CRAWLER: FAILED")
    
    return success, final_stats['semantic_nodes'] - initial_stats['semantic_nodes']


def test_comparison():
    """Compare both crawlers"""
    print_header("TEST 3: CRAWLER COMPARISON")
    
    # Wikipedia test
    print("Testing Wikipedia crawler...")
    graph_wiki = CausalGraph()
    wiki_crawler = WikipediaCrawler(graph_wiki, verbose=False)
    
    start = time.time()
    wiki_stats = wiki_crawler.crawl_topic('Python_(programming_language)', max_pages=3, max_depth=0)
    wiki_time = time.time() - start
    
    wiki_nodes = graph_wiki.get_statistics()['semantic_nodes']
    
    time.sleep(3)
    
    # Wikidata test
    print("Testing Wikidata crawler...")
    graph_wd = CausalGraph()
    wd_crawler = WikidataCrawler(graph_wd, verbose=False)
    
    start = time.time()
    wd_stats = wd_crawler.crawl_entity('Q28865', max_relations=10)
    wd_time = time.time() - start
    
    wd_nodes = graph_wd.get_statistics()['semantic_nodes']
    
    # Results
    print("\\nComparison Results:")
    print("\\nWikipedia:")
    print(f"  Pages crawled: {wiki_stats['pages_crawled']}")
    print(f"  Nodes added: {wiki_nodes}")
    print(f"  Time: {wiki_time:.1f}s")
    
    print("\\nWikidata:")
    print(f"  Entities added: {wd_stats['entities_added']}")
    print(f"  Relations added: {wd_stats['relations_added']}")
    print(f"  Nodes added: {wd_nodes}")
    print(f"  Time: {wd_time:.1f}s")
    
    print("\\nRecommendation:")
    if wd_stats['entities_added'] > 0 and wd_time < wiki_time * 2:
        print("  ✅ Wikidata: More structured, reliable data")
        print("  Use Wikidata for entity-relationship extraction")
    else:
        print("  ✅ Wikipedia: More coverage, detailed info")
        print("  Use Wikipedia for broader knowledge crawling")


def run_all_tests():
    """Run all crawler tests"""
    print_header("CRAWLER TEST SUITE")
    
    results = {}
    
    # Test 1: Wikipedia
    try:
        results['wikipedia'] = test_wikipedia_crawler()
        time.sleep(3)
    except Exception as e:
        print(f"\\n❌ Wikipedia test error: {e}")
        results['wikipedia'] = (False, 0)
    
    # Test 2: Wikidata
    try:
        results['wikidata'] = test_wikidata_crawler()
        time.sleep(3)
    except Exception as e:
        print(f"\\n❌ Wikidata test error: {e}")
        results['wikidata'] = (False, 0)
    
    # Test 3: Comparison
    try:
        test_comparison()
    except Exception as e:
        print(f"\\n❌ Comparison test error: {e}")
    
    # Summary
    print_header("TEST SUMMARY")
    
    wiki_success, wiki_nodes = results['wikipedia']
    wd_success, wd_nodes = results['wikidata']
    
    print(f"Wikipedia Crawler: {'✅ PASSED' if wiki_success else '❌ FAILED'}")
    print(f"  Nodes added: {wiki_nodes}")
    
    print(f"\\nWikidata Crawler: {'✅ PASSED' if wd_success else '❌ FAILED'}")
    print(f"  Nodes added: {wd_nodes}")
    
    if wiki_success and wd_success:
        print("\\n🎉 ALL TESTS PASSED!")
        print("\\nBoth crawlers are working correctly.")
        print("You can now use them to expand your knowledge graph!")
    elif wiki_success or wd_success:
        print("\\n⚠️  PARTIAL SUCCESS")
        print("\\nAt least one crawler is working.")
    else:
        print("\\n❌ ALL TESTS FAILED")
        print("\\nCheck your internet connection and try again.")
    
    print("\\n" + "="*70 + "\\n")


if __name__ == "__main__":
    run_all_tests()
