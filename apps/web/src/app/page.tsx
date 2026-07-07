"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
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

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

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

export default function Home() {
  const [apiHealth, setApiHealth] = useState<string>("checking");
  const [file, setFile] = useState<File | null>(null);
  const [chunksPath, setChunksPath] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [ingestion, setIngestion] = useState<IngestionResponse | null>(null);
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [uploadError, setUploadError] = useState("");
  const [answerError, setAnswerError] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [answerLoading, setAnswerLoading] = useState(false);

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await readJsonResponse<HealthResponse>(response);
        setApiHealth(data.status || "unknown");
      } catch {
        setApiHealth("offline");
      }
    }

    checkHealth();
  }, []);

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

      if (data.chunks_path) {
        setChunksPath(data.chunks_path);
      }

      const parsedDocumentId = data.document?.metadata?.document_id;
      if (parsedDocumentId) {
        setDocumentId(parsedDocumentId);
      }
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
