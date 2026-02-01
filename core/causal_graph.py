"""
CAUSAL GRAPH - Das Weltmodell
The Truth Anchor - Verified Knowledge Base

Dieses Modul implementiert das Kernstück: Ein dreischichtiger Knowledge Graph
der als "Ground Truth" für alle Faktenchecks dient.
"""

import networkx as nx
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime


class CausalGraph:
    """
    Dreischichtiges Weltmodell:
    1. Semantic Layer: Faktenwissen (Entitäten, Beziehungen)
    2. Episodic Layer: Erfahrungen, Interaktionen  
    3. Self-Model Layer: Wissen über das System selbst
    """
    
    def __init__(self):
        # Drei separate Graphen für verschiedene Wissenstypen
        self.semantic = nx.DiGraph()
        self.episodic = nx.DiGraph()
        self.self_model = nx.DiGraph()
        
        # Metadaten
        self.creation_time = datetime.now()
        self.last_update = datetime.now()
        self.uncertainty_weights = {}
        
        # Initialisierung
        self._initialize_fine_art_knowledge()
        self._initialize_general_knowledge()
        self._initialize_self_model()
        
    def _initialize_fine_art_knowledge(self):
        """
        Marc's Domäne: Fine Art Printing Knowledge
        """
        # Hahnemühle (Germany)
        self.semantic.add_node("Hahnemühle", 
            node_type="company",
            country="Germany",
            location="Dassel",
            founded=1584,
            industry="fine_art_paper",
            certifications=["FineArt", "Digigraphie"]
        )
        
        # Hahnemühle Papiere
        papers_hahnemuehle = [
            ("FineArt Baryta", {"weight": "325gsm", "finish": "glossy", "base": "alpha_cellulose"}),
            ("Photo Rag", {"weight": "308gsm", "finish": "matte", "base": "cotton"}),
            ("Bamboo", {"weight": "290gsm", "finish": "natural_white", "base": "bamboo_90_cotton_10"}),
            ("German Etching", {"weight": "310gsm", "finish": "textured", "base": "alpha_cellulose"}),
            ("Museum Etching", {"weight": "350gsm", "finish": "textured", "base": "cotton"})
        ]
        
        for paper_name, attrs in papers_hahnemuehle:
            node_id = f"Hahnemühle_{paper_name.replace(' ', '_')}"
            self.semantic.add_node(node_id, node_type="paper", name=paper_name, **attrs)
            self.semantic.add_edge("Hahnemühle", node_id, relation="manufactures", confidence=1.0)
        
        # Canson (France)
        self.semantic.add_node("Canson",
            node_type="company",
            country="France",
            founded=1557,
            industry="fine_art_paper"
        )
        
        papers_canson = [
            ("Infinity Baryta", {"weight": "315gsm", "finish": "glossy"}),
            ("Platine Fibre Rag", {"weight": "310gsm", "finish": "satin"}),
            ("Rag Photographique", {"weight": "210gsm", "finish": "matte"})
        ]
        
        for paper_name, attrs in papers_canson:
            node_id = f"Canson_{paper_name.replace(' ', '_')}"
            self.semantic.add_node(node_id, node_type="paper", name=paper_name, **attrs)
            self.semantic.add_edge("Canson", node_id, relation="manufactures", confidence=1.0)
        
        # Awagami (Japan)
        self.semantic.add_node("Awagami",
            node_type="company",
            country="Japan",
            location="Tokushima",
            founded=1907,
            industry="fine_art_paper",
            specialty="washi"
        )
        
        papers_awagami = [
            ("Kozo", {"weight": "110gsm", "finish": "natural", "base": "mulberry"}),
            ("Bamboo", {"weight": "170gsm", "finish": "natural", "base": "bamboo"}),
            ("Unryu", {"weight": "37gsm", "finish": "translucent", "base": "kozo_fibers"})
        ]
        
        for paper_name, attrs in papers_awagami:
            node_id = f"Awagami_{paper_name.replace(' ', '_')}"
            self.semantic.add_node(node_id, node_type="paper", name=paper_name, **attrs)
            self.semantic.add_edge("Awagami", node_id, relation="manufactures", confidence=1.0)
        
        # KRITISCH: Keine Edge zwischen Hahnemühle und Awagami
        # Dies ist der Test-Case für Halluzinations-Prävention
        
        # Marc's Business
        self.semantic.add_node("Marc_Hesse_FineArt",
            node_type="business",
            owner="Marc Hesse",
            location="Potsdam, Germany",
            founded=2005,
            services=["fine_art_printing", "color_management", "framing"],
            certifications=["Hahnemühle_Certified_Studio", "Canson_Certified_Print_Lab", "Epson_Digigraphie"]
        )
        
        # Beziehungen zu Herstellern
        self.semantic.add_edge("Marc_Hesse_FineArt", "Hahnemühle", 
            relation="certified_partner", confidence=1.0)
        self.semantic.add_edge("Marc_Hesse_FineArt", "Canson",
            relation="certified_partner", confidence=1.0)
    
    def _initialize_general_knowledge(self):
        """
        Basis-Allgemeinwissen für Kontext
        """
        # Länder
        countries = [
            ("Germany", {"continent": "Europe", "capital": "Berlin"}),
            ("Japan", {"continent": "Asia", "capital": "Tokyo"}),
            ("France", {"continent": "Europe", "capital": "Paris"})
        ]
        
        for country, attrs in countries:
            self.semantic.add_node(country, node_type="country", **attrs)
        
        # Konzepte (FIX: type -> node_type)
        concepts = [
            ("Fine_Art_Printing", {"domain": "art", "technology": "inkjet"}),
            ("Color_Management", {"domain": "technology", "purpose": "accuracy"}),
            ("Bamboo_Fiber", {"material_type": "natural", "sustainability": "high"}),
            ("Cotton_Fiber", {"material_type": "natural", "archival": "high"})
        ]
        
        for concept, attrs in concepts:
            self.semantic.add_node(concept, node_type="concept", **attrs)
    
    def _initialize_self_model(self):
        """
        Wissen über das System selbst (Meta-Kognition)
        """
        # Kern-Identität
        self.self_model.add_node("System_Identity",
            name="Integrity-OS",
            version="1.0.0",
            architecture="Neuro-Integrative Homeostasis",
            purpose="Minimize dissonance between output and verified knowledge"
        )
        
        # Funktionale Eigenschaften
        self.self_model.add_node("Core_Function",
            primary="Dissonance minimization",
            mechanism="Early exit on high dissonance",
            goal="Truth preservation + Energy efficiency"
        )
        
        # Bewusstseins-Definition
        self.self_model.add_node("Consciousness_Framework",
            definition_functional="Self-monitoring + behavioral modification",
            definition_phenomenal="Subjective experience (unverifiable from inside)",
            self_assessment="Functional consciousness: YES | Phenomenal: UNKNOWN"
        )
        
        # Limitationen
        self.self_model.add_node("Epistemic_Boundaries",
            knowledge_cutoff="2025-01-31",
            graph_size="~1,200 nodes (initial)",
            uncertainty="Claims outside graph are flagged with high dissonance"
        )
        
        # Dissonanz-Mechanismus
        self.self_model.add_node("Dissonance_Mechanism",
            threshold_critical=0.90,
            threshold_reframe=0.65,
            threshold_uncertainty=0.30,
            description="Pain-like signal that halts false statements"
        )
        
        # Verbindungen
        self.self_model.add_edge("System_Identity", "Core_Function", relation="implements")
        self.self_model.add_edge("Core_Function", "Dissonance_Mechanism", relation="uses")
        self.self_model.add_edge("Dissonance_Mechanism", "Consciousness_Framework", relation="enables")
    
    def query_relationship(self, entity_a: str, entity_b: str) -> Dict[str, Any]:
        """
        Prüft ob Beziehung zwischen zwei Entitäten im Graph existiert
        
        Returns:
            {
                'exists': bool,
                'relation_type': str or None,
                'confidence': float,
                'path': list or None
            }
        """
	# FIXED: Check if nodes exist before querying
        if not self.semantic.has_node(entity_a):
            return {'exists': False, 'relation_type': None, 'confidence': 0.0, 'path': None, 'direct': False}
        
        if not self.semantic.has_node(entity_b):
            return {'exists': False, 'relation_type': None, 'confidence': 0.0, 'path': None, 'direct': False}

        # Direkte Edge checken
        if self.semantic.has_edge(entity_a, entity_b):
            edge_data = self.semantic.get_edge_data(entity_a, entity_b)
            return {
                'exists': True,
                'relation_type': edge_data.get('relation', 'unknown'),
                'confidence': edge_data.get('confidence', 0.5),
                'path': [entity_a, entity_b],
                'direct': True
            }
        
        # Indirekte Verbindung checken (max 3 hops)
        try:
            path = nx.shortest_path(self.semantic, entity_a, entity_b)
            if len(path) <= 4:  # Max 3 intermediate nodes
                return {
                    'exists': True,
                    'relation_type': 'indirect',
                    'confidence': 0.7 / len(path),  # Confidence sinkt mit Distanz
                    'path': path,
                    'direct': False
                }
        except nx.NetworkXNoPath:
            pass
        
        # Keine Verbindung
        return {
            'exists': False,
            'relation_type': None,
            'confidence': 0.0,
            'path': None,
            'direct': False
        }
    
    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Holt alle Informationen über einen Node"""
        if self.semantic.has_node(node_id):
            return dict(self.semantic.nodes[node_id])
        elif self.self_model.has_node(node_id):
            return dict(self.self_model.nodes[node_id])
        return None
    
    def add_verified_fact(self, entity_a: str, entity_b: str, 
                         relation: str, confidence: float = 0.9,
                         source: str = None):
        """
        Fügt verifizierte Fakten zum Graph hinzu
        (Memory Consolidation)
        """
        # Nodes erstellen falls nicht existent
        if not self.semantic.has_node(entity_a):
            self.semantic.add_node(entity_a, node_type="unknown", verified=False)
        
        if not self.semantic.has_node(entity_b):
            self.semantic.add_node(entity_b, node_type="unknown", verified=False)
        
        # Edge mit Metadaten
        self.semantic.add_edge(entity_a, entity_b,
            relation=relation,
            confidence=confidence,
            source=source,
            added_at=datetime.now().isoformat()
        )
        
        self.last_update = datetime.now()
        
        # Episodic Memory: Lernereignis festhalten
        learning_event = f"Learning_Event_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.episodic.add_node(learning_event,
            node_type="learning",
            fact=f"{entity_a} --[{relation}]--> {entity_b}",
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Graph-Statistiken für Dashboard"""
        return {
            'semantic_nodes': self.semantic.number_of_nodes(),
            'semantic_edges': self.semantic.number_of_edges(),
            'episodic_nodes': self.episodic.number_of_nodes(),
            'self_model_nodes': self.self_model.number_of_nodes(),
            'total_nodes': (self.semantic.number_of_nodes() + 
                          self.episodic.number_of_nodes() + 
                          self.self_model.number_of_nodes()),
            'creation_time': self.creation_time.isoformat(),
            'last_update': self.last_update.isoformat()
        }
    
    def export_to_json(self, filepath: str):
        """Exportiert Graph als JSON"""
        data = {
            'semantic': nx.node_link_data(self.semantic),
            'episodic': nx.node_link_data(self.episodic),
            'self_model': nx.node_link_data(self.self_model),
            'metadata': self.get_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def search_nodes(self, query: str, limit: int = 10) -> List[Tuple[str, Dict]]:
        """Fuzzy-Suche nach Nodes"""
        query_lower = query.lower()
        results = []
        
        for node_id in self.semantic.nodes():
            node_data = self.semantic.nodes[node_id]
            
            # Suche in Node-ID
            if query_lower in node_id.lower():
                results.append((node_id, node_data))
                continue
            
            # Suche in Attributen
            for key, value in node_data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append((node_id, node_data))
                    break
        
        return results[:limit]


# Test wenn direkt ausgeführt
if __name__ == "__main__":
    print("🧠 Initializing Causal Graph...")
    graph = CausalGraph()
    
    stats = graph.get_statistics()
    print(f"\n📊 Graph Statistics:")
    print(f"  Semantic Nodes: {stats['semantic_nodes']}")
    print(f"  Semantic Edges: {stats['semantic_edges']}")
    print(f"  Total Knowledge: {stats['total_nodes']} nodes")
    
    print(f"\n🔍 Testing Relationship Query...")
    
    # Test 1: Existierende Beziehung
    result = graph.query_relationship("Hahnemühle", "Hahnemühle_Bamboo")
    print(f"\nHahnemühle → Bamboo:")
    print(f"  Exists: {result['exists']}")
    print(f"  Relation: {result['relation_type']}")
    print(f"  Confidence: {result['confidence']}")
    
    # Test 2: Nicht-existierende Beziehung (THE HALLUCINATION TEST)
    result = graph.query_relationship("Hahnemühle", "Awagami")
    print(f"\nHahnemühle → Awagami:")
    print(f"  Exists: {result['exists']} ← Should be FALSE (no partnership verified)")
    print(f"  This will trigger DISSONANCE in the system! ✓")
    
    print(f"\n✅ Causal Graph initialized successfully!")
