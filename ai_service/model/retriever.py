import logging
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from model.embeddings import EmbeddingManager

logger = logging.getLogger(__name__)

class SemanticRetriever:
    """
    Performs semantic search over NCERT content using FAISS
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_manager = EmbeddingManager(model_name)
        self.index = None
        self.texts = None
        self._load_index()
    
    def _load_index(self):
        """Load the pre-built FAISS index and metadata"""
        try:
            self.index, self.texts = self.embedding_manager.load_index()
            logger.info("FAISS index loaded successfully")
        except FileNotFoundError as e:
            logger.error(str(e))
            self.index = None
            self.texts = []
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for the most relevant text chunks for a given query
        
        Args:
            query: User's question
            top_k: Number of top results to return
            
        Returns:
            List of tuples (text_chunk, similarity_score)
        """
        if self.index is None or not self.texts:
            logger.error("Index not loaded. Cannot perform search.")
            return []
        
        # Create query embedding
        query_embedding = self.embedding_manager.model.encode([query], convert_to_numpy=True)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.texts):
                results.append((self.texts[idx], float(score)))
        
        logger.info(f"Retrieved {len(results)} relevant chunks for query")
        return results
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Get concatenated context from top matching chunks
        
        Args:
            query: User's question
            top_k: Number of chunks to include
            
        Returns:
            Concatenated context string
        """
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, (text, score) in enumerate(results, 1):
            context_parts.append(f"[Passage {i}] {text}")
        
        return "\n\n".join(context_parts)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    retriever = SemanticRetriever()
    
    # Test query
    test_query = "What is photosynthesis?"
    results = retriever.search(test_query, top_k=3)
    
    print(f"\nQuery: {test_query}\n")
    for i, (text, score) in enumerate(results, 1):
        print(f"Result {i} (score: {score:.4f}):")
        print(f"{text[:200]}...\n")
