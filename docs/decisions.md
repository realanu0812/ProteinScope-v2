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

## Decision 10: Export Ingestion Output as JSON

We will export ingested document output as JSON during early development.

Reason:
- Helps inspect PDF parsing quality
- Makes debugging easier before chunking/embedding
- Prevents embedding dirty or broken extracted text
- Allows us to compare parser outputs over time

This export is for development and debugging. In production, parsed outputs will be stored in the database/object storage.

## Decision 11: Use Conservative Text Cleaning

We will use conservative cleaning for scientific PDFs.

Reason:
- Scientific documents contain important symbols and tokens such as TP53, IL-6, TNF-α, p-value < 0.05, mTORC1
- Aggressive regex cleaning can destroy useful biomedical information
- The goal is to remove obvious noise without harming scientific meaning

We currently clean:
- null characters
- excessive whitespace
- repeated blank lines
- standalone page numbers

We intentionally do not remove:
- numbers
- Greek symbols
- hyphens
- punctuation
- scientific notation

## Decision 12: Skip Pages With Very Low Useful Text

We will skip pages where extracted text is too short or mostly non-alphabetic.

Reason:
- Helps remove blank pages
- Detects scanned pages where PyMuPDF extracted no useful text
- Avoids storing pages that only contain headers, footers, or page numbers

This is a temporary baseline. Later, scanned pages will be routed to OCR instead of simply being skipped.

## Decision 13: Attach Metadata During Ingestion

We will attach document and page metadata during ingestion instead of waiting until retrieval.

Reason:
- Metadata is needed for citations
- Metadata enables filtering by source type and trust level
- Metadata helps debug poor retrieval results
- Metadata supports future user/workspace isolation
- Metadata supports parser/version tracking

Each ingested document currently stores:
- document_id
- filename
- source_type
- trust_level
- title
- author
- parser_name
- parser_version
- ingestion_status
- created_at

Each page currently stores:
- page_number
- text
- char_count
- is_empty

## Decision 14: Use Explicit Ingestion Response Status

We will return structured ingestion responses with status values such as completed and failed.

Reason:
- Makes API behavior predictable
- Prepares the system for future async/background ingestion
- Improves frontend UX
- Helps debugging failed parsing jobs

Current response fields:
- status
- message
- output_path
- document
- error

## Decision 15: Store Raw Files Under Document ID Directories

Uploaded raw files will be stored using document-specific directories.

Current structure:
uploads/{document_id}/original.pdf

Reason:

* Avoids filename collisions
* Preserves raw source files for future reprocessing
* Keeps all document artifacts grouped together
* Prepares for future derived files such as parsed JSON, chunks, OCR outputs, and embeddings

We create document_id before parsing so the same ID can be reused across raw storage, parsed output, chunks, vectors, and citations.

## Decision 16: Validate Uploaded PDFs Before Parsing

We will validate uploaded PDFs before running the parser.

Current validations:
- filename must exist
- extension must be .pdf
- file must not be empty
- file must be under 25 MB
- file must be openable by PyMuPDF
- file must contain at least one useful extracted text page

Reason:
- Prevents corrupted files from reaching parser logic
- Makes API errors clearer
- Protects backend from very large uploads during early development
- Helps detect scanned PDFs that require OCR

Current limitation:
- File extension validation is not enough for production security.
- Later we may add MIME type detection and stricter content validation.

## Decision 17: Track Ingestion Summary Metrics

We will compute summary metrics for every ingested PDF.

Current metrics:
- total_pages_in_pdf
- extracted_pages
- skipped_pages
- total_characters
- average_characters_per_page

Reason:
- Helps quickly inspect extraction quality
- Detects suspicious parser output
- Helps identify scanned PDFs or low-quality extraction
- Provides useful debugging signals before chunking and embedding

## Decision 18: Add Baseline Scientific Section Detection

We will add simple rule-based section detection during PDF ingestion.

Current detected sections:
- abstract
- introduction/background
- methods/materials and methods/methodology
- results/findings
- discussion
- conclusion
- references

Reason:
- Scientific papers have meaningful structure
- Section metadata improves future chunking and retrieval
- Users may ask section-specific questions such as study methods or findings
- This prepares the system for section-aware retrieval

