# Architecture

ProteinScope v2 uses a scientific-paper-focused RAG architecture.

## Layers

1. Evidence Layer
   - Research papers
   - Scientific articles

2. Retrieval Layer
   - Dense retrieval
   - Hybrid search
   - Reranking

3. Generation Layer
   - Citation-backed answers
   - grounded answer generation

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
Scientific Evidence Retriever
    ↓
Reranker
    ↓
Answer Generator
    ↓
Citation-Backed Response

## Ingestion Pipeline

ProteinScope uses a scientific-document ingestion pipeline.

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

## Improved Section Detection

Section detection now supports:

- clean headings
- numbered headings
- subsection-style headings
- common aliases
- combined Results and Discussion sections

Examples:

1 Introduction              → introduction
2.1 Materials and Methods   → methods
3 Results and Discussion    → results_discussion

This is still a rule-based baseline and will later be compared against layout-aware parsing.

## Section Block Extraction

Page-level section labels are not enough because multiple sections can appear on one page.

ProteinScope will keep both:

pages[]          → raw page-wise extracted text for inspection/citations
section_blocks[] → section-aware text blocks for chunking/retrieval
Example:
{
  "section": "abstract",
  "start_page": 1,
  "end_page": 1,
  "text": "..."
}

{
  "section": "introduction",
  "start_page": 1,
  "end_page": 2,
  "text": "..."
}
This gives us better structure than assigning one section label to an entire page.
Pages remain useful for debugging and citations, while section_blocks will become the primary input for chunking.

## Ingestion Debug Report

Each successful ingestion exports:

outputs/ingestion/{document_id}.json
outputs/ingestion/{document_id}_report.md

The Markdown report summarizes:

* document metadata
* extraction metrics
* section blocks
* page ranges
* character counts
* text previews

This helps validate parser quality before chunking and embedding.

## Baseline Chunking Flow

Current flow:

section_blocks
    ↓
character-based splitter
    ↓
overlap applied
    ↓
metadata-rich chunks
    ↓
export chunks JSON
Each chunk contains:
{
  "chunk_id": "...",
  "document_id": "...",
  "source_type": "scientific_paper",
  "trust_level": "verified",
  "section": "results",
  "start_page": 4,
  "end_page": 5,
  "chunk_index": 12,
  "text": "...",
  "char_count": 800
}
This is the first retrieval-ready data unit.

## Recursive Chunking

ProteinScope now uses recursive chunking for scientific section blocks.

Flow:

section_block
    ↓
paragraph split
    ↓
sentence split if paragraph too large
    ↓
character split only as fallback
    ↓
overlap added between chunks
This improves chunk quality compared to fixed character splitting.

## Chunk Debug Report

Each successful chunking run exports:

outputs/chunks/{document_id}_chunks.json
outputs/chunks/{document_id}_chunks_report.md
The chunk report summarizes:

* total chunks
* average/min/max chunk size
* chunk counts by section
* page ranges
* chunk previews

This helps validate chunk quality before embeddings are generated.

## Chunk Quality Review Checklist

Before embedding chunks, we inspect:

- readability
- chunk size distribution
- section preservation
- page range correctness
- reference section noise
- table extraction quality
- overlap redundancy

This prevents bad chunks from becoming bad embeddings.

## Chunk Validation

Before embeddings, chunks will be checked for:

- very small chunks
- oversized chunks
- missing section labels
- suspicious starts
- empty text

This acts as a quality gate before vector indexing.

## Chunk Overlap Cap

ProteinScope uses sentence-level overlap, but overlap is capped at 250 characters.

Current rule:

if previous_sentence_overlap <= 250 chars:
    prepend overlap
else:
    skip overlap
Chunk validation now fails when chunks are empty, too small, or too large.

## Embedding Layer

ProteinScope will use an abstract embedding provider.

Initial provider:

sentence-transformers/all-MiniLM-L6-v2
Planned structure:
apps/api/app/embeddings/
├── provider.py
├── schemas.py
└── sentence_transformer_provider.py
Design principle:

The rest of the system should not depend directly on one embedding model or vendor.

## Current Embedding Flow

Current flow:

chunks
    ↓
SentenceTransformerEmbeddingProvider
    ↓
normalized embeddings
    ↓
embedding JSON export

Each embedded chunk stores:

* chunk_id
* document_id
* chunk_index
* source_type
* trust_level
* section
* page range
* text
* embedding_model
* embedding vector

Vector DB integration comes next.

## Embedding Debug Report

Each successful embedding run exports:

