from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model.response_engine import generate_answer
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="StudyMate AI Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return {
        "status": "success",
        "message": "StudyMate AI Service is running"
    }

@app.post("/ask")
async def ask(query: Query):
    """
    Main endpoint for answering student questions
    """
    try:
        if not query.question or len(query.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Received question: {query.question[:100]}...")
        
        # Generate answer using the AI pipeline
        answer = generate_answer(query.question)
        
        if not answer:
            raise HTTPException(status_code=500, detail="Failed to generate answer")
        
        logger.info("Answer generated successfully")
        
        return {
            "answer": answer,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Check if vector store exists
    vector_store_path = "data/vector_store/faiss_index.faiss"
    if not os.path.exists(vector_store_path):
        logger.warning(
            "Vector store not found! Please run scripts/ingest_pdfs.py "
            "and scripts/rebuild_embeddings.py first."
        )
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
