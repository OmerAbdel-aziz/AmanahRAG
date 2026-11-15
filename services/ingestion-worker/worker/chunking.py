"""Language-aware chunking.

Word-based windows with overlap, snapped to sentence boundaries where possible. Arabic text
is normalised (tatweel, diacritics, alef variants) for *embedding* only; the stored chunk
keeps the author's original characters so citations read naturally.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TATWEEL = "\u0640"
DIACRITICS = re.compile(r"[\u064B-\u0652\u0670]")
ALEF_VARIANTS = re.compile(r"[إأآ]")

SENTENCE_END = re.compile(r"(?<=[.!?؟])\s+")


@dataclass(slots=True)
class Chunk:
    ordinal: int
    text: str
    token_count: int


def normalize_for_embedding(text: str) -> str:
    text = text.replace(TATWEEL, "")
    text = DIACRITICS.sub("", text)
    text = ALEF_VARIANTS.sub("ا", text)
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, max_words: int = 220, overlap_words: int = 40) -> list[Chunk]:
    words = text.split()
    if not words:
        return []
    if overlap_words >= max_words:
        raise ValueError("overlap_words must be smaller than max_words")

    chunks: list[Chunk] = []
    start = 0
    ordinal = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        window = " ".join(words[start:end])

        # Prefer ending on a sentence boundary in the last third of the window.
        if end < len(words):
            sentences = SENTENCE_END.split(window)
            if len(sentences) > 1:
                candidate = " ".join(sentences[:-1])
                if len(candidate.split()) >= max_words // 2:
                    window = candidate
                    end = start + len(window.split())

        chunks.append(Chunk(ordinal=ordinal, text=window, token_count=len(window.split())))
        ordinal += 1
        if end >= len(words):
            break
        start = max(end - overlap_words, start + 1)

    return chunks
