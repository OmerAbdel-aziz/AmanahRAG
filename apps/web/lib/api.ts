const GATEWAY_URL =
  process.env.NEXT_PUBLIC_GATEWAY_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export type Citation = {
  document_id: string;
  chunk_id: string;
  title: string;
  snippet: string;
  score: number;
};

export type ChatResponse = {
  trace_id: string;
  answer: string;
  language: "ar" | "en";
  model: string;
  latency_ms: number;
  citations: Citation[];
};

export async function askQuestion(
  question: string,
  language: "ar" | "en",
): Promise<ChatResponse> {
  const response = await fetch(`${GATEWAY_URL}/v1/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ question, language }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Gateway ${response.status}: ${detail.slice(0, 200)}`);
  }

  return (await response.json()) as ChatResponse;
}