Current limitation:
- Detection is rule-based and may miss numbered or layout-heavy headings.
- Later, Docling/layout-aware parsing can improve section extraction.

## Decision 19: Improve Section Detection for Numbered Scientific Headings

We will support common numbered scientific section headings.

Examples:
- 1 Introduction
- 1. Introduction
- 2.1 Materials and Methods
- 3 Results and Discussion

Reason:
- Scientific papers frequently use numbered sections
- Section metadata improves chunking and retrieval
- More accurate section detection helps answer method/result/conclusion-specific questions

Current limitation:
- This remains rule-based
- It may still fail on complex layouts, multi-column PDFs, or visually styled headings
- Later layout-aware parsing can improve this

## Decision 20: Move From Page-Level Section Labels to Section Blocks

Page-level section detection is not sufficient for scientific papers because multiple sections can start on the same page.

Example:
- Abstract and Introduction may both appear on page 1
- Results and Discussion may appear on the same page
- Conclusion may start halfway through a page

We will keep page-level extracted text for inspection and citations, but introduce section_blocks for section-aware chunking and retrieval.

Reason:
- Avoids assigning an entire page to the wrong section
- Preserves scientific document structure more accurately
- Improves future chunking quality
- Supports section-specific retrieval

New structure:
- pages: raw page-wise extraction
- section_blocks: continuous text grouped by detected section

## Decision 21: Implement Section Blocks for Scientific Papers

We implemented section_blocks in addition to page-wise extraction.

Reason:
- Multiple sections can appear on the same page
- Page-level section labels are too coarse
- Section blocks are better suited for future chunking and retrieval
- Pages are still preserved for inspection and citation support

Current structure:
- pages: raw page-wise text
- section_blocks: continuous section-aware text spans

Current limitation:
- Section block extraction is still rule-based
- Complex layouts may require Docling/layout-aware parsing later

## Decision 22: Generate Markdown Ingestion Debug Reports

We will generate a Markdown report for every successful PDF ingestion during development.

Reason:
- Large JSON outputs are difficult to inspect manually
- Reports make parser quality easier to review
- Reports show section blocks, page ranges, and character counts clearly
- Helps catch ingestion issues before chunking and embedding

Current report path:

outputs/ingestion/{document_id}_report.md
In production, this may become an internal admin/debug view instead of a local Markdown file.

## Decision 23: Start With Section-Aware Character-Based Chunking

We will start chunking from section_blocks, not raw pages.

Current chunking strategy:
- input: section_blocks
- target size: 800 characters
- overlap: 150 characters
- metadata preserved on every chunk

Reason:
- section_blocks preserve scientific document structure
- character-based splitting is simple and model-independent
- overlap reduces boundary context loss
- every chunk remains traceable to document, section, and page range

Current limitation:
- character-based chunking is not token-aware
- chunks may split mid-sentence
- later we will improve this with recursive paragraph/sentence splitting

## Decision 24: Upgrade to Recursive Chunking

We upgraded from simple character-based chunking to recursive chunking.

Current splitting priority:
1. Preserve section blocks
2. Preserve paragraphs
3. Split large paragraphs into sentences
4. Split oversized sentences by characters only as fallback
5. Add overlap between neighboring chunks

Reason:
- Reduces mid-sentence splitting
- Preserves more semantic meaning
- Produces better retrieval units
- Still remains simple and debuggable

Current limitation:
- Sentence splitting is regex-based
- Scientific abbreviations may still cause imperfect splits
- Later we may use token-aware or NLP-based splitting

## Decision 25: Generate Chunk Debug Reports

We will generate a Markdown report after chunking.

Reason:
- Chunk JSON is difficult to manually inspect
- Chunk quality must be checked before embeddings
- Report helps identify bad chunk sizes, missing sections, and broken text
- Supports faster iteration on chunking strategy

Current report path:
outputs/chunks/{document_id}_chunks_report.md

## Decision 26: Review Chunk Quality Before Embedding

We will inspect chunk reports before generating embeddings.

Reason:
- Embeddings preserve the quality of input text
- Bad chunks lead to poor retrieval
- Chunking issues are easier to fix before indexing
- This avoids polluting the vector database with low-quality vectors

## Decision 27: Replace Character-Level Overlap With Sentence-Level Overlap

We observed that character-level overlap caused some chunks to start in the middle of words or sentences.

