from worker.config import Settings
from worker.embeddings import HashEmbedder
from worker.pipeline import process_document
from worker.schemas import DocumentRef


class FakeStore:
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.deleted: list[str] = []

    def upsert(self, rows: list[dict], *, document_id: str, replace_document: bool = True) -> int:
        if replace_document:
            self.deleted.append(document_id)
        self.rows = rows
        return len(rows)


def test_pipeline_chunks_embeds_and_upserts() -> None:
    settings = Settings(chunk_words=50, chunk_overlap_words=10, embedding_dim=64)
    store = FakeStore()
    embedder = HashEmbedder(64)
    document = DocumentRef(
        id="doc-1",
        title="Retention policy",
        language="en",
        text=" ".join(["policy"] * 140),
    )

    result = process_document(document, store, embedder, settings)

    assert result.document_id == "doc-1"
    assert result.chunks > 1
    assert result.vectors == result.chunks
    assert store.deleted == ["doc-1"]
    assert len(store.rows) == result.chunks
    assert all(len(row["embedding"]) == 64 for row in store.rows)
    assert {row["language"] for row in store.rows} == {"en"}
    assert len({row["pk"] for row in store.rows}) == len(store.rows)


def test_pipeline_rejects_empty_document() -> None:
    settings = Settings()
    document = DocumentRef(id="doc-2", title="Empty", language="ar", text="   ")

    result = process_document(document, FakeStore(), HashEmbedder(settings.embedding_dim), settings)

    assert result.chunks == 0
