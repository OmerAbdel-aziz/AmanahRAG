"""LangGraph pipeline: retrieve -> generate -> restore.

The PII scrub happens in middleware, before this graph runs. The graph only receives the
token map so it can rehydrate the final answer for the original caller.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.config import get_settings
from app.llm import Answerer
from app.pii import PIIScrubber
from app.retrieval import Retriever, RetrievedChunk, get_retriever

logger = logging.getLogger(__name__)


class ChatState(TypedDict, total=False):
    question: str
    language: str
    top_k: int
    chunks: list[RetrievedChunk]
    answer: str
    model: str
    pii_mapping: dict[str, str]


def build_graph(retriever: Retriever, answerer: Answerer):
    settings = get_settings()

    async def retrieve(state: ChatState) -> ChatState:
        chunks = await retriever.retrieve(
            state["question"], state["language"], state.get("top_k", settings.top_k)
        )
        return {"chunks": chunks}

    async def generate(state: ChatState) -> ChatState:
        result = await answerer.answer(
            state["question"], state.get("chunks", []), state["language"]
        )
        return {"answer": result.text, "model": result.model}

    async def restore(state: ChatState) -> ChatState:
        mapping = state.get("pii_mapping") or {}
        if not mapping or not settings.pii_restore_response:
            return {}
        return {"answer": PIIScrubber.restore(state["answer"], mapping)}

    graph = StateGraph(ChatState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_node("restore", restore)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "restore")
    graph.add_edge("restore", END)
    return graph.compile()


@lru_cache
def get_graph():
    return build_graph(get_retriever(), Answerer())
