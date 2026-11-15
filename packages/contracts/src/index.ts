/**
 * Hand-maintained mirror of the OpenAPI and event schemas in this package.
 * Regenerating from OpenAPI is a follow-up; until then these types are reviewed alongside
 * the YAML in the same pull request.
 */

export type Language = "ar" | "en";

export interface Citation {
  document_id: string;
  chunk_id: string;
  title: string;
  snippet: string;
  score: number;
}

export interface ChatRequest {
  question: string;
  language?: Language;
  top_k?: number;
}

export interface ChatResponse {
  trace_id: string;
  answer: string;
  language: Language;
  model: string;
  latency_ms: number;
  citations: Citation[];
  pii_redactions?: number;
}

export interface DocumentUploadedV1 {
  event_id: string;
  event_type: "document.uploaded.v1";
  occurred_at: string;
  document: {
    id: string;
    title: string;
    language: Language;
    text: string;
    source_uri?: string | null;
    checksum?: string | null;
  };
}

export interface DocumentIndexedV1 {
  event_id: string;
  event_type: "document.indexed.v1";
  occurred_at: string;
  document_id: string;
  chunks: number;
  vectors: number;
  model?: string;
}

export type AmanahEvent = DocumentUploadedV1 | DocumentIndexedV1;

export const EVENT_NAMES = ["document.uploaded.v1", "document.indexed.v1"] as const;
export type EventName = (typeof EVENT_NAMES)[number];
