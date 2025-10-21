import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiWrapper:
    """
    Optional wrapper for Google Gemini API to enhance answer quality
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini model initialized successfully")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini: {str(e)}")
    
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generate an educational answer using Gemini with retrieved context
        
        Args:
            query: User's question
            context: Retrieved NCERT content
            
        Returns:
            Generated answer
        """
        prompt = f"""You are an educational assistant helping students with NCERT curriculum (Classes 6-10).

**Context from NCERT textbooks:**
{context}

**Student's Question:**
{query}

**Instructions:**
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Use simple, student-friendly language
4. Structure your answer with clear explanations
5. Add examples if relevant from the context
6. Keep the answer educational and encouraging

**Answer:**"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

if __name__ == "__main__":
    # Test only if API key is available
    if os.getenv('GEMINI_API_KEY'):
        wrapper = GeminiWrapper()
        test_context = "Photosynthesis is the process by which plants make their own food using sunlight, water, and carbon dioxide."
        test_query = "What is photosynthesis?"
        
        answer = wrapper.generate_answer(test_query, test_context)
        print(answer)
    else:
        print("GEMINI_API_KEY not set. Skipping test.")
