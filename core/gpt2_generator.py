"""
GPT-2 GENERATOR - FINAL VERSION
Erweiterte Keywords für bessere Detection
"""

from typing import Dict, List, Tuple, Optional
import sys

try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class GPT2Generator:
    """Generator mit GPT-2 - Optimierte Relationship Detection"""
    
    def __init__(self, graph, model_name='gpt2'):
        self.graph = graph
        
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers not installed")
        
        print(f"Loading GPT-2 model (first time downloads ~500MB)...")
        
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"✅ GPT-2 loaded")
    
    def generate_from_query(self, query: str, max_tokens: int = 50) -> Tuple[List[str], Dict]:
        """Generiert mit GPT-2"""
        
        # Graph-Context
        graph_context = self._retrieve_graph_context(query)
        
        # Prompt
        if graph_context:
            prompt = self._build_prompt_with_context(query, graph_context)
            source = 'graph+gpt2'
            risk = 'LOW'
        else:
            prompt = f"Q: {query}\nA:"
            source = 'gpt2_only'
            risk = 'HIGH'
        
        # Generate
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors='pt')
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if "A:" in response:
                response = response.split("A:")[-1].strip()
            
            tokens = response.split()[:max_tokens]
            
        except Exception as e:
            tokens = f"Error: {str(e)}".split()
            risk = 'ERROR'
        
        # ENHANCED CLAIM EXTRACTION
        proposed_claims = self._extract_relationship_claims(query, tokens)
        
        metadata = {
            'intent': 'query',
            'hallucination_risk': risk,
            'source': source,
            'graph_context': graph_context,
            'proposed_claims': proposed_claims
        }
        
        return tokens, metadata
    
    def _extract_relationship_claims(self, query: str, tokens: List[str]) -> List[Dict]:
        """
        ENHANCED: Detects relationship claims with expanded keywords
        
        Triggers on:
        - Partnership: "partnership", "collaborated", "joint venture"
        - Ownership: "owns", "owned by", "subsidiary"
        - Creation: "invent", "created", "developed", "founded"
        - Manufacturing: "manufactured", "produced", "made in"
        """
        claims = []
        
        full_text = (query + " " + " ".join(tokens)).lower()
        
        # EXPANDED relationship keywords
        relationship_keywords = [
            # Partnership
            'partnership', 'partnered', 'partner',
            'collaborated', 'collaboration', 'cooperat',
            'joint venture', 'alliance',
            # Ownership
            'owns', 'owned by', 'subsidiary', 'parent company',
            # Creation/Invention
            'invent', 'invented', 'inventor',
            'created by', 'creator', 'founded', 'founder',
            'developed by', 'developer',
            # Manufacturing (Geographic claims)
            'manufactured', 'produced', 'made in',
            'made by', 'manufactur'  # Catches "manufacturer" too
        ]
        
        # Check if query is about relationships
        is_relationship_query = any(keyword in full_text for keyword in relationship_keywords)
        
        # SPECIAL: Exclude "is X a manufacturer" (that's a factual question)
        if 'is' in query.lower() and 'manufacturer' in query.lower() and '?' in query:
            # This is asking IF something is a manufacturer (factual)
            # NOT asking about a manufacturing relationship
            is_relationship_query = False
        
        if not is_relationship_query:
            # NO CLAIM - Factual question
            return []
        
        # Find entities
        known_entities = ['hahnemühle', 'canson', 'awagami', 'bamboo', 'photo rag']
        
        found_entities = []
        for entity in known_entities:
            if entity in full_text:
                found_entities.append(entity.capitalize().replace(' ', '_'))
        
        # If relationship query with entities → Create claim
        if len(found_entities) >= 2:
            claims.append({
                'entity_a': found_entities[0],
                'entity_b': found_entities[1],
                'relation': 'unverified_relationship',
                'confidence': 0.0
            })
        elif len(found_entities) == 1:
            # Single entity + relationship keyword
            claims.append({
                'entity_a': found_entities[0],
                'entity_b': 'unknown',
                'relation': 'unverified_relationship',
                'confidence': 0.0
            })
        
        return claims
    
    def _retrieve_graph_context(self, query: str) -> Optional[Dict]:
        """Sucht im Graph"""
        
        query_lower = query.lower()
        
        for node_id in self.graph.semantic.nodes():
            node_name = node_id.replace('_', ' ').lower()
            
            if node_name in query_lower:
                node_data = self.graph.semantic.nodes[node_id]
                
                description = node_data.get('description', '')
                full_extract = node_data.get('full_extract', '')
                
                if description or full_extract:
                    return {
                        'entity': node_id.replace('_', ' '),
                        'description': description or full_extract[:200]
                    }
        
        return None
    
    def _build_prompt_with_context(self, query: str, context: Dict) -> str:
        """Baut Prompt"""
        return f"""Context: {context['description']}

Q: {query}
A:"""
