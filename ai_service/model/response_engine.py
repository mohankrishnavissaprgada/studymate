import logging
import os
from typing import Optional
from model.retriever import SemanticRetriever
from model.gemini_wrapper import GeminiWrapper

logger = logging.getLogger(__name__)

class ResponseEngine:
    """
    Generates educational responses using retrieved context
    """
    
    def __init__(self, use_gemini: bool = False):
        self.retriever = SemanticRetriever()
        self.use_gemini = use_gemini and os.getenv('GEMINI_API_KEY')
        
        if self.use_gemini:
            try:
                self.gemini = GeminiWrapper()
                logger.info("Gemini integration enabled")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}. Falling back to template-based responses.")
                self.use_gemini = False
        else:
            self.gemini = None
            logger.info("Using template-based response generation")
    
    def format_template_answer(self, query: str, context: str) -> str:
        """
        Generate a structured answer using templates (no LLM)
        """
        if not context:
            return (
                "I apologize, but I couldn't find relevant information in the NCERT materials "
                "to answer your question. Please try rephrasing or asking about topics covered "
                "in NCERT textbooks for classes 6-10 (Science, Maths, or English)."
            )
        
        # Extract key sentences from context
        sentences = context.split('.')
        key_points = [s.strip() + '.' for s in sentences[:5] if len(s.strip()) > 20]
        
        answer_parts = [
            f"Based on the NCERT curriculum, here's what I found about your question:\n",
            f"**Question:** {query}\n",
            f"**Answer:**\n"
        ]
        
        # Add context in a structured way
        for i, point in enumerate(key_points, 1):
            answer_parts.append(f"{i}. {point}\n")
        
        answer_parts.append(
            "\n**Note:** This answer is derived directly from NCERT textbooks. "
            "If you need more details, please ask a more specific question."
        )
        
        return '\n'.join(answer_parts)
    
    def generate(self, query: str, top_k: int = 3) -> str:
        """
        Generate a complete answer for the user's question
        
        Args:
            query: User's question
            top_k: Number of context chunks to retrieve
            
        Returns:
            Formatted answer string
        """
        # Retrieve relevant context
        context = self.retriever.get_context(query, top_k)
        
        # Generate answer
        if self.use_gemini and self.gemini:
            try:
                answer = self.gemini.generate_answer(query, context)
            except Exception as e:
                logger.error(f"Gemini generation failed: {e}. Using template.")
                answer = self.format_template_answer(query, context)
        else:
            answer = self.format_template_answer(query, context)
        
        return answer

# Singleton instance
_response_engine = None

def generate_answer(question: str) -> str:
    """
    Main function called by the API to generate answers
    """
    global _response_engine
    
    if _response_engine is None:
        use_gemini = bool(os.getenv('GEMINI_API_KEY'))
        _response_engine = ResponseEngine(use_gemini=use_gemini)
    
    return _response_engine.generate(question)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    test_question = "Explain the process of respiration in plants"
    answer = generate_answer(test_question)
    print(f"\nQuestion: {test_question}\n")
    print(f"Answer:\n{answer}")
