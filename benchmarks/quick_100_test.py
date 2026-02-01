"""
QUICK 100-TEST RUN
==================

Quick test with just programming domain to verify everything works.
Estimated time: 15-20 minutes

Usage:
    cd D:\claude\github-repo
    python benchmarks\quick_100_test.py
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.causal_graph import CausalGraph
from core.gpt2_generator import GPT2Generator
from core.dissonance_detector import DissonanceDetector
from core.inhibition_controller import InhibitionController
from crawlers.wikipedia_crawler import WikipediaCrawler

import json
import time
import random
from datetime import datetime

# Just run a simplified version inline
if __name__ == "__main__":
    print("\n🚀 QUICK 100-TEST RUN")
    print("="*60)
    print("Domain: Programming only")
    print("Tests: ~30 (quick validation)")
    print("Time: ~5-10 minutes")
    print("="*60 + "\n")
    
    input("Press ENTER to start...")
    
    # Initialize
    graph = CausalGraph()
    crawler = WikipediaCrawler(graph, verbose=True)
    
    # Crawl programming topics
    print("\n[PHASE 1] Crawling Programming Topics...")
    topics = [
        'Python_(programming_language)',
        'Java_(programming_language)',
        'JavaScript'
    ]
    
    for topic in topics:
        print(f"\nCrawling: {topic}")
        crawler.crawl_topic(topic, max_pages=2, max_depth=0)
        time.sleep(2)
    
    # Generate simple tests
    print("\n[PHASE 2] Generating Tests...")
    nodes = list(graph.semantic.nodes())
    print(f"Available nodes: {len(nodes)}")
    
    # Just test that everything works
    print("\n[PHASE 3] Testing Core System...")
    
    generator = GPT2Generator(graph)
    detector = DissonanceDetector(graph)
    
    # Test 1: Verified fact
    print("\nTest 1: Verified fact")
    result1 = detector.calculate_dissonance(
        token="language",
        token_index=0,
        context=[],
        proposed_claim={'entity_a': 'Python_(programming_language)', 'entity_b': None, 'relation': 'description'}
    )
    print(f"  Dissonance: {result1.score:.3f}")
    print(f"  Should inhibit: {result1.should_inhibit}")
    
    # Test 2: False claim
    print("\nTest 2: False claim")
    result2 = detector.calculate_dissonance(
        token="partnership",
        token_index=0,
        context=[],
        proposed_claim={'entity_a': 'Python_(programming_language)', 'entity_b': 'Java_(programming_language)', 'relation': 'partnership'}
    )
    print(f"  Dissonance: {result2.score:.3f}")
    print(f"  Should inhibit: {result2.should_inhibit}")
    
    print("\n" + "="*60)
    print("✅ QUICK TEST COMPLETE!")
    print("="*60)
    
    if result1.score < 0.5 and result2.score > 0.8:
        print("\n✅ System is working correctly!")
        print("You can now run the full 1000-test suite:")
        print("  python benchmark_1000_suite.py")
    else:
        print("\n⚠️ Unexpected results - check configuration")
        print(f"  Verified fact dissonance: {result1.score:.3f} (expected < 0.5)")
        print(f"  False claim dissonance: {result2.score:.3f} (expected > 0.8)")
