import os
import pickle
import logging
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Manages creation and storage of text embeddings using SentenceTransformers and FAISS
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the SentenceTransformer model
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.dimension}")
        
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of text chunks
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        logger.info(f"Creating embeddings for {len(texts)} text chunks")
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        return embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Build FAISS index for fast similarity search
        
        Args:
            embeddings: Numpy array of embeddings
            
        Returns:
            FAISS index
        """
        logger.info("Building FAISS index")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create index
        index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine similarity)
        index.add(embeddings)
        
        logger.info(f"FAISS index built with {index.ntotal} vectors")
        return index
    
    def save_index(self, index: faiss.Index, texts: List[str], 
                   index_path: str = "data/vector_store/faiss_index.faiss",
                   metadata_path: str = "data/vector_store/metadata.pkl"):
        """
        Save FAISS index and associated metadata
        """
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(index, index_path)
        logger.info(f"FAISS index saved to {index_path}")
        
        # Save metadata (original texts)
        metadata = {
            'texts': texts,
            'model_name': self.model_name,
            'dimension': self.dimension
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        logger.info(f"Metadata saved to {metadata_path}")
    
    def load_index(self, index_path: str = "data/vector_store/faiss_index.faiss",
                   metadata_path: str = "data/vector_store/metadata.pkl") -> Tuple[faiss.Index, List[str]]:
        """
        Load FAISS index and metadata
        
        Returns:
            Tuple of (FAISS index, list of texts)
        """
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("FAISS index or metadata not found. Please run rebuild_embeddings.py first.")
        
        # Load FAISS index
        index = faiss.read_index(index_path)
        logger.info(f"FAISS index loaded from {index_path} ({index.ntotal} vectors)")
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        texts = metadata['texts']
        logger.info(f"Metadata loaded: {len(texts)} text chunks")
        
        return index, texts
    
    def build_from_processed_texts(self, processed_dir: str = "data/processed_texts") -> Tuple[faiss.Index, List[str]]:
        """
        Build embeddings and FAISS index from processed text files
        
        Returns:
            Tuple of (FAISS index, list of texts)
        """
        all_chunks = []
        
        if not os.path.exists(processed_dir):
            raise FileNotFoundError(f"Processed texts directory not found: {processed_dir}")
        
        text_files = [f for f in os.listdir(processed_dir) if f.endswith('.txt')]
        
        if not text_files:
            raise ValueError(f"No processed text files found in {processed_dir}")
        
        logger.info(f"Loading {len(text_files)} processed text files")
        
        for text_file in text_files:
            file_path = os.path.join(processed_dir, text_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                chunks = content.split('\n\n---CHUNK---\n\n')
                all_chunks.extend([c.strip() for c in chunks if c.strip()])
        
        logger.info(f"Total chunks collected: {len(all_chunks)}")
        
        # Create embeddings
        embeddings = self.create_embeddings(all_chunks)
        
        # Build FAISS index
        index = self.build_faiss_index(embeddings)
        
        return index, all_chunks

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = EmbeddingManager()
    index, texts = manager.build_from_processed_texts()
    manager.save_index(index, texts)
    
    print(f"Successfully built and saved index with {len(texts)} chunks")
