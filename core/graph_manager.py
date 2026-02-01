"""
GRAPH MANAGER
Zentrale Verwaltung des Knowledge Graphs
Speichert/Lädt automatisch
"""

import os
import json
import pickle
from datetime import datetime
from colorama import Fore


class GraphManager:
    """
    Verwaltet Graph-Persistierung
    
    Features:
    - Auto-Save nach Änderungen
    - Auto-Load beim Start
    - JSON Export
    - Pickle für schnelles Laden
    """
    
    GRAPH_DIR = "D:/claude/data/graph_storage"
    GRAPH_FILE = "knowledge_graph.pkl"
    BACKUP_FILE = "knowledge_graph.json"
    
    @staticmethod
    def ensure_directory():
        """Erstellt Storage-Directory falls nicht existent"""
        os.makedirs(GraphManager.GRAPH_DIR, exist_ok=True)
    
    @staticmethod
    def get_graph_path():
        """Gibt Pfad zur Graph-Datei zurück"""
        GraphManager.ensure_directory()
        return os.path.join(GraphManager.GRAPH_DIR, GraphManager.GRAPH_FILE)
    
    @staticmethod
    def get_backup_path():
        """Gibt Pfad zur Backup-Datei zurück"""
        GraphManager.ensure_directory()
        return os.path.join(GraphManager.GRAPH_DIR, GraphManager.BACKUP_FILE)
    
    @staticmethod
    def save_graph(graph, verbose=True):
        """
        Speichert Graph auf Disk
        
        Args:
            graph: CausalGraph Instanz
            verbose: Print Status
        """
        GraphManager.ensure_directory()
        
        try:
            # Pickle speichern (schnell)
            graph_path = GraphManager.get_graph_path()
            
            graph_data = {
                'semantic': graph.semantic,
                'episodic': graph.episodic,
                'self_model': graph.self_model,
                'metadata': {
                    'saved_at': datetime.now().isoformat(),
                    'stats': graph.get_statistics()
                }
            }
            
            with open(graph_path, 'wb') as f:
                pickle.dump(graph_data, f)
            
            if verbose:
                stats = graph.get_statistics()
                print(f"{Fore.GREEN}✅ Graph saved:")
                print(f"{Fore.WHITE}   File: {graph_path}")
                print(f"{Fore.WHITE}   Nodes: {stats['total_nodes']}")
                print(f"{Fore.WHITE}   Edges: {stats['semantic_edges']}")
            
            # JSON Backup (langsam aber lesbar)
            backup_path = GraphManager.get_backup_path()
            graph.export_to_json(backup_path)
            
            return True
            
        except Exception as e:
            if verbose:
                print(f"{Fore.RED}Error saving graph: {e}")
            return False
    
    @staticmethod
    def load_graph(graph, verbose=True):
        """
        Lädt Graph von Disk
        
        Args:
            graph: CausalGraph Instanz (wird überschrieben)
            verbose: Print Status
        
        Returns:
            True wenn erfolgreich geladen, False sonst
        """
        graph_path = GraphManager.get_graph_path()
        
        if not os.path.exists(graph_path):
            if verbose:
                print(f"{Fore.YELLOW}No saved graph found, using fresh graph")
            return False
        
        try:
            with open(graph_path, 'rb') as f:
                graph_data = pickle.load(f)
            
            # Überschreibe Graph-Daten
            graph.semantic = graph_data['semantic']
            graph.episodic = graph_data['episodic']
            graph.self_model = graph_data['self_model']
            
            if verbose:
                stats = graph.get_statistics()
                saved_at = graph_data['metadata'].get('saved_at', 'Unknown')
                print(f"{Fore.GREEN}✅ Graph loaded:")
                print(f"{Fore.WHITE}   Saved: {saved_at}")
                print(f"{Fore.WHITE}   Nodes: {stats['total_nodes']}")
                print(f"{Fore.WHITE}   Edges: {stats['semantic_edges']}")
            
            return True
            
        except Exception as e:
            if verbose:
                print(f"{Fore.RED}Error loading graph: {e}")
            return False
    
    @staticmethod
    def graph_exists():
        """Prüft ob gespeicherter Graph existiert"""
        return os.path.exists(GraphManager.get_graph_path())
    
    @staticmethod
    def delete_graph(verbose=True):
        """Löscht gespeicherten Graph (Reset)"""
        graph_path = GraphManager.get_graph_path()
        backup_path = GraphManager.get_backup_path()
        
        deleted = False
        
        if os.path.exists(graph_path):
            os.remove(graph_path)
            deleted = True
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        if verbose and deleted:
            print(f"{Fore.YELLOW}Graph deleted - starting fresh")
        
        return deleted


# Patch CausalGraph mit Auto-Save/Load
def patch_causal_graph():
    """
    Erweitert CausalGraph mit Auto-Persistierung
    """
    import sys
    sys.path.append('D:/claude')
    from core.causal_graph import CausalGraph
    
    # Speichere Original __init__
    original_init = CausalGraph.__init__
    
    def new_init(self, auto_load=True):
        """Erweiterte __init__ mit Auto-Load"""
        # Original Init
        original_init(self)
        
        # Auto-Load wenn gewünscht
        if auto_load and GraphManager.graph_exists():
            GraphManager.load_graph(self, verbose=True)
    
    # Ersetze __init__
    CausalGraph.__init__ = new_init
    
    # Füge save-Methode hinzu
    def save(self, verbose=False):
        """Speichert Graph"""
        return GraphManager.save_graph(self, verbose=verbose)
    
    CausalGraph.save = save


# Test
if __name__ == "__main__":
    import sys
    sys.path.append('D:/claude')
    
    from core.causal_graph import CausalGraph
    from colorama import init
    
    init(autoreset=True)
    
    print(f"\n{Fore.CYAN}Testing Graph Manager...")
    
    # Test 1: Neuen Graph erstellen und speichern
    print(f"\n{Fore.YELLOW}TEST 1: Save Graph")
    graph1 = CausalGraph()
    
    # Füge Test-Node hinzu
    graph1.semantic.add_node("Test_Node_123", 
        node_type="test",
        created="now"
    )
    
    stats_before = graph1.get_statistics()
    print(f"{Fore.WHITE}Before save: {stats_before['total_nodes']} nodes")
    
    GraphManager.save_graph(graph1)
    
    # Test 2: Graph laden
    print(f"\n{Fore.YELLOW}TEST 2: Load Graph")
    graph2 = CausalGraph()
    GraphManager.load_graph(graph2)
    
    stats_after = graph2.get_statistics()
    print(f"{Fore.WHITE}After load: {stats_after['total_nodes']} nodes")
    
    # Prüfe ob Test-Node vorhanden
    if graph2.semantic.has_node("Test_Node_123"):
        print(f"{Fore.GREEN}✓ Test node found - persistence works!")
    else:
        print(f"{Fore.RED}✗ Test node missing - persistence broken!")
    
    print()
