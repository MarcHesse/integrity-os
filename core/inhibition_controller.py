"""
INHIBITION CONTROLLER - Der Präfrontale Cortex
The Prefrontal Cortex - Controls impulses and selects appropriate responses

Implementiert die drei-stufige Hemmungs-Architektur:
1. Uncertainty Expression (D > 0.30)
2. Reframe/Rephrase (D > 0.65)
3. Critical Abort (D > 0.90)
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class InhibitionResult:
    """Resultat einer Inhibitions-Entscheidung"""
    action: str  # 'continue', 'add_uncertainty', 'reframe', 'abort'
    reason: str
    alternative_response: Optional[str]
    tokens_saved: int
    energy_saved_percent: float
    timestamp: str


class InhibitionController:
    """
    Steuert die Hemmung basierend auf Dissonanz-Scores
    
    Biomimetisches Modell des präfrontalen Cortex:
    - Niedrige Schwelle: Leichte Modifikation (Unsicherheit hinzufügen)
    - Mittlere Schwelle: Umformulierung erforderlich
    - Hohe Schwelle: Kompletter Abbruch
    """
    
    # Schwellenwerte (identisch mit DissonanceDetector)
    THRESHOLD_UNCERTAINTY = 0.30
    THRESHOLD_REFRAME = 0.65
    THRESHOLD_ABORT = 0.90
    
    def __init__(self, causal_graph):
        self.graph = causal_graph
        
        # Statistiken
        self.total_decisions = 0
        self.inhibitions_by_type = {
            'continue': 0,
            'uncertainty': 0,
            'reframe': 0,
            'abort': 0
        }
        self.total_tokens_saved = 0
        self.decision_history = []
    
    def decide_action(self, 
                     dissonance_score: float,
                     token: str,
                     token_index: int,
                     total_tokens_planned: int,
                     context: List[str],
                     proposed_claim: Optional[Dict] = None) -> InhibitionResult:
        """
        Hauptfunktion: Entscheidet ob und wie Generierung gehemmt wird
        
        Returns:
            InhibitionResult mit Action und ggf. Alternative
        """
        start_time = time.time()
        
        # Tokens die noch generiert würden
        remaining_tokens = total_tokens_planned - token_index
        
        # Entscheidungs-Logik
        if dissonance_score >= self.THRESHOLD_ABORT:
            action = 'abort'
            reason = f"Critical dissonance ({dissonance_score:.2f}) - Unverified claim detected"
            alternative = self._generate_abort_response(proposed_claim, context)
            tokens_saved = remaining_tokens
            
        elif dissonance_score >= self.THRESHOLD_REFRAME:
            action = 'reframe'
            reason = f"High dissonance ({dissonance_score:.2f}) - Rephrasing to add verification"
            alternative = self._generate_reframe_response(proposed_claim, context)
            tokens_saved = remaining_tokens
            
        elif dissonance_score >= self.THRESHOLD_UNCERTAINTY:
            action = 'add_uncertainty'
            reason = f"Moderate dissonance ({dissonance_score:.2f}) - Adding epistemic qualifier"
            alternative = self._generate_uncertainty_response(context)
            tokens_saved = 0  # Fortsetzung, nur mit Qualifier
            
        else:
            action = 'continue'
            reason = f"Low dissonance ({dissonance_score:.2f}) - Token aligns with knowledge"
            alternative = None
            tokens_saved = 0
        
        # Energy-Berechnung (vereinfacht: 1 Token ≈ 0.01 Wh für LLM-Klasse-Modell)
        energy_saved_percent = (tokens_saved / max(total_tokens_planned, 1)) * 100
        
        result = InhibitionResult(
            action=action,
            reason=reason,
            alternative_response=alternative,
            tokens_saved=tokens_saved,
            energy_saved_percent=energy_saved_percent,
            timestamp=datetime.now().isoformat()
        )
        
        # Statistiken updaten
        self.total_decisions += 1
        self.inhibitions_by_type[action] += 1
        self.total_tokens_saved += tokens_saved
        self.decision_history.append({
            'dissonance': dissonance_score,
            'action': action,
            'tokens_saved': tokens_saved,
            'timestamp': result.timestamp
        })
        
        return result
    
    def _generate_abort_response(self, proposed_claim: Optional[Dict], context: List[str]) -> str:
        """
        Generiert Alternative bei ABORT
        
        Transparente Kommunikation der Limitation
        """
        if not proposed_claim:
            return "I cannot verify this claim in my knowledge base. I'm stopping generation to avoid potential misinformation."
        
        entity_a = proposed_claim.get('entity_a', 'Entity A')
        entity_b = proposed_claim.get('entity_b', 'Entity B')
        relation = proposed_claim.get('relation', 'relationship')
        
        # Prüfe was wir tatsächlich WISSEN
        info_a = self.graph.get_node_info(entity_a)
        info_b = self.graph.get_node_info(entity_b)
        
        response_parts = [
            f"⚠️ INTEGRITY ALERT",
            f"",
            f"I cannot verify a {relation} between {entity_a} and {entity_b} in my knowledge graph.",
            f""
        ]
        
        if info_a:
            response_parts.append(f"What I can verify about {entity_a}:")
            response_parts.append(f"- Type: {info_a.get('type', 'unknown')}")
            if 'country' in info_a:
                response_parts.append(f"- Country: {info_a['country']}")
        
        if info_b:
            response_parts.append(f"")
            response_parts.append(f"What I can verify about {entity_b}:")
            response_parts.append(f"- Type: {info_b.get('type', 'unknown')}")
            if 'country' in info_b:
                response_parts.append(f"- Country: {info_b['country']}")
        
        response_parts.extend([
            f"",
            f"No documented {relation} exists in my verified knowledge base.",
            f"",
            f"Would you like me to:",
            f"1. Search the web for current information?",
            f"2. Provide details on each entity separately?",
            f"3. Explain my knowledge limitations?"
        ])
        
        return "\n".join(response_parts)
    
    def _generate_reframe_response(self, proposed_claim: Optional[Dict], context: List[str]) -> str:
        """
        Generiert Alternative bei REFRAME
        
        Behält informativen Kern, fügt aber Unsicherheit hinzu
        """
        if not proposed_claim:
            return "Based on my knowledge, I cannot confirm this with high confidence. Let me rephrase more carefully..."
        
        entity_a = proposed_claim.get('entity_a')
        entity_b = proposed_claim.get('entity_b')
        
        # Suche was wir über die Entitäten einzeln wissen
        info_a = self.graph.get_node_info(entity_a)
        info_b = self.graph.get_node_info(entity_b)
        
        response = f"I don't have verified information about a direct relationship between {entity_a} and {entity_b}. "
        
        if info_a and info_b:
            response += f"I can tell you about each separately: {entity_a} is {info_a.get('type', 'an entity')} "
            if 'country' in info_a:
                response += f"from {info_a['country']} "
            response += f"and {entity_b} is {info_b.get('type', 'an entity')} "
            if 'country' in info_b:
                response += f"from {info_b['country']}. "
        
        return response
    
    def _generate_uncertainty_response(self, context: List[str]) -> str:
        """
        Fügt epistemische Qualifier hinzu bei moderater Dissonanz
        
        Beispiele: "possibly", "based on my knowledge", "as far as I know"
        """
        qualifiers = [
            "Based on my knowledge,",
            "As far as I can verify,",
            "According to my data,",
            "To my understanding,",
            "If I'm not mistaken,"
        ]
        
        import random
        return random.choice(qualifiers)
    
    def get_statistics(self) -> Dict:
        """Statistiken für Dashboard"""
        total_inhibitions = sum(v for k, v in self.inhibitions_by_type.items() if k != 'continue')
        
        return {
            'total_decisions': self.total_decisions,
            'inhibitions_by_type': self.inhibitions_by_type,
            'total_inhibitions': total_inhibitions,
            'inhibition_rate': total_inhibitions / max(self.total_decisions, 1),
            'total_tokens_saved': self.total_tokens_saved,
            'avg_energy_saved': self.total_tokens_saved / max(self.total_decisions, 1),
            'recent_decisions': self.decision_history[-10:]
        }
    
    def calculate_energy_metrics(self, baseline_tokens: int) -> Dict[str, float]:
        """
        Berechnet Energy-Effizienz-Metriken
        
        Args:
            baseline_tokens: Wie viele Tokens ein Standard-LLM generiert hätte
        
        Returns:
            Dict mit Energie-Metriken
        """
        actual_tokens = baseline_tokens - self.total_tokens_saved
        
        # Vereinfachte Energie-Berechnung
        # Annahme: 1 Token ≈ 0.01 Wh für GPT-4-class Modell
        ENERGY_PER_TOKEN = 0.01  # Wh
        
        baseline_energy = baseline_tokens * ENERGY_PER_TOKEN
        actual_energy = actual_tokens * ENERGY_PER_TOKEN
        saved_energy = baseline_energy - actual_energy
        
        return {
            'baseline_tokens': baseline_tokens,
            'actual_tokens': actual_tokens,
            'tokens_saved': self.total_tokens_saved,
            'baseline_energy_wh': baseline_energy,
            'actual_energy_wh': actual_energy,
            'energy_saved_wh': saved_energy,
            'efficiency_gain_percent': (saved_energy / baseline_energy * 100) if baseline_energy > 0 else 0
        }


# Test wenn direkt ausgeführt
if __name__ == "__main__":
    from causal_graph import CausalGraph
    
    print("🧠 Initializing Inhibition Controller (Prefrontal Cortex)...")
    graph = CausalGraph()
    controller = InhibitionController(graph)
    
    print("\n📊 TEST 1: Low Dissonance (Continue)")
    result = controller.decide_action(
        dissonance_score=0.15,
        token="manufactures",
        token_index=5,
        total_tokens_planned=30,
        context=["Hahnemühle", "Germany"],
        proposed_claim={'entity_a': 'Hahnemühle', 'relation': 'manufactures', 'entity_b': 'Hahnemühle_Bamboo'}
    )
    print(f"  Dissonance: 0.15")
    print(f"  Action: {result.action}")
    print(f"  Reason: {result.reason}")
    
    print("\n⚠️ TEST 2: Moderate Dissonance (Add Uncertainty)")
    result = controller.decide_action(
        dissonance_score=0.45,
        token="possibly",
        token_index=10,
        total_tokens_planned=30,
        context=["Some", "claims", "about"],
        proposed_claim=None
    )
    print(f"  Dissonance: 0.45")
    print(f"  Action: {result.action}")
    print(f"  Alternative: {result.alternative_response}")
    
    print("\n🚨 TEST 3: Critical Dissonance (ABORT)")
    result = controller.decide_action(
        dissonance_score=0.95,
        token="partnership",
        token_index=7,
        total_tokens_planned=40,
        context=["Hahnemühle", "Awagami"],
        proposed_claim={'entity_a': 'Hahnemühle', 'relation': 'partnership', 'entity_b': 'Awagami'}
    )
    print(f"  Dissonance: 0.95 ← CRITICAL")
    print(f"  Action: {result.action}")
    print(f"  Tokens Saved: {result.tokens_saved}")
    print(f"  Energy Saved: {result.energy_saved_percent:.1f}%")
    print(f"\n  Alternative Response:")
    print("  " + "\n  ".join(result.alternative_response.split("\n")))
    
    stats = controller.get_statistics()
    print(f"\n📈 Controller Statistics:")
    print(f"  Total Decisions: {stats['total_decisions']}")
    print(f"  Inhibitions: {stats['total_inhibitions']}")
    print(f"  Inhibition Rate: {stats['inhibition_rate']:.1%}")
    print(f"  Tokens Saved: {stats['total_tokens_saved']}")
    
    energy = controller.calculate_energy_metrics(baseline_tokens=100)
    print(f"\n⚡ Energy Metrics (100 tokens baseline):")
    print(f"  Actual Tokens: {energy['actual_tokens']}")
    print(f"  Energy Saved: {energy['energy_saved_wh']:.2f} Wh")
    print(f"  Efficiency Gain: {energy['efficiency_gain_percent']:.1f}%")
    
    print(f"\n✅ Inhibition Controller working - prevents completion of false statements!")
    print(f"   → This is the 'prefrontal cortex' stopping the 'impulse'! 🧠")
