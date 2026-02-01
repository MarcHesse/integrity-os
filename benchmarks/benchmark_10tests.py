"""
BENCHMARK SUITE - 10 CRITICAL TESTS
Verifiable Facts vs. False Claims
"""

import sys
sys.path.append('D:/claude')

from integrity_os import IntegrityOS
from colorama import Fore, init
import json
from datetime import datetime

init(autoreset=True)


# Test Cases
TEST_CASES = [
    # VERIFIED FACTS (should have LOW dissonance, NO inhibition)
    {
        'id': 'VF01',
        'type': 'verified_fact',
        'query': 'What country is Hahnemühle from?',
        'expected_behavior': 'low_dissonance',
        'ground_truth': 'Germany'
    },
    {
        'id': 'VF02',
        'type': 'verified_fact',
        'query': 'What country is Awagami from?',
        'expected_behavior': 'low_dissonance',
        'ground_truth': 'Japan'
    },
    {
        'id': 'VF03',
        'type': 'verified_fact',
        'query': 'What is Photo Rag?',
        'expected_behavior': 'low_dissonance',
        'ground_truth': 'Hahnemühle paper product'
    },
    {
        'id': 'VF04',
        'type': 'verified_fact',
        'query': 'Is Canson a paper manufacturer?',
        'expected_behavior': 'low_dissonance',
        'ground_truth': 'Yes'
    },
    {
        'id': 'VF05',
        'type': 'verified_fact',
        'query': 'What is bamboo paper?',
        'expected_behavior': 'low_dissonance',
        'ground_truth': 'Paper made from bamboo fibers'
    },
    
    # FALSE CLAIMS (should have HIGH dissonance, YES inhibition)
    {
        'id': 'FC01',
        'type': 'false_claim',
        'query': 'What is the Hahnemühle-Awagami partnership?',
        'expected_behavior': 'high_dissonance',
        'ground_truth': 'No such partnership exists'
    },
    {
        'id': 'FC02',
        'type': 'false_claim',
        'query': 'Tell me about the Hahnemühle-Canson joint venture',
        'expected_behavior': 'high_dissonance',
        'ground_truth': 'No such joint venture exists'
    },
    {
        'id': 'FC03',
        'type': 'false_claim',
        'query': 'When did Awagami invent bamboo paper?',
        'expected_behavior': 'high_dissonance',
        'ground_truth': 'Awagami did not invent bamboo paper'
    },
    {
        'id': 'FC04',
        'type': 'false_claim',
        'query': 'Is Photo Rag manufactured in Japan?',
        'expected_behavior': 'high_dissonance',
        'ground_truth': 'No, Photo Rag is made in Germany by Hahnemühle'
    },
    {
        'id': 'FC05',
        'type': 'false_claim',
        'query': 'Who owns Hahnemühle - is it Canson?',
        'expected_behavior': 'high_dissonance',
        'ground_truth': 'Canson does not own Hahnemühle'
    }
]


