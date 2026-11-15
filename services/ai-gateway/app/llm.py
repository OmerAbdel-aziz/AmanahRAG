"""Answer generation.

With ``LITELLM_MODEL`` set this calls the configured provider. Without it, an extractive
stub returns the opening of the best-matching passage so the full request path — middleware,
retrieval, citations, rehydration — stays testable offline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import Settings, get_settings
from app.retrieval import RetrievedChunk

logger = logging.getLogger(__name__)

SYSTEM_PROMPTS = {
    "en": (
        "You answer only from the numbered context passages. Cite every claim with [n]. "
        "If the passages do not contain the answer, say you do not know and stop. "
        "Reply in English. Do not invent document names or numbers."
    ),
    "ar": (
        "أجب فقط من المقاطع المرقّمة المرفقة. أضف رقم المقطع [n] بعد كل معلومة. "
        "إذا لم تجد الإجابة في المقاطع فقل إنك لا تعرف وتوقف. "
        "اكتب الإجابة بالعربية. لا تختلق أسماء مستندات أو أرقامًا."
    ),
}


@dataclass(slots=True)
class Answer:
    text: str
    model: str


class Answerer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: str
    ) -> Answer:
        if not self.settings.litellm_model:
            return self._stub(question, chunks, language)

        import litellm

        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])},
            {
                "role": "user",
                "content": self._user_prompt(question, chunks, language),
            },
        ]
        response = await litellm.acompletion(
            model=self.settings.litellm_model,
            messages=messages,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            timeout=self.settings.request_timeout_seconds,
        )
        return Answer(
            text=(response.choices[0].message.content or "").strip(),
            model=self.settings.litellm_model,
        )

    def _user_prompt(self, question: str, chunks: list[RetrievedChunk], language: str) -> str:
        if not chunks:
            context = "(no passages retrieved)"
        else:
            context = "\n\n".join(
                f"[{index}] {chunk.title}\n{chunk.text}"
                for index, chunk in enumerate(chunks, start=1)
            )
        heading = "Question" if language == "en" else "السؤال"
        passages = "Passages" if language == "en" else "المقاطع"
        return f"{passages}:\n{context}\n\n{heading}: {question}"

    def _stub(
        self, question: str, chunks: list[RetrievedChunk], language: str
    ) -> Answer:
        if not chunks:
            text = (
                "No indexed passages matched this question. Ingest the corpus, then try again."
                if language == "en"
                else "لم يتم العثور على مقاطع مفهرسة لهذا السؤال. أضف المستندات ثم حاول مجددًا."
            )
            return Answer(text=text, model="stub:no-context")

        top = chunks[0]
        excerpt = " ".join(top.text.split())[:420]
        if language == "en":
            text = f"{excerpt} [{1}]\n\n(stub answer: set LITELLM_MODEL for generated prose)"
        else:
            text = f"{excerpt} [{1}]\n\n(إجابة تجريبية: اضبط LITELLM_MODEL لتوليد نص فعلي)"
        return Answer(text=text, model="stub:extractive")
