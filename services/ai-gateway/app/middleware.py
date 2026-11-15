"""Request-level PII boundary.

The middleware rewrites JSON request bodies before they reach a route handler, so no
downstream code (graph node, retriever, prompt builder, LLM client) can accidentally see raw
PII. The token map is stored on the ASGI scope's ``state`` (what ``request.state`` reads) and
only the response rehydration step uses it.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.datastructures import Headers, MutableHeaders

from app.pii import PIIScrubber

logger = logging.getLogger(__name__)

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

SCRUBBED_METHODS = {"POST", "PUT", "PATCH"}


class PIIMiddleware:
    """Pure ASGI middleware; BaseHTTPMiddleware cannot safely replace a request body."""

    def __init__(self, app, scrubber: PIIScrubber | None = None, enabled: bool = True) -> None:
        self.app = app
        self.scrubber = scrubber or PIIScrubber()
        self.enabled = enabled

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.enabled or scope["type"] != "http" or not self._should_scrub(scope):
            await self.app(scope, receive, send)
            return

        body = await self._read_body(receive)
        if body is None:
            await self.app(scope, receive, send)
            return

        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            await self.app(scope, self._replay(body), send)
            return

        scrubbed, mapping = self.scrubber.scrub_payload(payload)
        if not mapping:
            await self.app(scope, self._replay(body), send)
            return

        new_body = json.dumps(scrubbed).encode("utf-8")
        state = scope.setdefault("state", {})
        state["pii_mapping"] = mapping
        state["pii_redactions"] = len(mapping)

        headers = MutableHeaders(scope=scope)
        headers["content-length"] = str(len(new_body))

        logger.info("redacted %d PII value(s) from %s", len(mapping), scope.get("path", ""))
        await self.app(scope, self._replay(new_body), send)

    @staticmethod
    async def _read_body(receive: Receive) -> bytes | None:
        chunks: list[bytes] = []
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return None
            chunks.append(message.get("body", b""))
            if not message.get("more_body", False):
                return b"".join(chunks)

    @staticmethod
    def _replay(body: bytes) -> Receive:
        sent = False

        async def replay() -> Message:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        return replay

    @staticmethod
    def _should_scrub(scope: Scope) -> bool:
        if scope.get("method") not in SCRUBBED_METHODS:
            return False
        content_type = Headers(scope=scope).get("content-type", "")
        return content_type.startswith("application/json")