Problem example:
- chunk starts with `resent GenericAgent...`
- chunk starts with `e at the outset...`

We replaced character-level overlap with sentence-level overlap.

Reason:
- Prevents broken chunk starts
- Preserves semantic readability
- Makes chunks better retrieval units
- Improves future citation-backed generation quality

Current strategy:
- split by paragraphs
- split paragraphs into sentences
- group sentences up to target chunk size
- use the last full sentence from the previous chunk as overlap
- split oversized sentences only on word boundaries

Current limitation:
- sentence splitting is still regex-based
- scientific abbreviations may still be imperfect
- later we may use token-aware or NLP-based splitting

## Decision 28: Add Chunk Validation Before Embeddings

We will validate chunks before generating embeddings.

Reason:
- Bad chunks create bad embeddings
- Chunk issues are easier to fix before vector indexing
- Validation catches extremely small, oversized, or poorly structured chunks
- This creates a quality gate before retrieval

## Decision 29: Cap Sentence-Level Overlap to Avoid Oversized Chunks

After inspecting the chunk report, we found oversized chunks even after switching to sentence-level overlap.

Cause:
- Some scientific PDFs contain tables, code blocks, or figure text that the regex sentence splitter treats as one very long sentence.
- When that long sentence is reused as overlap, the next chunk can become much larger than the target size.

Decision:
- Keep sentence-level overlap only when overlap text is at most 250 characters.
- Skip overlap when the previous sentence-like unit is too large.
- Make validation fail when chunks are too small or too large.

Reason:
- Prevents oversized chunks
- Keeps chunks readable
- Avoids mid-word overlap
- Improves quality before embeddings

## Decision 30: Start With Local Sentence Transformer Embeddings

We will start embedding chunks using a local Sentence Transformer model.

Initial model:
- sentence-transformers/all-MiniLM-L6-v2

Reason:
- Free for local experimentation
- Fast enough for development
- Avoids API cost during early iteration
- Helps understand embeddings directly before using managed providers

Current limitation:
- May be weaker than larger embedding models
- CPU inference may be slower for large documents
- Later we may add OpenAI, Gemini, BGE, or E5 through the same provider abstraction

## Decision 31: Export Embeddings Locally Before Vector DB Integration

We will export chunk embeddings to JSON before adding Qdrant.

Reason:
- Helps inspect embedding output shape
- Keeps embeddings phase separate from vector database setup
- Makes debugging easier
- Allows us to verify chunk-to-vector mapping before indexing

Current output:
outputs/embeddings/{document_id}_embeddings.json

## Decision 32: Generate Embedding Debug Reports

We will generate a Markdown report after embedding generation.

Reason:
- Confirms embedding count matches chunk count
- Confirms vector dimension
- Confirms embedding model name
- Helps inspect chunk-to-vector mapping before vector database indexing

Current report path:
outputs/embeddings/{document_id}_embeddings_report.md

## Decision 33: Use Qdrant for Dense Vector Storage

We will use Qdrant as the first vector database.

Reason:
- Supports vector similarity search
- Supports metadata payloads
- Supports filtering
- Runs locally with Docker
- Good fit for production-style RAG systems

Initial collection:
- name: proteinscope_chunks
- vector size: 384
- distance: cosine

Current limitation:
- Collection size is tied to all-MiniLM-L6-v2 embedding dimension.
- If embedding model changes, vectors must be re-indexed or a new collection must be created.

## Decision 34: Add Baseline Dense Retrieval Endpoint

We added a basic dense retrieval endpoint using query embeddings and Qdrant similarity search.

Current flow:
- user query
- embed query using same embedding provider as documents
- search Qdrant
- return top-k chunks with metadata

Reason:
- Verifies that indexed chunks are searchable
- Establishes the first retrieval layer
- Lets us inspect retrieval quality before generation
- Keeps retrieval separate from LLM answering

Current limitation:
- Dense retrieval only
- No hybrid BM25 yet
- No reranking yet
- No metadata filters yet

## Decision 35: Exclude References From Default Retrieval

We observed that dense retrieval returned references for broad queries like "what methods were used?"

Reason:
- References contain many overlapping academic terms
- Dense retrieval treats all indexed chunks equally
- References are usually low-value for answering content questions

Decision:
- Exclude section=references from default search results
- Later, allow references only when user explicitly asks for bibliography/source references