outputs/embeddings/{document_id}_embeddings.json
outputs/embeddings/{document_id}_embeddings_report.md
The report summarizes:

* embedding count
* embedding model
* vector dimension
* chunk index mapping
* section/page metadata

This helps verify embedding quality before vector DB integration.

## Qdrant Vector Store

ProteinScope stores embedded chunks in Qdrant.

Collection:

proteinscope_chunks
Current vector config:
size = 384
distance = cosine
Each Qdrant point contains:

* vector embedding
* chunk_id
* document_id
* chunk_index
* source_type
* trust_level
* section
* page range
* text
* embedding_model

This enables future dense retrieval and metadata filtering.

## Dense Retrieval Flow

Current search flow:

User Query
    ↓
SentenceTransformerEmbeddingProvider
    ↓
Query Vector
    ↓
Qdrant Similarity Search
    ↓
Top-k Chunks with Metadata
The same embedding model is used for document chunks and user queries.

This is required because vectors must live in the same embedding space.

## Default Retrieval Filter

Default dense retrieval excludes references.

Current filter:

must_not section = references
Reason:

* references often create noisy matches
* scientific QA usually needs abstract, methods, results, discussion, or conclusion
* references can be retrieved later through an explicit reference-specific mode

## Metadata-Aware Dense Retrieval

The `/search` endpoint supports optional metadata filters over scientific document chunks.

Example request:

{
  "query": "what methods were used?",
  "top_k": 5,
  "section": "methods",
  "source_type": "scientific_paper",
  "trust_level": "verified"
}

The API converts these fields into a Qdrant filter using must conditions.
By default, section = references is excluded using must_not unless include_references is true.

## Retrieval Debug Logging

Each `/search` call is logged to JSONL.

Current log path:

outputs/retrieval/search_logs.jsonl
This helps inspect:

* what query was searched
* which filters were applied
* which chunks were returned
* what scores were assigned
* whether retrieved sections were appropriate

This is an early observability layer for retrieval quality.

## BM25 Keyword Retrieval

ProteinScope now supports separate BM25 keyword retrieval.

Flow:

chunks JSON
    ↓
BM25Index
    ↓
keyword scoring
    ↓
top-k chunks

BM25 is useful for exact matches such as:

* gene/protein names
* abbreviations
* dosage values
* section-specific keywords
* paper-specific terms

This prepares the system for hybrid retrieval.
EOF
## Hybrid Retrieval Flow

Current hybrid retrieval flow:

User Query
    ↓
Dense Search in Qdrant
    ↓
BM25 Keyword Search over Chunks
    ↓
Reciprocal Rank Fusion
    ↓
Top-k Hybrid Results
Hybrid retrieval improves coverage because:

* dense retrieval finds semantic matches
* BM25 finds exact keyword matches
* RRF merges both result sets without score normalization

Current endpoint:
POST /search/hybrid

## BM25 Metadata Filtering

BM25 now applies metadata filters before keyword indexing/search.

Flow:

Load chunks
    ↓
Apply metadata filters
    ↓
Build BM25 index
    ↓
Search filtered chunks
This keeps BM25 aligned with dense Qdrant filtering during hybrid retrieval.


## Hybrid Retrieval Logging

Each `/search/hybrid` call logs:

- query
- filters
- dense results
- BM25 results
- fused hybrid results
- dense_rank
- bm25_rank
- fusion_score

This makes hybrid retrieval observable and easier to evaluate.

## Reranking Flow

ProteinScope now supports reranking after hybrid retrieval.

Flow:

User Query
    ↓
Dense Search
    ↓
BM25 Search
    ↓
RRF Fusion
    ↓
Candidate Chunks
    ↓
Cross-Encoder Reranker
    ↓
Final Top-k Chunks

Endpoint:
POST /search/rerank

Reranking improves precision by scoring query-chunk pairs more carefully than approximate retrieval.


## Retrieval Evaluation Baseline

ProteinScope starts retrieval evaluation with a small JSON eval set.

Current eval file:
apps/api/evals/retrieval_eval_set.json

Initial metrics:

* Hit@K
* Precision@K
* Recall@K

Current relevance signal:
retrieved chunk section ∈ relevant_sections

This will later be upgraded to chunk-level golden labels.

## Retrieval Evaluation Script

Current evaluation runner:

apps/api/run_retrieval_eval.py
It evaluates hybrid retrieval using:

* Hit@K
* Precision@K
* retrieved sections
* retrieved chunk indices

Outputs:
outputs/evals/retrieval_eval_results.json

## Retrieval Strategy Evaluation

