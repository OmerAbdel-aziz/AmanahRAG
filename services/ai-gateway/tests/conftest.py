"""Test environment defaults. Set before app modules read Settings."""

import os

os.environ.setdefault("MILVUS_ENABLED", "false")
os.environ.setdefault("LITELLM_MODEL", "")
os.environ.setdefault("PII_REDACTION_ENABLED", "true")
