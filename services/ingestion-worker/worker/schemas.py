from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DocumentRef(BaseModel):
    id: str
    title: str
    language: Literal["ar", "en"]
    text: str = Field(min_length=1)
    source_uri: str | None = None
    checksum: str | None = None


class DocumentUploadedV1(BaseModel):
    """Mirror of packages/contracts/events/document.uploaded.v1.schema.json."""

    event_id: str
    event_type: Literal["document.uploaded.v1"] = "document.uploaded.v1"
    occurred_at: datetime
    document: DocumentRef
