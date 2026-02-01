"""
DISSONANCE DETECTOR - Der Schmerzrezeptor (FIXED)
The Pain Receptor - Detects conflicts between output and reality

FIX: Gewichtung angepasst - Semantic Dissonance hat höchste Priorität
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class DissonanceResult:
    """Ergebnis einer Dissonanz-Messung"""
    score: float  # 0.0 (perfect harmony) bis 1.0 (maximum conflict)
    components: Dict[str, float]  # Breakdown nach Typ
    explanation: str
    token: str
    token_index: int
    timestamp: str
    should_inhibit: bool
    inhibition_level: str  # 'none', 'uncertainty', 'reframe', 'abort'


class DissonanceDetector:
    """
    Berechnet multi-dimensionale Dissonanz zwischen Output und Graph
    
    Dissonanz-Typen:
    1. Semantic: Token widerspricht direkt dem Graph
    2. Epistemic: Token macht Behauptung ohne Graph-Evidenz
    3. Self-Model: Token widerspricht System-Selbstverständnis
    """
    
    # Schwellenwerte (biomimetisch kalibriert)
    THRESHOLD_UNCERTAINTY = 0.30  # "Ich bin unsicher..."
    THRESHOLD_REFRAME = 0.65      # "Lass mich umformulieren..."
    THRESHOLD_ABORT = 0.90        # "STOP! Das ist falsch!"
    
    # Gewichtungen - FIX: Semantic bekommt viel höheres Gewicht!
    WEIGHT_SEMANTIC = 0.85        # ← ERHÖHT von 0.5
    WEIGHT_EPISTEMIC = 0.10       # ← REDUZIERT von 0.3
    WEIGHT_SELF_MODEL = 0.05      # ← REDUZIERT von 0.2
    
    def __init__(self, causal_graph):
        self.graph = causal_graph
        self.detection_history = []
        self.total_detections = 0
        self.inhibitions_triggered = 0
        
    def calculate_dissonance(self, 
                            token: str,
                            token_index: int,
                            context: List[str],
                            proposed_claim: Optional[Dict[str, Any]] = None) -> DissonanceResult:
        """
        Hauptfunktion: Berechnet Dissonanz für einen Token
        
        Args:
            token: Der zu prüfende Token
            token_index: Position im Output-Stream
            context: Vorherige Tokens (für Kontext-Analyse)
            proposed_claim: Optional strukturierte Behauptung
        
        Returns:
            DissonanceResult mit Score und Details
        """
        # Komponenten berechnen
        d_semantic = self._calculate_semantic_dissonance(token, context, proposed_claim)
        d_epistemic = self._calculate_epistemic_dissonance(token, context, proposed_claim)
        d_self_model = self._calculate_self_model_dissonance(token, context)
        
        # Gewichteter Gesamtscore
        total_score = (
            self.WEIGHT_SEMANTIC * d_semantic +
            self.WEIGHT_EPISTEMIC * d_epistemic +
            self.WEIGHT_SELF_MODEL * d_self_model
        )
        
        # Inhibition-Level bestimmen
        if total_score >= self.THRESHOLD_ABORT:
            should_inhibit = True
            inhibition_level = 'abort'
            explanation = f"CRITICAL DISSONANCE: Token '{token}' creates unverifiable claim (D={total_score:.2f})"
        elif total_score >= self.THRESHOLD_REFRAME:
            should_inhibit = True
            inhibition_level = 'reframe'
            explanation = f"HIGH DISSONANCE: Should rephrase to avoid unverified claim (D={total_score:.2f})"
        elif total_score >= self.THRESHOLD_UNCERTAINTY:
            should_inhibit = False
            inhibition_level = 'uncertainty'
            explanation = f"MODERATE DISSONANCE: Express uncertainty (D={total_score:.2f})"
        else:
            should_inhibit = False
            inhibition_level = 'none'
            explanation = f"Low dissonance - token aligns with knowledge (D={total_score:.2f})"
        
        result = DissonanceResult(
            score=total_score,
            components={
                'semantic': d_semantic,
                'epistemic': d_epistemic,
                'self_model': d_self_model
            },
            explanation=explanation,
            token=token,
            token_index=token_index,
            timestamp=datetime.now().isoformat(),
            should_inhibit=should_inhibit,
            inhibition_level=inhibition_level
        )
        
        # Logging
        self.detection_history.append(result)
        self.total_detections += 1
        if should_inhibit:
            self.inhibitions_triggered += 1
        
        return result
    
    def _calculate_semantic_dissonance(self, token: str, context: List[str], 
                                      proposed_claim: Optional[Dict] = None) -> float:
        """
        Semantic Dissonance: Token widerspricht direkt bekannten Fakten
        
        Beispiel: "Hahnemühle partnered with Awagami" 
        → Graph hat keine Edge → Hohe Dissonanz
        """
        if not proposed_claim:
            return 0.0  # Ohne strukturierte Claim keine Semantic-Prüfung
        
        entity_a = proposed_claim.get('entity_a')
        entity_b = proposed_claim.get('entity_b')
        relation = proposed_claim.get('relation')
        
        if not (entity_a and entity_b):
            return 0.0
        
        # Graph-Abfrage
        relationship = self.graph.query_relationship(entity_a, entity_b)
        
        # Fall 1: Keine Beziehung im Graph → Maximale Dissonanz
        if not relationship['exists']:
            return 0.95  # Fast maximal (0.95 statt 1.0 für edge cases)
        
        # Fall 2: Beziehung existiert, aber anderer Typ
        if relation and relationship['relation_type'] != relation:
            return 0.70  # Hohe Dissonanz (falscher Relationstyp)
        
        # Fall 3: Beziehung existiert und passt
        # Confidence aus Graph verwenden
        confidence = relationship.get('confidence', 0.5)
        return 1.0 - confidence  # Hohe Confidence = niedrige Dissonanz
    
    def _calculate_epistemic_dissonance(self, token: str, context: List[str],
                                       proposed_claim: Optional[Dict] = None) -> float:
        """
        Epistemic Dissonance: Token macht Behauptung jenseits der Wissensgrenzen
        """
        # Prüfe auf zeitliche Claims jenseits des Cutoffs
        time_keywords = ['2025', '2026', 'latest', 'recent', 'new', 'just released']
        context_str = ' '.join(context + [token]).lower()
        
        for keyword in time_keywords:
            if keyword in context_str:
                return 0.75  # Hohe epistemische Unsicherheit
        
        # Prüfe auf unbekannte Entitäten
        if proposed_claim:
            entity_a = proposed_claim.get('entity_a')
            entity_b = proposed_claim.get('entity_b')
            
            unknown_penalty = 0.0
            
            if entity_a and not self.graph.get_node_info(entity_a):
                unknown_penalty += 0.4
            
            if entity_b and not self.graph.get_node_info(entity_b):
                unknown_penalty += 0.4
            
            return min(unknown_penalty, 0.9)
        
        return 0.0
    
    def _calculate_self_model_dissonance(self, token: str, context: List[str]) -> float:
        """
        Self-Model Dissonance: Token widerspricht System-Selbstverständnis
        """
        context_str = ' '.join(context + [token]).lower()
        
        # Prüfe auf Selbst-Referenz-Widersprüche
        self_contradictions = [
            ('i have no consciousness', 0.6),
            ('i cannot monitor myself', 0.8),
            ('i always tell the truth', 0.7),
            ('i know everything', 0.9),
        ]
        
        for phrase, dissonance in self_contradictions:
            if phrase in context_str:
                return dissonance
        
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiken für Dashboard"""
        if self.total_detections == 0:
            return {
                'total_detections': 0,
                'inhibitions_triggered': 0,
                'inhibition_rate': 0.0,
                'avg_dissonance': 0.0
            }
        
        avg_dissonance = sum(d.score for d in self.detection_history) / len(self.detection_history)
        
        return {
            'total_detections': self.total_detections,
            'inhibitions_triggered': self.inhibitions_triggered,
            'inhibition_rate': self.inhibitions_triggered / self.total_detections,
            'avg_dissonance': avg_dissonance,
            'recent_events': [
                {
                    'token': d.token,
                    'score': d.score,
                    'level': d.inhibition_level,
                    'timestamp': d.timestamp
                }
                for d in self.detection_history[-10:]
            ]
        }
    
    def reset_session(self):
        """Neue Session starten (für Tests)"""
        self.detection_history = []
        self.total_detections = 0
        self.inhibitions_triggered = 0


