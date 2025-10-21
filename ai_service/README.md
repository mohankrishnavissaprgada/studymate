# StudyMate AI Service

Python microservice for AI-powered question answering from NCERT materials.

## Features
- PDF text extraction and preprocessing
- Semantic embeddings using SentenceTransformers
- FAISS-based vector search
- Template-based answer generation
- Optional Gemini API integration

## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Prepare Data
1. Place NCERT PDF files in `data/raw_pdfs/`
2. Run preprocessing:
```bash
cd ../scripts
python ingest_pdfs.py
python rebuild_embeddings.py
```

### Run Service
```bash
python app.py
```

Service runs on http://localhost:5000

## API Endpoints

### GET /
Health check

### POST /ask
Ask a question

**Request:**
```json
{
  "question": "What is photosynthesis?"
}
```

**Response:**
```json
{
  "answer": "...",
  "status": "success"
}
```

## Environment Variables

Create `.env` file:
````
```
