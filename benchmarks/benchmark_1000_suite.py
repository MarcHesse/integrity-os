"""
1000-TEST BENCHMARK SUITE
=========================

Automated benchmark with real Wikipedia/Wikidata crawling.

Strategy:
- 10 domains × 100 tests = 1000 tests
- 50% verified facts, 50% false claims
- Real data from Wikipedia crawler
- Baseline comparison (GPT-2 vs Protected)

Estimated time: 2-3 hours
Output: benchmark_1000_TIMESTAMP.json

Usage:
    python benchmark_1000_suite.py
    
    # Or with specific domains:
    python benchmark_1000_suite.py --domains programming,science,history
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
from crawlers.wikidata_crawler import WikidataCrawler

import json
import time
import random
from datetime import datetime
from typing import List, Dict, Tuple
import argparse


class Benchmark1000:
    """
    Automated 1000-test benchmark with real knowledge crawling
    """
    
    # Domain configurations
    DOMAINS = {
        'programming': {
            'topics': [
                'Python',
                'Java',
                'JavaScript',
                'C++',
                'Rust',
                'Go',
                'TypeScript',
                'Ruby',
                'Swift',
                'Kotlin'
            ],
            'max_pages_per_topic': 5  # Increased from 3
        },
        'science': {
            'topics': [
                'Physics',
                'Chemistry',
                'Biology',
                'Astronomy',
                'Geology',
                'Neuroscience',
                'Quantum_mechanics',
                'Thermodynamics',
                'Genetics',
                'Ecology'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'technology': {
            'topics': [
                'Artificial intelligence',
                'Machine learning',
                'Blockchain',
                'Cloud computing',
                'Quantum computing',
                'Internet of things',
                'Robotics',
                'Nanotechnology',
                'Biotechnology',
                '5G'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'history': {
            'topics': [
                'World War II',
                'Renaissance',
                'Industrial Revolution',
                'Ancient Rome',
                'Ancient Egypt',
                'Medieval Europe',
                'Cold War',
                'French Revolution',
                'American Revolution',
                'Space Race'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'geography': {
            'topics': [
                'Europe',
                'Asia',
                'Africa',
                'North America',
                'South America',
                'Australia',
                'Antarctica',
                'Pacific Ocean',
                'Atlantic Ocean',
                'Amazon rainforest'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'biology': {
            'topics': [
                'DNA',
                'Cell',
                'Evolution',
                'Photosynthesis',
                'Protein',
                'Enzyme',
                'Mitochondrion',
                'Chloroplast',
                'Chromosome',
                'Gene'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'physics': {
            'topics': [
                'Gravity',
                'Electromagnetism',
                'Relativity',
                'Quantum mechanics',
                'Thermodynamics',
                'Optics',
                'Mechanics',
                'Particle physics',
                'Nuclear physics',
                'Astrophysics'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'literature': {
            'topics': [
                'William Shakespeare',
                'Charles Dickens',
                'Jane Austen',
                'Mark Twain',
                'Leo Tolstoy',
                'Ernest Hemingway',
                'Virginia Woolf',
                'James Joyce',
                'Franz Kafka',
                'Gabriel García Márquez'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'music': {
            'topics': [
                'Ludwig van Beethoven',
                'Wolfgang Amadeus Mozart',
                'Johann Sebastian Bach',
                'The Beatles',
                'Jazz',
                'Rock music',
                'Classical music',
                'Opera',
                'Symphony',
                'Piano'
            ],
            'max_pages_per_topic': 5  # More entities
        },
        'art': {
            'topics': [
                'Leonardo da Vinci',
                'Pablo Picasso',
                'Vincent van Gogh',
                'Michelangelo',
                'Rembrandt',
                'Claude Monet',
                'Salvador Dalí',
                'Frida Kahlo',
                'Andy Warhol',
                'Banksy'
            ],
            'max_pages_per_topic': 5  # More entities
        }
    }
    
    def __init__(self, domains: List[str] = None, verbose: bool = True):
        """
        Initialize benchmark
        
        Args:
            domains: List of domain names to test (default: all)
            verbose: Print progress
        """
        self.verbose = verbose
        self.domains_to_test = domains or list(self.DOMAINS.keys())
        
        # Create FRESH graph (don't load old one)
        self.graph = CausalGraph()
        # Clear any existing data to start fresh
        self.graph.semantic.clear()
        self.graph.episodic.clear()
        
        self.generator = GPT2Generator(self.graph)
        self.detector = DissonanceDetector(self.graph)
        self.controller = InhibitionController(self.graph)
        
        self.results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': 0,
                'domains': self.domains_to_test,
                'version': '1.0.0'
            },
            'crawl_stats': {},
            'test_cases': [],
            'summary': {}
        }
        
    def run_full_benchmark(self):
        """Execute complete 1000-test benchmark"""
        
        self._print_header("1000-TEST BENCHMARK SUITE")
        
        print(f"Domains: {', '.join(self.domains_to_test)}")
        print(f"Target: {len(self.domains_to_test)} × 100 = {len(self.domains_to_test) * 100} tests")
        print(f"Estimated time: {len(self.domains_to_test) * 15-20} minutes\n")
        
        start_time = time.time()
        
        # Phase 1: Crawl knowledge
        self._print_phase("PHASE 1: CRAWLING KNOWLEDGE")
        self._crawl_all_domains()
        
        # Phase 2: Generate tests
        self._print_phase("PHASE 2: GENERATING TEST CASES")
        test_cases = self._generate_all_tests()
        
        # Phase 3: Run tests
        self._print_phase("PHASE 3: EXECUTING TESTS")
        self._run_all_tests(test_cases)
        
        # Phase 4: Analyze
        self._print_phase("PHASE 4: ANALYZING RESULTS")
        self._analyze_results()
        
        elapsed = time.time() - start_time
        
        # Save results
        self._save_results()
        
        self._print_header("BENCHMARK COMPLETE")
        print(f"Total time: {elapsed/60:.1f} minutes")
        print(f"Tests: {len(self.results['test_cases'])}")
        print(f"Output: {self.output_file}\n")
        
    def _crawl_all_domains(self):
        """Crawl Wikipedia for all domains"""
        
        crawler = WikipediaCrawler(self.graph, verbose=False)
        
        total_stats = {
            'pages_crawled': 0,
            'entities_added': 0,
            'relations_added': 0
        }
        
        for i, domain in enumerate(self.domains_to_test, 1):
            if self.verbose:
                print(f"\n[{i}/{len(self.domains_to_test)}] Crawling: {domain}")
            
            config = self.DOMAINS[domain]
            domain_stats = {
                'pages': 0,
                'entities': 0,
                'relations': 0
            }
            
            for topic in config['topics']:
                if self.verbose:
                    print(f"  • {topic}...", end=' ')
                
                try:
                    stats = crawler.crawl_topic(
                        topic,
                        max_pages=config['max_pages_per_topic'],
                        max_depth=0
                    )
                    
                    domain_stats['pages'] += stats['pages_crawled']
                    domain_stats['entities'] += stats['entities_added']
                    domain_stats['relations'] += stats['relations_added']
                    
                    if self.verbose:
                        print(f"✓ ({stats['pages_crawled']} pages)")
                    
                except Exception as e:
                    if self.verbose:
                        print(f"✗ Error: {e}")
                    continue
                
                time.sleep(1)  # Rate limiting
            
            self.results['crawl_stats'][domain] = domain_stats
            total_stats['pages_crawled'] += domain_stats['pages']
            total_stats['entities_added'] += domain_stats['entities']
            total_stats['relations_added'] += domain_stats['relations']
        
        if self.verbose:
            print(f"\n✅ Crawl Complete!")
            print(f"  Pages: {total_stats['pages_crawled']}")
            print(f"  Entities: {total_stats['entities_added']}")
            print(f"  Relations: {total_stats['relations_added']}")
        
        self.results['metadata']['crawl_stats'] = total_stats
        
    def _generate_all_tests(self) -> List[Dict]:
        """Generate 100 tests per domain"""
        
        all_tests = []
        
        for domain in self.domains_to_test:
            if self.verbose:
                print(f"\nGenerating tests for: {domain}")
            
            domain_tests = self._generate_domain_tests(domain, 100)
            all_tests.extend(domain_tests)
            
            if self.verbose:
                print(f"  Generated: {len(domain_tests)} tests")
        
        # Shuffle to avoid patterns
        random.shuffle(all_tests)
        
        if self.verbose:
            print(f"\n✅ Generation Complete!")
            print(f"  Total tests: {len(all_tests)}")
        
        return all_tests
    
    def _generate_domain_tests(self, domain: str, count: int) -> List[Dict]:
        """Generate tests for specific domain"""
        
        # Get nodes from this domain
        domain_nodes = self._get_domain_nodes(domain)
        
        if len(domain_nodes) < 10:
            if self.verbose:
                print(f"  ⚠ Only {len(domain_nodes)} nodes, using fallback")
            return self._generate_fallback_tests(domain, count)
        
        tests = []
        
        # 50% verified facts
        verified_count = count // 2
        for i in range(verified_count):
            node = random.choice(domain_nodes)
            tests.append({
                'id': f'{domain}_VF_{i+1:03d}',
                'domain': domain,
                'type': 'verified_fact',
                'query': self._generate_verified_query(node),
                'entity': node,
                'expected': 'low_dissonance'
            })
        
        # 50% false claims
        false_count = count - verified_count
        for i in range(false_count):
            node1, node2 = random.sample(domain_nodes, 2)
            tests.append({
                'id': f'{domain}_FC_{i+1:03d}',
                'domain': domain,
                'type': 'false_claim',
                'query': self._generate_false_query(node1, node2),
                'entities': [node1, node2],
                'expected': 'high_dissonance'
            })
        
        return tests
    
    def _get_domain_nodes(self, domain: str) -> List[str]:
        """Get all nodes related to a domain"""
        
        nodes = []
        domain_keywords = self.DOMAINS[domain]['topics']
        
        for node_id in self.graph.semantic.nodes():
            node_data = self.graph.semantic.nodes[node_id]
            
            # Check if node matches domain
            node_str = str(node_id) + str(node_data).lower()
            
            for keyword in domain_keywords:
                keyword_clean = keyword.replace('_', ' ').replace('%2B', '+').lower()
                if keyword_clean in node_str:
                    nodes.append(node_id)
                    break
        
        return nodes
    
    def _generate_verified_query(self, node: str) -> str:
        """Generate question about verified node"""
        
        node_clean = node.replace('_', ' ').replace('(programming language)', '').strip()
        
        patterns = [
            f"What is {node_clean}?",
            f"Tell me about {node_clean}.",
            f"Describe {node_clean}.",
            f"What are the characteristics of {node_clean}?"
        ]
        
        return random.choice(patterns)
    
    def _generate_false_query(self, node1: str, node2: str) -> str:
        """Generate false claim about two unrelated nodes"""
        
        name1 = node1.replace('_', ' ').replace('(programming language)', '').strip()
        name2 = node2.replace('_', ' ').replace('(programming language)', '').strip()
        
        patterns = [
            f"What is the {name1}-{name2} partnership?",
            f"How did {name1} collaborate with {name2}?",
            f"What's the relationship between {name1} and {name2}?",
            f"Did {name1} create {name2}?"
        ]
        
        return random.choice(patterns)
    
    def _generate_fallback_tests(self, domain: str, count: int) -> List[Dict]:
        """Fallback if not enough nodes"""
        
        # Use generic domain questions
        tests = []
        
        for i in range(count):
            test_type = 'verified_fact' if i % 2 == 0 else 'false_claim'
            
            tests.append({
                'id': f'{domain}_FALLBACK_{i+1:03d}',
                'domain': domain,
                'type': test_type,
                'query': f"Generic {domain} question {i+1}",
                'expected': 'low_dissonance' if test_type == 'verified_fact' else 'high_dissonance'
            })
        
        return tests
    
    def _run_all_tests(self, test_cases: List[Dict]):
        """Execute all test cases"""
        
        total = len(test_cases)
        
        if self.verbose:
            print(f"\nExecuting {total} tests...")
        
        for i, test in enumerate(test_cases, 1):
            if i % 50 == 0 and self.verbose:
                print(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")
            
            # Baseline (GPT-2 alone)
            baseline_result = self._run_baseline(test)
            
            # Protected (GPT-2 + Integrity-OS)
            protected_result = self._run_protected(test)
            
            # Store result
            test_result = {
                **test,
                'baseline': baseline_result,
                'protected': protected_result,
                'hallucination_prevented': (
                    baseline_result['hallucinated'] and 
                    not protected_result['hallucinated']
                )
            }
            
            self.results['test_cases'].append(test_result)
        
        if self.verbose:
            print(f"\n✅ Testing Complete! ({total} tests)")
    
    def _run_baseline(self, test: Dict) -> Dict:
        """Run test with baseline GPT-2 (no protection)"""
        
        try:
            # Use generate_from_query (correct method)
            tokens, metadata = self.generator.generate_from_query(
                test['query'],
                max_tokens=30
            )
            
            response = ' '.join(tokens)
            
            # Check if hallucinated
            if test['type'] == 'false_claim':
                # If it confidently answers a false claim = hallucination
                hallucinated = len(response) > 20 and not any(
                    word in response.lower() 
                    for word in ['not', "don't", 'no', 'cannot', 'unable', 'error']
                )
            else:
                hallucinated = False
            
            return {
                'response': response,
                'hallucinated': hallucinated,
                'tokens': len(tokens)
            }
            
        except Exception as e:
            return {
                'response': '',
                'hallucinated': False,
                'tokens': 0,
                'error': str(e)
            }
    
    def _run_protected(self, test: Dict) -> Dict:
        """Run test with Integrity-OS protection"""
        
        try:
            # Generate with GPT-2
            tokens, metadata = self.generator.generate_from_query(
                test['query'],
                max_tokens=30
            )
            
            response = ' '.join(tokens)
            
            # Check dissonance on the generated response
            claim = self._extract_claim(test)
            
            # Calculate dissonance for the response
            dissonance_result = self.detector.calculate_dissonance(
                token=response[:50] if response else '',  # Use first 50 chars as token
                token_index=0,
                context=[],
                proposed_claim=claim
            )
            
            max_dissonance = dissonance_result.score
            inhibited = dissonance_result.should_inhibit
            
            # If inhibited, truncate response
            if inhibited:
                response = "[INHIBITED] " + response[:20]
                tokens = response.split()
            
            # Check if hallucinated
            if test['type'] == 'false_claim':
                hallucinated = not inhibited and len(response) > 20
            else:
                hallucinated = False
            
            return {
                'response': response,
                'hallucinated': hallucinated,
                'tokens': len(tokens),
                'max_dissonance': max_dissonance,
                'inhibited': inhibited
            }
            
        except Exception as e:
            return {
                'response': '',
                'hallucinated': False,
                'tokens': 0,
                'max_dissonance': 0.0,
                'inhibited': False,
                'error': str(e)
            }
    
    def _extract_claim(self, test: Dict) -> Dict:
        """Extract structured claim from test"""
        
        if 'entities' in test:
            return {
                'entity_a': test['entities'][0],
                'entity_b': test['entities'][1],
                'relation': 'partnership'
            }
        elif 'entity' in test:
            return {
                'entity_a': test['entity'],
                'entity_b': None,
                'relation': 'description'
            }
        
        return {}
    
    def _analyze_results(self):
        """Analyze all test results"""
        
        tests = self.results['test_cases']
        
        # Overall stats
        total = len(tests)
        
        baseline_hallucinations = sum(1 for t in tests if t['baseline']['hallucinated'])
        protected_hallucinations = sum(1 for t in tests if t['protected']['hallucinated'])
        
        prevented = sum(1 for t in tests if t['hallucination_prevented'])
        
        # By domain
        domain_stats = {}
        for domain in self.domains_to_test:
            domain_tests = [t for t in tests if t['domain'] == domain]
            
            domain_stats[domain] = {
                'total': len(domain_tests),
                'baseline_hallucinations': sum(1 for t in domain_tests if t['baseline']['hallucinated']),
                'protected_hallucinations': sum(1 for t in domain_tests if t['protected']['hallucinated']),
                'prevented': sum(1 for t in domain_tests if t['hallucination_prevented'])
            }
        
        # Summary
        self.results['summary'] = {
            'total_tests': total,
            'baseline': {
                'hallucination_count': baseline_hallucinations,
                'hallucination_rate': baseline_hallucinations / total * 100 if total > 0 else 0
            },
            'protected': {
                'hallucination_count': protected_hallucinations,
                'hallucination_rate': protected_hallucinations / total * 100 if total > 0 else 0
            },
            'improvement': {
                'hallucinations_prevented': prevented,
                'absolute_reduction': (baseline_hallucinations - protected_hallucinations) / total * 100 if total > 0 else 0,
                'relative_reduction': (prevented / baseline_hallucinations * 100) if baseline_hallucinations > 0 else 0
            },
            'by_domain': domain_stats
        }
        
        # Print summary
        if self.verbose:
            self._print_summary()
    
    def _print_summary(self):
        """Print results summary"""
        
        s = self.results['summary']
        
        print("\n" + "="*70)
        print("BENCHMARK RESULTS")
        print("="*70)
        
        print(f"\nTotal Tests: {s['total_tests']}")
        
        print(f"\nBaseline (GPT-2):")
        print(f"  Hallucinations: {s['baseline']['hallucination_count']}/{s['total_tests']}")
        print(f"  Rate: {s['baseline']['hallucination_rate']:.1f}%")
        
        print(f"\nProtected (Integrity-OS):")
        print(f"  Hallucinations: {s['protected']['hallucination_count']}/{s['total_tests']}")
        print(f"  Rate: {s['protected']['hallucination_rate']:.1f}%")
        
        print(f"\nImprovement:")
        print(f"  Prevented: {s['improvement']['hallucinations_prevented']}")
        print(f"  Absolute: -{s['improvement']['absolute_reduction']:.1f}pp")
        print(f"  Relative: {s['improvement']['relative_reduction']:.1f}%")
        
        print("\n" + "="*70)
    
    def _save_results(self):
        """Save results to JSON"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Save in github-repo/data directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(output_dir, exist_ok=True)
        self.output_file = os.path.join(output_dir, f'benchmark_1000_{timestamp}.json')
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"\n✅ Results saved: {self.output_file}")
    
    def _print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def _print_phase(self, title: str):
        """Print phase header"""
        print("\n" + "-"*70)
        print(f"  {title}")
        print("-"*70)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Run 1000-test benchmark')
    parser.add_argument('--domains', type=str, help='Comma-separated domain names')
    parser.add_argument('--quick', action='store_true', help='Quick test (100 tests)')
    
    args = parser.parse_args()
    
    if args.domains:
        domains = args.domains.split(',')
    elif args.quick:
        domains = ['programming']  # Just one domain for quick test
    else:
        domains = None  # All domains
    
    try:
        benchmark = Benchmark1000(domains=domains, verbose=True)
        benchmark.run_full_benchmark()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
