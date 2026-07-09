# ProteinScope v2

ProteinScope v2 is a production-grade RAG platform that compares scientific evidence with real-world community experiences for protein and nutrition-related topics.

## Vision

Help users answer questions like:

- Is creatine safe?
- What does research say about whey protein?
- What side effects do users report?
- Where do scientific studies and real-world experiences agree or disagree?

## Core Sources

### Evidence Layer

- Research papers
- PubMed
- Scientific articles

### Community Layer

- Reddit discussions
- User experiences

## Planned Features

- Scientific PDF ingestion
- Metadata-aware chunking
- Hybrid retrieval
- Cross-encoder reranking
- Citation-backed answers
- Evaluation dashboard
- Authentication
- Research report generation

## ProteinScope v2 — Local Deployment

ProteinScope runs as a Docker-based stack:

- FastAPI backend
- Qdrant vector database
- GROBID scientific PDF parser

1. Environment setup

Create:
apps/api/.env
Example:
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_URL=http://qdrant:6333
GROBID_URL=http://grobid:8070

2. Start full stack

From project root:
docker compose up --build

3. API docs

Open:
http://localhost:8000/docs

4. Health checks

Basic API health:
curl http://localhost:8000
Dependency health:
curl http://localhost:8000/health
Expected services:

* Qdrant reachable
* GROBID reachable
* Groq configured

5. Ingest a PDF

Use:
POST /ingest/pdf

The ingestion pipeline performs:
PDF upload
→ PyMuPDF page extraction
→ GROBID scientific section parsing
→ section-aware chunking
→ SentenceTransformer embeddings
→ Qdrant vector indexing
→ debug reports

6. Search

Dense search:
POST /search
BM25 search:
POST /search/bm25
Hybrid search:
POST /search/hybrid
Reranked search:
POST /search/rerank

7. Answer generation

Grounded answer generation:
POST /answer
The answer endpoint uses:
Hybrid dense + BM25 retrieval
→ grounded prompt
→ Groq LLM
→ citations
→ guardrails
→ answer logging

8. Evaluation

Retrieval evaluation:
cd apps/api

python run_retrieval_eval.py \
  --eval-path evals/whey_retrieval_eval_set.json \
  --chunks-path outputs/chunks/YOUR_DOCUMENT_ID_chunks.json \
  --top-k 5 \
  --dense-k 30 \
  --bm25-k 30
Batch answer evaluation:
python run_answer_eval_set.py \
  --eval-path evals/whey_answer_eval_set.json \
  --chunks-path outputs/chunks/YOUR_DOCUMENT_ID_chunks.json \
  --top-k 5 \
  --dense-k 30 \
  --bm25-k 30 \
  --use-llm-judge
Latency report:
python run_latency_report.py

9. Observability outputs

ProteinScope writes local debug/evaluation logs to:
apps/api/outputs/retrieval/
apps/api/outputs/generation/
apps/api/outputs/evals/
apps/api/outputs/observability/
These are ignored by git.


### Environment file template

A sample environment file is provided at:

apps/api/.env.example
For local development:
cp apps/api/.env.example apps/api/.env
Then add your actual GROQ_API_KEY.

When running through Docker Compose, service URLs are automatically overridden by compose environment variables.


## Running ProteinScope with Docker Compose

### Start all services
docker compose up --build

This starts:

* Qdrant on http://localhost:6333
* GROBID on http://localhost:8070
* API on http://localhost:8000
* Web app on http://localhost:3000

Stop services
docker compose down

Notes

* API outputs are persisted under apps/api/outputs
* Uploaded PDFs are persisted under apps/api/uploads
* Qdrant data is stored in a Docker volume

## Frontend Environment

The frontend reads:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
Template:
cp apps/web/.env.example apps/web/.env.local
For local Docker Compose, use:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
For deployment, replace it with the deployed backend API URL.
