"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
};

type DocumentRecord = {
  document_id: string;
  title?: string | null;
  filename?: string | null;
  chunks_path: string;
  chunk_count: number;
  embedding_count: number;
  indexed_count: number;
  parser_name?: string | null;
  created_at: string;
};

type DocumentsResponse = {
  documents: DocumentRecord[];
};

type IngestionResponse = {
  status: string;
  message: string;
  error?: string;
  chunks_path?: string;
  chunk_count?: number;
  embedding_count?: number;
  indexed_count?: number;
  document?: {
    metadata?: {
      document_id?: string;
      title?: string;
      parser_name?: string;
    };
  };
};

type Citation = {
  citation_id: number;
  section: string | null;
  start_page: number;
  end_page: number;
  text_preview: string;
};

type AnswerResponse = {
  question: string;
  answer: string;
  generator_model: string;
  retrieval_strategy: string;
  citations: Citation[];
};

type SavedDocument = {
  documentId: string;
  chunksPath: string;
  title?: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const SAVED_DOCUMENT_KEY = "proteinscope_latest_document";

async function readJsonResponse<T>(response: Response): Promise<T> {
  const data = await response.json();

  if (!response.ok) {
    const message =
      typeof data?.detail === "string"
        ? data.detail
        : typeof data?.message === "string"
          ? data.message
          : typeof data?.error === "string"
            ? data.error
            : `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data as T;
}

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export default function Home() {
  const [apiHealth, setApiHealth] = useState<string>("checking");
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  const [file, setFile] = useState<File | null>(null);
  const [chunksPath, setChunksPath] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [documentTitle, setDocumentTitle] = useState("");

  const [question, setQuestion] = useState("");
  const [ingestion, setIngestion] = useState<IngestionResponse | null>(null);
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);

  const [uploadError, setUploadError] = useState("");
  const [answerError, setAnswerError] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [answerLoading, setAnswerLoading] = useState(false);

  useEffect(() => {
    checkHealth();
    loadSavedDocument();
    fetchDocuments();
  }, []);

  async function checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await readJsonResponse<HealthResponse>(response);
      setApiHealth(data.status || "unknown");
    } catch {
      setApiHealth("offline");
    }
  }

  function loadSavedDocument() {
    const savedDocumentRaw = window.localStorage.getItem(SAVED_DOCUMENT_KEY);

    if (savedDocumentRaw) {
      try {
        const savedDocument = JSON.parse(savedDocumentRaw) as SavedDocument;

        if (savedDocument.documentId && savedDocument.chunksPath) {
          setDocumentId(savedDocument.documentId);
          setChunksPath(savedDocument.chunksPath);
          setDocumentTitle(savedDocument.title || "");
        }
      } catch {
        window.localStorage.removeItem(SAVED_DOCUMENT_KEY);
      }
    }
  }

  async function fetchDocuments() {
    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const response = await fetch(`${API_BASE_URL}/documents`);
      const data = await readJsonResponse<DocumentsResponse>(response);

      const sortedDocuments = [...data.documents].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      );

      setDocuments(sortedDocuments);
    } catch (caughtError) {
      setDocumentsError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not load documents",
      );
    } finally {
      setDocumentsLoading(false);
    }
  }

  function saveLatestDocument(document: SavedDocument) {
    window.localStorage.setItem(SAVED_DOCUMENT_KEY, JSON.stringify(document));
  }

  function selectDocument(record: DocumentRecord) {
    const title = record.title || record.filename || record.document_id;

    setDocumentId(record.document_id);
    setChunksPath(record.chunks_path);
    setDocumentTitle(title);
    setAnswer(null);
    setAnswerError("");

    saveLatestDocument({
      documentId: record.document_id,
      chunksPath: record.chunks_path,
      title,
    });
  }

  function clearLatestDocument() {
    window.localStorage.removeItem(SAVED_DOCUMENT_KEY);
    setChunksPath("");
    setDocumentId("");
    setDocumentTitle("");
    setIngestion(null);
    setAnswer(null);
    setUploadError("");
    setAnswerError("");
  }

  async function uploadPdf() {
    if (!file) return;

    setUploadLoading(true);
    setUploadError("");
    setAnswerError("");
    setAnswer(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE_URL}/ingest/pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await readJsonResponse<IngestionResponse>(response);

      if (data.status === "failed") {
        throw new Error(data.error || data.message || "PDF ingestion failed.");
      }

      setIngestion(data);

      const parsedChunksPath = data.chunks_path || "";
      const parsedDocumentId = data.document?.metadata?.document_id || "";
      const parsedTitle = data.document?.metadata?.title || file.name;

      if (parsedChunksPath) {
        setChunksPath(parsedChunksPath);
      }

      if (parsedDocumentId) {
        setDocumentId(parsedDocumentId);
      }

      setDocumentTitle(parsedTitle);

      if (parsedChunksPath && parsedDocumentId) {
        saveLatestDocument({
          documentId: parsedDocumentId,
          chunksPath: parsedChunksPath,
          title: parsedTitle,
        });
      }

      await fetchDocuments();
    } catch (caughtError) {
      setUploadError(
        caughtError instanceof Error
          ? caughtError.message
          : "PDF upload failed",
      );
    } finally {
      setUploadLoading(false);
    }
  }

  async function askQuestion() {
    if (!question || !chunksPath) return;

    setAnswerLoading(true);
    setAnswerError("");

    try {
      const response = await fetch(`${API_BASE_URL}/answer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          chunks_path: chunksPath,
          document_id: documentId || null,
          top_k: 5,
          dense_k: 30,
          bm25_k: 30,
          source_type: "scientific_paper",
          trust_level: "verified",
        }),
      });

      const data = await readJsonResponse<AnswerResponse>(response);
      setAnswer(data);
    } catch (caughtError) {
      setAnswerError(
        caughtError instanceof Error
          ? caughtError.message
          : "Question request failed",
      );
    } finally {
      setAnswerLoading(false);
    }
  }

  const healthColor =
    apiHealth === "ok"
      ? "bg-emerald-500"
      : apiHealth === "warning" || apiHealth === "checking"
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-8 text-zinc-100">
      <div className="mx-auto max-w-5xl space-y-8">
        <section>
          <div className="flex flex-wrap items-center gap-3">
            <p className="text-sm text-zinc-400">ProteinScope v2</p>
            <span className="flex items-center gap-2 rounded-full border border-zinc-800 px-3 py-1 text-xs text-zinc-400">
              <span className={`h-2 w-2 rounded-full ${healthColor}`} />
              API {apiHealth}
            </span>
          </div>

          <h1 className="mt-2 text-4xl font-bold tracking-tight">
            Scientific RAG Assistant
          </h1>
          <p className="mt-3 max-w-2xl text-zinc-400">
            Upload a research paper, index it with GROBID + Qdrant, and ask
            grounded questions with citations.
          </p>
        </section>

        {chunksPath && documentId && (
          <section className="rounded-2xl border border-emerald-900 bg-emerald-950/20 p-4 text-sm text-emerald-100">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-semibold">Active document loaded</p>
                <p className="mt-1 text-emerald-200/80">
                  {documentTitle || documentId}
                </p>
                <p className="mt-1 break-all text-xs text-emerald-200/60">
                  {chunksPath}
                </p>
              </div>

              <button
                onClick={clearLatestDocument}
                className="rounded-lg border border-emerald-800 px-4 py-2 text-xs font-medium text-emerald-100 hover:bg-emerald-900/40"
              >
                Clear
              </button>
            </div>
          </section>
        )}

        <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-xl font-semibold">0. Indexed Documents</h2>

            <button
              onClick={fetchDocuments}
              disabled={documentsLoading}
              className="rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-800 disabled:opacity-50"
            >
              {documentsLoading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {documentsError && (
            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/50 p-4 text-sm text-red-200">
              {documentsError}
            </div>
          )}

          {documents.length === 0 && !documentsLoading ? (
            <p className="mt-4 text-sm text-zinc-400">
              No indexed documents yet. Upload a PDF below to create one.
            </p>
          ) : (
            <div className="mt-4 space-y-3">
              {documents.map((record) => {
                const isActive = record.document_id === documentId;

                return (
                  <button
                    key={record.document_id}
                    onClick={() => selectDocument(record)}
                    className={`w-full rounded-xl border p-4 text-left text-sm transition ${
                      isActive
                        ? "border-emerald-700 bg-emerald-950/30"
                        : "border-zinc-800 bg-zinc-950 hover:border-zinc-700"
                    }`}
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-semibold text-zinc-100">
                          {record.title || record.filename || record.document_id}
                        </p>
                        <p className="mt-1 text-xs text-zinc-500">
                          {record.document_id}
                        </p>
                      </div>

                      <p className="text-xs text-zinc-500">
                        {formatDate(record.created_at)}
                      </p>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-zinc-400">
                      <span className="rounded-full bg-zinc-900 px-2 py-1">
                        chunks: {record.chunk_count}
                      </span>
                      <span className="rounded-full bg-zinc-900 px-2 py-1">
                        indexed: {record.indexed_count}
                      </span>
                      <span className="rounded-full bg-zinc-900 px-2 py-1">
                        parser: {record.parser_name || "unknown"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="text-xl font-semibold">1. Upload PDF</h2>

          <div className="mt-4 flex flex-col gap-4 sm:flex-row">
            <input
              type="file"
              accept="application/pdf"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 p-3 text-sm"
            />

            <button
              onClick={uploadPdf}
              disabled={!file || uploadLoading}
              className="rounded-lg bg-white px-5 py-3 font-medium text-zinc-950 disabled:opacity-50"
            >
              {uploadLoading ? "Processing..." : "Ingest PDF"}
            </button>
          </div>

          {uploadError && (
            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/50 p-4 text-sm text-red-200">
              {uploadError}
            </div>
          )}

          {ingestion && (
            <div className="mt-5 rounded-xl bg-zinc-950 p-4 text-sm text-zinc-300">
              <p>
                <span className="font-semibold text-zinc-100">Status:</span>{" "}
                {ingestion.status}
              </p>
              <p>
                <span className="font-semibold text-zinc-100">Message:</span>{" "}
                {ingestion.message}
              </p>
              <p>
                <span className="font-semibold text-zinc-100">Document ID:</span>{" "}
                {documentId || "N/A"}
              </p>
              <p>
                <span className="font-semibold text-zinc-100">Title:</span>{" "}
                {documentTitle || "N/A"}
              </p>
              <p>
                <span className="font-semibold text-zinc-100">Chunks:</span>{" "}
                {ingestion.chunk_count ?? "N/A"}
              </p>
              <p>
                <span className="font-semibold text-zinc-100">Indexed:</span>{" "}
                {ingestion.indexed_count ?? "N/A"}
              </p>
              <p className="break-all">
                <span className="font-semibold text-zinc-100">Chunks path:</span>{" "}
                {chunksPath || "N/A"}
              </p>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="text-xl font-semibold">2. Ask Question</h2>

          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: How does heat treatment affect whey proteins?"
            className="mt-4 min-h-28 w-full rounded-lg border border-zinc-700 bg-zinc-950 p-3 text-sm"
          />

          <button
            onClick={askQuestion}
            disabled={!question || !chunksPath || answerLoading}
            className="mt-4 rounded-lg bg-white px-5 py-3 font-medium text-zinc-950 disabled:opacity-50"
          >
            {answerLoading ? "Thinking..." : "Ask"}
          </button>

          {answerError && (
            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/50 p-4 text-sm text-red-200">
              {answerError}
            </div>
          )}

          {answer && (
            <div className="mt-6 space-y-5">
              <div className="rounded-xl bg-zinc-950 p-5">
                <p className="text-sm text-zinc-500">
                  Model: {answer.generator_model}
                </p>
                <p className="text-sm text-zinc-500">
                  Retrieval: {answer.retrieval_strategy}
                </p>
                <p className="mt-4 whitespace-pre-wrap leading-7">
                  {answer.answer}
                </p>
              </div>

              <div>
                <h3 className="font-semibold">Citations</h3>

                <div className="mt-3 space-y-3">
                  {answer.citations.map((citation) => (
                    <div
                      key={citation.citation_id}
                      className="rounded-xl border border-zinc-800 bg-zinc-950 p-4 text-sm"
                    >
                      <p className="font-semibold">
                        Source {citation.citation_id} ·{" "}
                        {citation.section || "unknown"} · pages{" "}
                        {citation.start_page === citation.end_page
                          ? citation.start_page
                          : `${citation.start_page}-${citation.end_page}`}
                      </p>
                      <p className="mt-2 text-zinc-400">
                        {citation.text_preview}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
