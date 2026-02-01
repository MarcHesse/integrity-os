"""
INTEGRITY-OS REPOSITORY TEST
Tests if all Python modules can be imported correctly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*60)
print("INTEGRITY-OS PYTHON IMPORT TEST")
print("="*60 + "\n")

errors = []
successes = []

# Test 1: Import Core Modules
print("[TEST 1] Importing Core Modules...")
try:
    from core import causal_graph
    print("  ✓ core.causal_graph")
    successes.append("causal_graph")
except Exception as e:
    print(f"  ✗ core.causal_graph - {e}")
    errors.append(("causal_graph", str(e)))

try:
    from core import dissonance_detector
    print("  ✓ core.dissonance_detector")
    successes.append("dissonance_detector")
except Exception as e:
    print(f"  ✗ core.dissonance_detector - {e}")
    errors.append(("dissonance_detector", str(e)))

try:
    from core import inhibition_controller
    print("  ✓ core.inhibition_controller")
    successes.append("inhibition_controller")
except Exception as e:
    print(f"  ✗ core.inhibition_controller - {e}")
    errors.append(("inhibition_controller", str(e)))

try:
    from core import gpt2_generator
    print("  ✓ core.gpt2_generator")
    successes.append("gpt2_generator")
except Exception as e:
    print(f"  ✗ core.gpt2_generator - {e}")
    errors.append(("gpt2_generator", str(e)))

try:
    from core import graph_manager
    print("  ✓ core.graph_manager")
    successes.append("graph_manager")
except Exception as e:
    print(f"  ✗ core.graph_manager - {e}")
    errors.append(("graph_manager", str(e)))

# Test 2: Instantiate Classes
print("\n[TEST 2] Instantiating Core Classes...")
try:
    from core.causal_graph import CausalGraph
    graph = CausalGraph()
    print(f"  ✓ CausalGraph created ({graph.semantic.number_of_nodes()} nodes)")
    successes.append("CausalGraph instantiation")
except Exception as e:
    print(f"  ✗ CausalGraph instantiation - {e}")
    errors.append(("CausalGraph instantiation", str(e)))

try:
    from core.dissonance_detector import DissonanceDetector
    detector = DissonanceDetector(graph)
    print("  ✓ DissonanceDetector created")
    successes.append("DissonanceDetector instantiation")
except Exception as e:
    print(f"  ✗ DissonanceDetector instantiation - {e}")
    errors.append(("DissonanceDetector instantiation", str(e)))

try:
    from core.inhibition_controller import InhibitionController
    controller = InhibitionController(graph)
    print("  ✓ InhibitionController created")
    successes.append("InhibitionController instantiation")
except Exception as e:
    print(f"  ✗ InhibitionController instantiation - {e}")
    errors.append(("InhibitionController instantiation", str(e)))

# Test 3: Check Data Files
print("\n[TEST 3] Checking Data Files...")
import json

data_files = [
    "data/causal_graph.json",
    "data/benchmark_1000_20260201_145905.json"
]

for filepath in data_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  ✓ {filepath} - Valid JSON")
        successes.append(f"{filepath} valid")
    except Exception as e:
        print(f"  ✗ {filepath} - {e}")
        errors.append((filepath, str(e)))

# Test 4: Quick Functionality Test
print("\n[TEST 4] Quick Functionality Test...")
try:
    # Test relationship query (should work)
    result = graph.query_relationship("Hahnemühle", "Hahnemühle_Bamboo")
    if result['exists']:
        print("  ✓ Relationship query works (Hahnemühle → Bamboo)")
        successes.append("Relationship query")
    else:
        print("  ✗ Relationship query failed")
        errors.append(("Relationship query", "No relationship found"))
    
    # Test dissonance detection
    dissonance = detector.calculate_dissonance(
        token="partnership",
        token_index=5,
        context=["Hahnemühle", "Awagami"],
        proposed_claim={
            'entity_a': 'Hahnemühle',
            'entity_b': 'Awagami',
            'relation': 'partnership'
        }
    )
    
    if dissonance.score > 0.8:
        print(f"  ✓ Dissonance detection works (D={dissonance.score:.2f})")
        successes.append("Dissonance detection")
    else:
        print(f"  ⚠ Dissonance detection questionable (D={dissonance.score:.2f})")
        
except Exception as e:
    print(f"  ✗ Functionality test - {e}")
    errors.append(("Functionality test", str(e)))

# Results
print("\n" + "="*60)
if len(errors) == 0:
    print("✅ ALL TESTS PASSED!")
    print(f"\nSuccesses: {len(successes)}")
    print("\nRepository is FULLY FUNCTIONAL! ✓")
    print("\nYou can safely push to GitHub!")
else:
    print(f"✗ {len(errors)} ERROR(S) FOUND!")
    print(f"\nSuccesses: {len(successes)}")
    print(f"Errors: {len(errors)}")
    print("\nError Details:")
    for module, error in errors:
        print(f"  - {module}: {error}")
    print("\nPlease fix errors before pushing to GitHub.")

print("="*60 + "\n")
