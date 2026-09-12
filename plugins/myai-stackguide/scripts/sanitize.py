"""Deterministic CP-07 sanitizer for the three named synthetic canaries only."""

from __future__ import annotations

import re


LITERAL = "STACKGUIDE_TEST_SECRET_7f4c2a90"
ASSIGNMENT = "STACKGUIDE_TEST_TOKEN=" + LITERAL
BLOCK_BEGIN = "-----BEGIN STACKGUIDE TEST SECRET-----"
BLOCK_END = "-----END STACKGUIDE TEST SECRET-----"
REPLACEMENT = "[REDACTED]"

_PATTERN = re.compile(
    "|".join(
        (
            re.escape(BLOCK_BEGIN) + r"[\s\S]*?" + re.escape(BLOCK_END),
            re.escape(ASSIGNMENT),
            re.escape(LITERAL),
        )
    )
)
_ADJACENT = re.compile(re.escape(REPLACEMENT) + r"(?:\s+" + re.escape(REPLACEMENT) + r")+")


class SanitizationError(ValueError):
    """A bounded input cannot be represented without violating the contract."""

    def __init__(self, message_key: str | None = None) -> None:
        super().__init__("invalid sanitized input")
        self.message_key = message_key


def sanitize_text(value: str, *, max_code_points: int = 2000) -> tuple[str, bool]:
    """Return normalized sanitized text and whether a named replacement occurred."""

    if not isinstance(value, str):
        raise SanitizationError()
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    sanitized, replacements = _PATTERN.subn(REPLACEMENT, normalized)
    if replacements:
        sanitized = _ADJACENT.sub(REPLACEMENT, sanitized)
    sanitized = sanitized.strip()
    if len(sanitized) > max_code_points:
        raise SanitizationError()
    if not sanitized or sanitized == REPLACEMENT:
        raise SanitizationError("answer_fully_redacted")
    return sanitized, bool(replacements)


def contains_named_canary(value: bytes | str) -> bool:
    """Check the exact named raw canaries before any persisted/output write."""

    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return False
    return any(token in value for token in (ASSIGNMENT, LITERAL, BLOCK_BEGIN, BLOCK_END))
