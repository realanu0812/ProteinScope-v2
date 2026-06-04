# Architecture Decision Records

This file tracks important technical decisions made during the project.

## Decision 1: Use Monorepo

We will use a monorepo structure with separate apps for frontend and backend.

Reason:
- Easier development
- Easier deployment coordination
- Better for a full-stack AI project

## Decision 2: Separate Evidence and Community Sources

Scientific papers and Reddit/community experiences will be stored and retrieved separately.

Reason:
- Scientific evidence is verified
- Reddit data is anecdotal
- The final answer should never mix anecdotal reports with scientific claims

## Decision 3: Use Next.js for Frontend

We will use Next.js for the frontend.

Reason:
- Professional product experience
- Easy deployment on Vercel
- Strong auth integration
- Better than Streamlit for recruiter-facing projects

Alternatives considered:
- Streamlit
- React SPA

## Decision 4: Use FastAPI for Backend

We will use FastAPI for the backend API.

Reason:
- Python-first RAG ecosystem
- Clean API design
- Async support
- Easy integration with ML libraries

Alternatives considered:
- Flask
- Django
- Node.js

## Decision 5: Use PostgreSQL for Product Data

We will use PostgreSQL for structured data such as users, workspaces, documents, ingestion jobs, and chat history.

Reason:
- Reliable relational database
- Industry standard
- Works well with hosted providers like Supabase and Neon

## Decision 6: Use Qdrant for Vector Search

We will use Qdrant as the vector database.

Reason:
- Strong metadata filtering
- Open-source
- Production-ready
- Easy local development with Docker

Alternatives considered:
- Chroma
- FAISS
- Pinecone
- pgvector

## Decision 7: Keep LLM and Embedding Providers Abstract

We will avoid tightly coupling the app to a single LLM or embedding provider.

Reason:
- Easier to switch between OpenAI, Gemini, local models, or OpenRouter
- Better long-term maintainability
- Cleaner architecture

## Decision 8: Start PDF Ingestion with PyMuPDF

We will start PDF ingestion using PyMuPDF.

Reason:
- Simple page-wise extraction
- Easy to understand
- Good baseline for scientific PDFs
- Supports page-level citation tracking

Alternatives considered:
- Docling
- Tesseract OCR

Docling will be added later for layout-aware parsing, table extraction, and complex scientific PDFs.

OCR will be added later for scanned documents.

## Decision 9: Store Source Type and Trust Level from Ingestion

Every ingested document will have a source_type and trust_level.

Reason:
- Scientific evidence and community experiences must remain separated
- Helps retrieval routing
- Prevents anecdotal data from being treated as verified evidence
- Supports safer answer generation