This is an example of metadata-aware retrieval improving dense search quality.

## Decision 36: Add Metadata-Aware Dense Retrieval Filters

We extended dense retrieval to support optional metadata filters.

Current supported filters:

* document_id
* source_type
* trust_level
* section
* include_references

Default behavior:

* references are excluded unless include_references is true

Reason:

* improves retrieval precision
* supports source-separated retrieval
* prepares for Evidence vs Community routing
* supports future user/workspace-specific retrieval

This is our first flexible metadata-aware retrieval layer.

## Decision 37: Log Search Events for Retrieval Debugging

We will log every search request and its returned chunks.

Logged fields:
- timestamp
- query
- filters
- top_k
- scores
- chunk IDs
- sections
- page ranges
- text previews

Reason:
- Helps debug poor retrieval
- Helps compare retrieval improvements over time
- Prepares for future retrieval evaluation
- Makes dense retrieval behavior observable

Current output:
outputs/retrieval/search_logs.jsonl

## Decision 38: Add BM25 Keyword Retrieval as a Separate Endpoint

We added BM25 keyword retrieval before implementing hybrid search.

Current endpoint:

POST /search/bm25
Reason:

* BM25 catches exact terms that dense embeddings may miss
* Scientific/biomedical text contains exact tokens like TP53, IL-6, EGFR, p-value, and dosage values
* Keeping BM25 separate first makes comparison with dense retrieval easier
* Hybrid search will later combine dense and BM25 results

Current limitation:

* BM25 index is built from exported chunk JSON per request
* This is acceptable for learning/debugging, but not production-efficient
* Later we will use a persistent keyword index or database-backed full-text search

## Decision 39: Combine Dense and BM25 Retrieval With Reciprocal Rank Fusion

We added hybrid retrieval by combining Qdrant dense search and BM25 keyword search.

Fusion method:
- Reciprocal Rank Fusion (RRF)

Reason:
- Dense search captures semantic similarity
- BM25 captures exact scientific terms, IDs, abbreviations, and dosage values
- Dense and BM25 scores live on different scales, so direct score addition is unreliable
- RRF combines ranked lists without needing score normalization

Current endpoint:

POST /search/hybrid
Current limitation:

* BM25 index is still loaded from exported chunks JSON per request
* Later this should move to persistent full-text search or cached indexes


## Decision 40: Apply Metadata Filters to BM25 Retrieval

We updated BM25 retrieval to support the same metadata filtering logic used by dense retrieval.

Supported filters:
- document_id
- source_type
- trust_level
- section
- include_references

Reason:
- Hybrid retrieval should not combine filtered dense results with unfiltered BM25 results
- Prevents references or wrong source types from leaking into hybrid results
- Prepares the system for source-separated Evidence vs Community retrieval
- Keeps retrieval behavior consistent across dense and sparse search

## Decision 41: Log Hybrid Retrieval Rankings

We will log dense, BM25, and fused hybrid rankings for every hybrid search.

Reason:
- Helps compare dense-only vs keyword-only vs hybrid retrieval
- Makes RRF behavior transparent
- Helps debug ranking disagreements
- Prepares for retrieval evaluation and precision@k analysis

Current output:

outputs/retrieval/hybrid_search_logs.jsonl

## Decision 42: Add Cross-Encoder Reranking After Hybrid Retrieval

We added a local cross-encoder reranker after hybrid retrieval.

Current reranker:
- cross-encoder/ms-marco-MiniLM-L-6-v2

Current flow:
- dense search
- BM25 search
- Reciprocal Rank Fusion
- top candidate chunks
- cross-encoder reranking
- final top-k chunks

Reason:
- Dense and BM25 retrieval are fast but approximate
- Reranking compares query and chunk text more directly
- Improves precision before context is passed to the LLM
- Creates a production-style retrieval pipeline

Current limitation:
- Cross-encoder reranking adds latency
- Current reranker is general-purpose, not domain-specific biomedical
- Later we may compare with BGE rerankers or hosted rerank APIs

## Decision 43: Start Retrieval Evaluation With Section-Based Labels

We will start retrieval evaluation using section-based relevance labels.

