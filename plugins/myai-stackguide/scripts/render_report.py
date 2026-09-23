"""Pure CP-10 HTML projection; CP-07 alone owns filesystem publication.

Checkpoint A supplies navigation and localization, not the B-D detail views.
Only small, explicit state fields enter this shell; no raw state JSON is embedded.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
from typing import Any


ASSETS = Path(__file__).resolve().parents[1] / "assets"
VIEWS = ("goal", "questions", "scan", "context", "options", "compare", "integration", "history")
UI_KEYS = frozenset(VIEWS) | {
    "navigation", "skip", "snapshot", "snapshot_note", "project", "revision", "saved_at",
    "status", "phase", "next", "codex", "no_js", "language", "missing", "pending_view",
    "shell", "questions_count", "answers_count", "question_limit", "source", "saved",
    "active", "finalized", "finalized_incomplete", "intake", "context_review", "matching", "report",
    "answer_question", "review_context", "proceed_with_assumptions", "resume_or_finalize",
    "clarification_required", "continue_codex",
}


def load_locales(assets: Path = ASSETS) -> dict[str, dict[str, str]]:
    """Reject incomplete dictionaries instead of silently shipping blank UI."""
    dictionaries = {}
    for locale in ("ru", "en"):
        values = json.loads((assets / "locales" / f"{locale}.json").read_text(encoding="utf-8"))
        if not isinstance(values, dict) or set(values) != UI_KEYS:
            raise ValueError("incomplete UI dictionary")
        if any(not isinstance(value, str) or not value.strip() for value in values.values()):
            raise ValueError("empty UI translation")
        dictionaries[locale] = values
    return dictionaries


def render_report(state: dict[str, Any]) -> bytes:
    """Render a validated snapshot without state writes, retrieval or translation."""
    try:
        dictionaries = load_locales()
        locale = (state.get("presentation") or {}).get("default_locale", "ru")
        if locale not in dictionaries:
            raise ValueError("invalid saved locale")
        labels = dictionaries[locale]

        def text(key: str) -> str:
            return f'<span data-i18n="{key}">{html.escape(labels[key])}</span>'

        navigation = "".join(
            f'<a href="#{view}" data-view="{view}"><span class="number">{index:02}</span>{text(view)}</a>'
            for index, view in enumerate(VIEWS, 1)
        )
        sources = {
            "goal": state.get("brief"), "questions": state["intake"], "scan": state.get("scan"),
            "context": state.get("brief"), "options": state.get("memo"), "compare": state.get("memo"),
            "integration": (state.get("memo") or {}).get("integration_plan"), "history": state.get("history"),
        }
        sections = []
        for index, view in enumerate(VIEWS, 1):
            availability = "saved" if sources[view] else "missing"
            details = ""
            if view == "questions":
                details = (
                    f'<dl><dt>{text("questions_count")}</dt><dd>{state["intake"]["questions_asked"]}</dd>'
                    f'<dt>{text("answers_count")}</dt><dd>{len(state["intake"]["answers"])}</dd></dl>'
                    f'<p>{text("question_limit")}</p>'
                )
            sections.append(
                f'<section id="{view}" aria-labelledby="heading-{view}" tabindex="-1">'
                f'<p class="eyebrow">{index:02} / 08</p><h1 id="heading-{view}">{text(view)}</h1>'
                f'<p class="availability">{text("source")}: {text(availability)}</p>'
                f'{details}<p class="notice">{text("pending_view")}</p></section>'
            )
        action = state["intake"].get("next_action", "clarification_required")
        if state["status"] != "active" or state.get("memo") or action not in UI_KEYS:
            action = "continue_codex"
        # The template is trusted code. Substitute once so inserted data cannot
        # introduce a second template instruction or an executable script tag.
        payload = json.dumps(dictionaries, ensure_ascii=False).replace("<", "\\u003c").replace(
            ">", "\\u003e"
        ).replace("&", "\\u0026")
        replacements = {
            "locale": locale, "navigation_items": navigation, "sections": "".join(sections),
            "dictionaries": payload, "revision_value": str(state["revision"]),
            "saved_value": html.escape(state["updated_at"]),
            "status_value": text(state["status"]), "phase_value": text(state["phase"]),
            "next_value": text(action),
            "navigation_label": html.escape(labels["navigation"], quote=True),
        }
        template = (ASSETS / "status-template.html").read_text(encoding="utf-8")
        result = re.sub(r"\{\{([a-z_]+)\}\}", lambda match: (
            replacements[match[1]] if match[1] in replacements else text(match[1])
        ), template)
        data = result.encode("utf-8")
        return data
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError("render_failed") from error
