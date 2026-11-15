from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from app.graph import build_graph
from app.llm import Answer
from app.main import app
from app.retrieval import RetrievedChunk


class FakeRetriever:
    def __init__(self) -> None:
        self.queries: list[str] = []

    async def retrieve(self, query: str, language: str, top_k: int):
        self.queries.append(query)
        return [
            RetrievedChunk(
                document_id="doc-1",
                chunk_id="chunk-1",
                title="Retention policy",
                text="Uploaded documents are kept for 24 months, then purged.",
                score=0.91,
                language=language,
            )
        ][:top_k]


class EchoAnswerer:
    async def answer(self, question: str, chunks, language: str) -> Answer:
        return Answer(text=f"echo: {question}", model="test:echo")


def test_healthz() -> None:
    client = TestClient(app)
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["service"] == "amanah-ai-gateway"


def test_chat_redacts_pii_before_retrieval_and_rehydrates_answer() -> None:
    retriever = FakeRetriever()
    graph = build_graph(retriever, EchoAnswerer())

    state = {
        "question": "Email sara@example.org about retention",
        "language": "en",
        "top_k": 3,
        "pii_mapping": {"[EMAIL_1]": "sara@example.org"},
    }
    result = asyncio.run(graph.ainvoke(state))

    assert retriever.queries == ["Email [EMAIL_1] about retention"]
    assert result["answer"] == "echo: Email sara@example.org about retention"
    assert len(result["chunks"]) == 1


def test_chat_endpoint_returns_citations_and_redaction_count() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/chat",
        json={"question": "Reach me at a@b.co about the retention policy", "language": "en"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "en"
    assert body["pii_redactions"] >= 1
    assert body["trace_id"]
    assert "a@b.co" not in body["answer"]