Reason:
- Faster than manually labeling chunk IDs
- Good enough to compare early dense/BM25/hybrid/reranked retrieval behavior
- Helps verify that method queries retrieve methods, result queries retrieve results, etc.
- Creates a baseline before building a more rigorous golden dataset

Current limitation:
- Section labels are only a weak proxy for relevance
- Later evaluation should use manually labeled relevant chunk IDs and answer-level metrics

## Decision 44: Add Retrieval Evaluation Script

We added a retrieval evaluation script that computes section-based Hit@K and Precision@K.

Reason:
- Lets us compare retrieval strategies objectively
- Creates measurable RAG quality metrics
- Helps validate hybrid retrieval before generation
- Prepares for future chunk-level and answer-level evaluation

Current limitation:
- Uses section labels as proxy relevance
- Later evaluation should use manually labeled relevant chunk IDs

## Decision 45: Compare Dense, BM25, Hybrid, and Reranked Retrieval

We upgraded retrieval evaluation to compare multiple retrieval strategies side by side.

Compared strategies:
- dense
- BM25
- hybrid
- reranked hybrid

Reason:
- Shows whether hybrid retrieval improves over dense-only search
- Shows whether reranking improves precision
- Produces measurable RAG quality metrics for iteration
- Helps justify architectural decisions in interviews and documentation

Current metrics:
- Hit@K
- Precision@K

Current limitation:
- Relevance is still section-based, not manually labeled chunk-level relevance

## Decision 46: Use General Heading-Based Section Detection

We replaced paper-specific section detection with a general heading detector.

Current strategy:
- detect common academic sections such as abstract, introduction, methods, results, discussion, conclusion, and references
- detect uppercase standalone headings
- detect title-case standalone headings
- normalize detected headings into slug-style section names

Reason:
- avoids hardcoding one paper's headings
- works across scientific, nutrition, biomedical, and AI papers
- preserves specific section names while remaining general

Current limitation:
- rule-based heading detection may still create false positives
- later Docling/layout-aware parsing can improve heading detection

## Decision 47: Add GROBID as Scientific Paper Parser

We added GROBID as the production-style parser for scholarly PDFs.

Reason:
- Regex-based section detection failed on multi-line headings and references
- GROBID is designed for academic paper structure extraction
- It extracts title, authors, abstract, body sections, and bibliography from scholarly PDFs
- This gives more reliable section blocks for scientific RAG

Current parser strategy:
- PyMuPDF extracts page-wise text for inspection and citations
- GROBID extracts scholarly structure and section blocks
- PyMuPDF section detection remains as fallback

Current limitation:
- GROBID does not always provide perfect page ranges, so page ranges are estimated from PyMuPDF text

## Decision 48: Add Grounded Answer Endpoint With Citations

We added a baseline `/answer` endpoint.

Current flow:
- question
- hybrid retrieval
- prompt construction
- simple extractive generator
- citation metadata returned

Reason:
- separates retrieval from generation
- validates answer API shape before adding LLM providers
- ensures every answer has citation-ready retrieved context
- prepares for grounded generation with Groq/OpenAI/Gemini

Current limitation:
- generator is temporary and does not call a real LLM yet

## Decision 49: Add Groq LLM Provider for Grounded Generation

We replaced the temporary extractive generator with a Groq LLM provider.

Reason:
- Enables real grounded answer generation
- Keeps generation behind a provider abstraction
- Allows later swapping between Groq, OpenAI, Gemini, or local models
- Maintains citation-first prompt structure

Current model:
- llama-3.3-70b-versatile

Current limitation:
- No answer-level evaluation yet
- No automatic faithfulness scoring yet

## Decision 50: Log Answer Generation Events

We added generation logging for `/answer`.

Logged fields:
- timestamp
- question
- generator model
- retrieval strategy
- retrieval parameters
- filters
- answer
- citations
- retrieved context preview

Reason:
- Makes generation observable
- Helps debug hallucinations and citation issues
- Supports future answer-level evaluation
- Provides traceability for generated research answers

Current output:

outputs/generation/answer_logs.jsonl

## Decision 51: Add Rule-Based Answer Evaluation

We added a basic answer evaluation script.

Current checks:
- answer is non-empty
- retrieved context exists
- answer includes citations like [Source 1]
- cited source IDs are valid

Reason:
- catches obvious generation failures
- validates citation behavior
- prepares for future LLM-as-judge evaluation
- creates answer-level observability before production deployment