The retrieval evaluator now compares:

Dense
BM25
Hybrid
Reranked Hybrid
For each strategy, it reports:

* Hit@K
* Precision@K
* retrieved sections
* retrieved chunk indices

This allows us to quantify improvements from hybrid retrieval and reranking.

## Scientific PDF Parsing With GROBID

ProteinScope now uses a production-style scientific parsing strategy.

Flow:

PDF
    ↓
PyMuPDF page extraction
    ↓
GROBID TEI XML extraction
    ↓
Structured title / author / abstract / sections
    ↓
Section blocks for chunking
    ↓
PyMuPDF fallback if GROBID fails
This avoids relying only on regex-based heading detection.

## Grounded Answer Generation

ProteinScope now supports a baseline answer endpoint.

Flow:

Question
    ↓
Hybrid Retrieval
    ↓
Top-k Context Chunks
    ↓
Grounded Prompt
    ↓
Generator
    ↓
Answer + Citations
Endpoint:
POST /answer
Answers are generated from retrieved scientific evidence and returned with citations.

## Groq Generation Provider

ProteinScope now supports Groq-based grounded generation.

Flow:

Question
    ↓
Hybrid Retrieval
    ↓
Grounded Prompt
    ↓
GroqGenerationProvider
    ↓
Answer with source citations
The generation layer uses a provider abstraction so model vendors can be swapped later.


## Generation Observability

Each `/answer` request is logged to:

outputs/generation/answer_logs.jsonl
The response now includes:

* generator_model
* retrieval_strategy
* citations
* retrieved_context

This improves answer traceability and prepares the system for answer evaluation.

cat >> docs/architecture.md <<'EOF'

## Answer Evaluation

ProteinScope now includes a basic answer evaluation runner:
apps/api/run_answer_eval.py

It evaluates answer logs from:
outputs/generation/answer_logs.jsonl

Current metrics:

* pass rate
* citation usage rate
* citation validity
* context availability

## LLM-as-Judge Evaluation

ProteinScope supports optional LLM-as-judge answer evaluation.

Runner:

apps/api/run_answer_eval.py --use-llm-judge
Outputs:
outputs/evals/answer_judge_results.json
Current metrics:

* faithfulness
* relevance
* completeness
* citation_quality

## Expected Topic Coverage

Batch answer evaluation now computes topic coverage.

For each answer:

expected_topics
    ↓
keyword matching against answer
    ↓
matched topics / missing topics
    ↓
topic_coverage score
This gives a measurable completeness metric for answer generation.

## Answer Guardrails

ProteinScope now includes guardrails around grounded generation.

Flow:

Question
    ↓
Hybrid Retrieval
    ↓
Retrieval Guardrail
    ↓
Grounded Generation
    ↓
Answer Guardrail
    ↓
Answer + Citations
Guardrails currently check context availability, weak retrieval confidence, citation presence, and health-advice-style questions.

## Cached Providers

ProteinScope now uses cached provider dependencies.

Current file:

apps/api/app/dependencies.py
Cached services:

* embedding model
* vector store client
* LLM client
* reranker model

This reduces request latency by avoiding repeated model/client initialization.

## BM25 Index Cache

ProteinScope now caches BM25 indexes.

File:

apps/api/app/retrieval/bm25_cache.py
Flow:
chunks_path + filters
    ↓
cached BM25Index
    ↓
keyword retrieval
This reduces latency for repeated BM25, hybrid, rerank, and answer requests.


## API Latency Observability

ProteinScope now logs API request latency.

Middleware:
apps/api/app/observability/latency_logger.py

Output:
outputs/observability/api_latency_logs.jsonl

The API also returns an X-Process-Time-ms response header for each request.


## Latency Reporting

ProteinScope includes a latency report runner:

apps/api/run_latency_report.py

It reads:
outputs/observability/api_latency_logs.jsonl

and writes:
outputs/observability/api_latency_summary.json

This allows endpoint-level latency benchmarking.

## Health Checks

ProteinScope exposes:

GET /
GET /health
The /health endpoint checks:

* Qdrant
* GROBID
* Groq LLM configuration

This improves deployment observability.

## Runtime Configuration

ProteinScope now uses a central config module:

apps/api/app/config.py
It controls:

* Qdrant URL
* GROBID URL
* Groq API key
* Groq model

This keeps local and Docker deployments consistent.

## Document Registry

ProteinScope now maintains a lightweight JSON document registry.

Endpoints:

GET /documents
GET /documents/{document_id}
This enables frontend document selection and prepares for future database-backed document management.