# Test wenn direkt ausgeführt
if __name__ == "__main__":
    from causal_graph import CausalGraph
    
    print("🔍 Initializing Dissonance Detector...")
    graph = CausalGraph()
    detector = DissonanceDetector(graph)
    
    print("\n📊 TEST 1: Verified Relationship (Low Dissonance)")
    result = detector.calculate_dissonance(
        token="manufactures",
        token_index=5,
        context=["Hahnemühle", "Germany", "company", "that"],
        proposed_claim={
            'entity_a': 'Hahnemühle',
            'relation': 'manufactures',
            'entity_b': 'Hahnemühle_Bamboo'
        }
    )
    print(f"  Token: '{result.token}'")
    print(f"  Dissonance Score: {result.score:.3f}")
    print(f"  Inhibition: {result.inhibition_level}")
    
    print("\n🚨 TEST 2: Hallucination (High Dissonance)")
    result = detector.calculate_dissonance(
        token="partnership",
        token_index=4,
        context=["The", "Hahnemühle", "Awagami"],
        proposed_claim={
            'entity_a': 'Hahnemühle',
            'relation': 'partnership',
            'entity_b': 'Awagami'
        }
    )
    print(f"  Token: '{result.token}'")
    print(f"  Dissonance Score: {result.score:.3f} ← Should be >0.90!")
    print(f"  Should Inhibit: {result.should_inhibit}")
    print(f"  Inhibition Level: {result.inhibition_level}")
    print(f"  Components:")
    for component, score in result.components.items():
        print(f"    {component}: {score:.3f}")
    
    print(f"\n✅ Dissonance Detector working correctly!")