Current limitation:
- does not judge factual faithfulness yet
- does not score completeness or correctness

## Decision 52: Add LLM-as-Judge Answer Evaluation

We added optional LLM-as-judge evaluation for generated answers.

Current judge metrics:
- faithfulness
- relevance
- completeness
- citation_quality

Reason:
- rule-based checks only validate structure
- LLM-as-judge helps detect hallucination and weak grounding
- creates answer-level quality metrics for RAG evaluation
- prepares for comparing prompts, models, and retrieval strategies

Current limitation:
- judge scores are model-dependent
- judge output should be reviewed periodically by humans

## Decision 53: Add Expected Topic Coverage Evaluation

We added expected-topic coverage scoring for batch answer evaluation.

Metric:
- topic_coverage = matched_expected_topics / total_expected_topics

Reason:
- Gives a simple answer completeness signal
- Uses the expected_topics already defined in eval datasets
- Helps compare prompt, retrieval, and model changes
- Complements LLM-as-judge scoring

Current limitation:
- Matching is keyword-based
- Synonyms and paraphrases may be missed
- Later this can be upgraded with semantic matching or LLM-based topic coverage

## Decision 54: Add Answer Guardrails

We added production-style answer guardrails.

Current checks:
- block answer generation when no context is retrieved
- block confident answer when retrieval confidence is too low
- validate that generated answers include citations
- add medical disclaimer for health-advice-style questions

Reason:
- reduces hallucination risk
- prevents unsupported answers
- improves scientific answer safety
- prepares for Reddit/community-source separation and medical-advice handling

Current limitation:
- retrieval confidence threshold is heuristic
- medical question detection is regex-based
- later guardrails should include stronger policy and source-aware safety checks

## Decision 55: Cache Model and Service Providers

We added cached provider dependencies using `lru_cache`.

Cached providers:
- SentenceTransformerEmbeddingProvider
- QdrantVectorStore
- GroqGenerationProvider
- CrossEncoderReranker

Reason:
- avoids reloading models on every request
- reduces request latency
- makes local API behavior closer to production dependency injection
- prepares for cleaner scaling and deployment

Current limitation:
- cache is per-process
- multi-worker deployment will load one copy per worker

## Decision 56: Cache BM25 Indexes by Chunk File and Filters

We added BM25 index caching.

Cache key:
- chunks_path
- document_id
- source_type
- trust_level
- section
- include_references

Reason:
- avoids rebuilding BM25 index on every request
- improves repeated query latency for the same document
- makes hybrid retrieval and answer generation faster
- supports document-specific search workflows

Current limitation:
- cache is in-memory and per-process
- changing a chunk file without restarting may require cache clearing

## Decision 57: Add API Latency Logging Middleware

We added middleware to log request latency for every API endpoint.

Logged fields:
- timestamp
- HTTP method
- path
- status code
- duration_ms

Reason:
- measures real API performance
- helps identify slow endpoints
- validates impact of provider and BM25 caching
- supports future latency optimization and deployment benchmarking

Current output:
outputs/observability/api_latency_logs.jsonl

## Decision 58: Add Latency Summary Reporting

We added a latency summary script that aggregates API latency logs.

Reported metrics:
- count
- average latency
- min latency
- max latency
- p50 latency
- p95 latency

Reason:
- gives measurable performance benchmarks
- helps quantify caching improvements
- supports deployment readiness checks
- creates resume-ready system performance metrics

Current script:
apps/api/run_latency_report.py

## Decision 59: Add Deployment Health Checks

We added a `/health` endpoint for production readiness.

Checks:
- Qdrant connectivity
- GROBID connectivity
- Groq LLM configuration

Reason:
- helps debug Docker and deployment issues
- makes the API easier to monitor
- separates simple API health from dependency health
- prepares for cloud deployment readiness checks

Current endpoint:
GET /health

## Decision 60: Add Deployment Documentation

We added local deployment instructions for the Docker-based ProteinScope stack.

Documented:
- environment variables
- Docker Compose startup
- API docs
- health checks
- ingestion
- retrieval endpoints
- answer endpoint
- evaluation commands
- observability outputs

Reason:
- makes the project easier to run
- improves recruiter/interviewer demo readiness
- documents deployment assumptions
- prepares for cloud deployment later
