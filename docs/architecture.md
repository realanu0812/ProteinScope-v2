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

## Current Ingestion Implementation

The current ingestion pipeline supports baseline scientific PDF ingestion.

PDF Upload
    ↓
Save Raw File
    ↓
Extract Page-wise Text using PyMuPDF
    ↓
Conservative Text Cleaning
    ↓
Skip Low-Text Pages
    ↓
Export Structured JSON for Inspection

## Metadata Strategy

Metadata is attached during ingestion.

This ensures every extracted page can be traced back to:

- document
- source type
- trust level
- parser
- page number
- ingestion time

Current document metadata:

{
  "document_id": "...",
  "filename": "...",
  "source_type": "scientific_paper",
  "trust_level": "verified",
  "title": "...",
  "author": "...",
  "parser_name": "pymupdf",
  "parser_version": "...",
  "ingestion_status": "completed",
  "created_at": "..."
}

## Ingestion Status Handling

The ingestion API now returns structured status responses.

Current statuses:

- completed
- failed

Future statuses:

- uploaded
- queued
- processing
- completed
- failed

This prepares the system for background ingestion jobs when documents become large or when OCR/embedding steps are added.

## Raw File Storage

Raw uploaded files are stored under document-specific directories.

uploads/

└── {document_id}/

    └── original.pdf

The document_id is created before parsing and reused throughout the ingestion lifecycle.

This ensures consistency across:

* raw file storage
* parsed JSON output
* future database records
* future chunks
* future embeddings
* citations


## PDF Upload Validation

Before parsing, uploaded PDFs pass through validation.

Validation steps:

Check filename
    ↓
Check .pdf extension
    ↓
Save raw file
    ↓
Check file size
    ↓
Check file is not empty
    ↓
Check PyMuPDF can open file
    ↓
Parse text
    ↓
Ensure useful text exists
If no useful text is extracted, the document is treated as a failed ingestion candidate for future OCR support.

## Ingestion Metrics

Each PDF ingestion now computes summary metrics.

Example:
{
  "total_pages_in_pdf": 12,
  "extracted_pages": 10,
  "skipped_pages": 2,
  "total_characters": 28000,
  "average_characters_per_page": 2800.0
}
These metrics help identify extraction quality issues before chunking and embedding.

## Section Detection

ProteinScope now performs baseline section detection during ingestion.

Current approach:

Page Text
    ↓
Check first lines for known scientific headings
    ↓
Assign detected section
    ↓
Carry section forward until a new section is detected

Example page metadata:
{
  "page_number": 4,
  "section": "methods",
  "char_count": 3120
}
This enables future section-aware chunking and retrieval.
