"""PII detection and redaction.

This is deliberately regex-first: it is predictable, cheap, and auditable. Names and
addresses need NER (Presidio + a spaCy Arabic model) and are a documented follow-up in
docs/adr/0003-*. The important property here is that model calls only ever see tokens.

The scrubber is stateless per call: ``scrub`` returns a mapping of token -> original value,
which is kept in process memory for the lifetime of one request and never logged.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

TokenMap = dict[str, str]

# Order matters: card numbers before phone numbers, IBAN before phone.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+", re.IGNORECASE)),
    (
        "IBAN",
        re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}[ ]?[A-Z0-9]{1,4}\b"),
    ),
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("PHONE", re.compile(r"(?<![\w])(?:\+|00)?\d[\d\s().-]{7,17}\d(?![\w])")),
    ("NATIONAL_ID", re.compile(r"\b\d{10,14}\b")),
]

@dataclass
class Scrubbed:
    text: str
    mapping: TokenMap = field(default_factory=dict)


class PIIScrubber:
    """Replaces sensitive values with stable, request-scoped tokens."""

    def __init__(self, patterns: list[tuple[str, re.Pattern[str]]] | None = None) -> None:
        self.patterns = patterns or PATTERNS

    def scrub(self, text: str) -> Scrubbed:
        mapping: TokenMap = {}
        counters: dict[str, int] = {}
        scrubbed = text

        for label, pattern in self.patterns:
            def _replace(match: re.Match[str], label: str = label) -> str:
                value = match.group(0)
                # Ignore short digit runs and things that are clearly not identifiers.
                digits = re.sub(r"\D", "", value)
                if label in {"CARD", "NATIONAL_ID"} and len(digits) < 10:
                    return value
                if label == "PHONE" and len(digits) < 9:
                    return value
                for token, original in mapping.items():
                    if original == value:
                        return token
                counters[label] = counters.get(label, 0) + 1
                token = f"[{label}_{counters[label]}]"
                mapping[token] = value
                return token

            scrubbed = pattern.sub(_replace, scrubbed)

        return Scrubbed(text=scrubbed, mapping=mapping)

    def scrub_payload(self, payload: Any) -> tuple[Any, TokenMap]:
        """Walks a JSON-decoded payload and scrubs every string value."""

        mapping: TokenMap = {}

        def walk(value: Any) -> Any:
            if isinstance(value, str):
                result = self.scrub(value)
                mapping.update(result.mapping)
                return result.text
            if isinstance(value, list):
                return [walk(item) for item in value]
            if isinstance(value, dict):
                return {key: walk(item) for key, item in value.items()}
            return value

        return walk(payload), mapping

    @staticmethod
    def restore(text: str, mapping: TokenMap) -> str:
        """Replaces tokens with their originals. Never send this across a trust boundary."""

        restored = text
        # Longest tokens first avoids [EMAIL_1] matching inside [EMAIL_10].
        for token in sorted(mapping, key=len, reverse=True):
            restored = restored.replace(token, mapping[token])
        return restored