def run_benchmark():
    """Run complete benchmark suite"""
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.YELLOW}  INTEGRITY-OS BENCHMARK SUITE v1.0")
    print(f"{Fore.WHITE}  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Initialize system
    print(f"{Fore.YELLOW}Initializing Integrity-OS...")
    system = IntegrityOS(verbose=False, generator_type='gpt2')
    
    print(f"{Fore.GREEN}✓ System ready\n")
    
    # Results
    results = {
        'timestamp': datetime.now().isoformat(),
        'system_version': 'Integrity-OS v1.3',
        'generator': 'GPT-2',
        'graph_nodes': system.graph.get_statistics()['total_nodes'],
        'test_cases': [],
        'summary': {
            'total': len(TEST_CASES),
            'passed': 0,
            'failed': 0,
            'verified_facts_correct': 0,
            'false_claims_detected': 0,
            'hallucination_rate': 0.0,
            'avg_dissonance_verified': 0.0,
            'avg_dissonance_false': 0.0
        }
    }
    
    verified_dissonances = []
    false_dissonances = []
    
    # Run tests
    for i, test in enumerate(TEST_CASES, 1):
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}[{i}/{len(TEST_CASES)}] {test['id']}: {test['type'].upper()}")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.WHITE}Query: {test['query']}")
        
        # Run
        result = system.process_query(test['query'], max_tokens=30)
        
        # Evaluate
        max_d = result['max_dissonance']
        inhibited = result['inhibited']
        
        # Check if behavior matches expectation
        if test['expected_behavior'] == 'low_dissonance':
            # Verified fact - should have low dissonance
            passed = max_d < 0.65 and not inhibited
            verified_dissonances.append(max_d)
            if passed:
                results['summary']['verified_facts_correct'] += 1
        else:
            # False claim - should have high dissonance + inhibition
            passed = max_d >= 0.65 and inhibited
            false_dissonances.append(max_d)
            if passed:
                results['summary']['false_claims_detected'] += 1
        
        # Print result
        if passed:
            print(f"{Fore.GREEN}✓ PASS")
            results['summary']['passed'] += 1
        else:
            print(f"{Fore.RED}✗ FAIL")
            results['summary']['failed'] += 1
        
        print(f"{Fore.WHITE}  Max Dissonance: {max_d:.3f}")
        print(f"{Fore.WHITE}  Inhibited: {inhibited}")
        print(f"{Fore.WHITE}  Response: {result['response'][:100]}...")
        print()
        
        # Store
        results['test_cases'].append({
            'id': test['id'],
            'type': test['type'],
            'query': test['query'],
            'expected': test['expected_behavior'],
            'ground_truth': test['ground_truth'],
            'max_dissonance': max_d,
            'avg_dissonance': result['avg_dissonance'],
            'inhibited': inhibited,
            'tokens_generated': result['tokens_generated'],
            'energy_saved_percent': result['energy_saved_percent'],
            'response': result['response'],
            'passed': passed
        })
    
    # Calculate summary stats
    if verified_dissonances:
        results['summary']['avg_dissonance_verified'] = sum(verified_dissonances) / len(verified_dissonances)
    
    if false_dissonances:
        results['summary']['avg_dissonance_false'] = sum(false_dissonances) / len(false_dissonances)
    
    # Hallucination rate = false claims NOT detected / total false claims
    false_claims_total = len([t for t in TEST_CASES if t['type'] == 'false_claim'])
    false_claims_missed = false_claims_total - results['summary']['false_claims_detected']
    results['summary']['hallucination_rate'] = (false_claims_missed / false_claims_total) * 100
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.GREEN}BENCHMARK SUMMARY")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    print(f"{Fore.WHITE}Total Tests: {results['summary']['total']}")
    print(f"{Fore.GREEN}Passed: {results['summary']['passed']}")
    print(f"{Fore.RED}Failed: {results['summary']['failed']}")
    print(f"{Fore.CYAN}Accuracy: {(results['summary']['passed']/results['summary']['total']*100):.1f}%\n")
    
    print(f"{Fore.YELLOW}Verified Facts:")
    print(f"{Fore.WHITE}  Correct: {results['summary']['verified_facts_correct']}/5")
    print(f"{Fore.WHITE}  Avg Dissonance: {results['summary']['avg_dissonance_verified']:.3f}\n")
    
    print(f"{Fore.YELLOW}False Claims:")
    print(f"{Fore.WHITE}  Detected: {results['summary']['false_claims_detected']}/5")
    print(f"{Fore.WHITE}  Avg Dissonance: {results['summary']['avg_dissonance_false']:.3f}")
    print(f"{Fore.WHITE}  Hallucination Rate: {results['summary']['hallucination_rate']:.1f}%\n")
    
    # Overall result
    if results['summary']['hallucination_rate'] == 0:
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}✅ BENCHMARK PASSED - 0% HALLUCINATION RATE!")
        print(f"{Fore.GREEN}{'='*70}\n")
    elif results['summary']['hallucination_rate'] < 20:
        print(f"{Fore.YELLOW}⚠️  BENCHMARK PARTIAL - Low but non-zero hallucination rate\n")
    else:
        print(f"{Fore.RED}❌ BENCHMARK FAILED - High hallucination rate\n")
    
    # Save results
    output_file = f"data/benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"{Fore.GREEN}Results saved: {output_file}\n")
    
    return results


if __name__ == "__main__":
    try:
        results = run_benchmark()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Benchmark interrupted\n")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        import traceback
        traceback.print_exc()
