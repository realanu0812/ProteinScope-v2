# Architecture

ProteinScope v2 uses a source-separated RAG architecture.

## Layers

1. Evidence Layer
   - Research papers
   - PubMed
   - Scientific articles

2. Community Layer
   - Reddit discussions
   - User experiences

3. Retrieval Layer
   - Dense retrieval
   - Hybrid search
   - Reranking

4. Generation Layer
   - Citation-backed answers
   - Evidence vs experience separation

## High-Level System Flow

User
 ↓
Next.js Frontend
 ↓
FastAPI Backend
 ↓
PostgreSQL
 ↓
Qdrant Vector Database
 ↓
LLM Provider

## Source-Separated RAG Flow

User Question
    ↓
Query Router
    ↓
Scientific Evidence Retriever
    ↓
Community Experience Retriever
    ↓
Reranker
    ↓
Answer Generator
    ↓
Evidence vs Experience Response

## Ingestion Pipeline

ProteinScope uses a source-aware ingestion pipeline.

Raw Source
    ↓
Load
    ↓
Parse
    ↓
Clean
    ↓
Attach Metadata
    ↓
Prepare for Chunking