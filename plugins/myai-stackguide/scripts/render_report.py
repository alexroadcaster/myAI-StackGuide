"""Pure CP-10 HTML projection; CP-07 alone owns filesystem publication.

Checkpoint C projects seven source-bound views. No raw state JSON is embedded.
"""

from __future__ import annotations

import html
import hashlib
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
    "outcome", "decision", "project_stage", "problem", "target_user", "workflow",
    "current_behavior", "target_behavior", "success_criterion", "baseline", "constraints",
    "scope", "non_goals", "session_summary", "current_question", "rationale", "consequence",
    "examples", "examples_note", "saved_answers", "coverage", "completion", "correction_impact",
    "no_goal", "no_question", "no_answers", "no_scan", "no_brief", "unknown", "unavailable_translation",
    "source_language", "answer_status", "answer_revision", "recorded_at", "question_topics",
    "answered", "skipped", "pending", "unasked", "question_status", "assumptions",
    "scan_scope", "classification", "scan_status", "scan_mode", "reason_codes", "scan_budget",
    "files", "bytes", "seconds", "visited", "file_attempts", "coverage_limit", "topology",
    "findings", "facts", "inferences", "gaps", "evidence", "source_ledger", "exclusions",
    "boundary", "scan_boundary", "selection_request", "requested_not_read", "next_check",
    "system_outline", "capabilities", "evidence_ledger", "tensions", "readiness", "corrections",
    "brief_version", "context_status", "claim_kind", "limitation", "refs", "answer_refs",
    "observed", "inferred", "user_statement", "unknown_kind", "correction_warning",
    "not_measured", "saved_deliverables", "selection", "scan_fact_limit", "translation_partial",
    "languages", "deployment", "allowed_licenses", "compatibility", "mandatory_fields",
    "require_no_server", "constraint_notes", "observed_kind", "user_statement_kind", "inference_kind",
    "no_memo", "no_plan", "recommendation_summary", "category_path", "candidate_roles",
    "repository", "role", "eligibility", "fit", "caveats", "next_checks", "matched_fields",
    "integration_surface", "license", "created_at", "pushed_at", "last_commit_at",
    "last_release_at", "observed_at", "catalog_status", "retrieval_disclosure",
    "query", "retrieved_hits", "candidates_count", "cards_count", "pack_bytes",
    "truncated", "index_format", "snapshot_id", "avoid_defer", "revisit_when",
    "reading_path", "missing_context", "evidence_ceiling", "comparison_scope",
    "no_change", "decision_matrix", "selection_rationale", "counterargument",
    "reconsider_when", "next_decision", "draft_only", "no_comparison_details",
    "proposed_outcome", "execution_status", "selected_candidates", "proposed_diagram",
    "diagram_nodes", "diagram_edges", "proposed", "prerequisites", "steps",
    "depends_on", "safe_paths", "proposed_commands", "acceptance", "first_validation",
    "validation_input", "expected_behavior", "widen_when", "actual_not_run",
    "risks", "rollback", "coding_handoff", "handoff_instruction", "first_slice",
    "stop_conditions", "execution_authority", "permission_changes", "affected_components",
    "no_matrix_cell", "source_not_execution", "pack_status", "reason_codes",
    "blocked_candidate", "reference_candidate", "unassigned_card", "source_snapshot_date", "built_at",
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


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


class ViewContent:
    """Escape canonical fields and bind saved localized text to exact source bytes."""

    def __init__(self, state: dict[str, Any], locale: str, dictionaries: dict[str, dict[str, str]]):
        self.state, self.locale, self.dictionaries = state, locale, dictionaries
        presentation = state.get("presentation") or {}
        self.entries = {entry["field_pointer"]: entry for entry in presentation.get("fields", [])}
        self.source_locale = presentation.get("source_locale", "und")
        if presentation and presentation.get("source_content_revision") != state.get("content_revision", state["revision"]):
            raise ValueError("stale presentation revision")
        brief, memo = state.get("brief"), state.get("memo")
        identities = {
            "brief_id": (brief or {}).get("brief_id"), "brief_version": (brief or {}).get("brief_version"),
            "memo_id": (memo or {}).get("memo_id"),
            "plan_id": ((memo or {}).get("integration_plan") or {}).get("plan_id"),
        }
        if presentation and any(presentation.get(key) != value for key, value in identities.items()):
            raise ValueError("stale presentation identity")

    def t(self, key: str) -> str:
        return f'<span data-i18n="{key}">{_escape(self.dictionaries[self.locale][key])}</span>'

    def literal(self, value: Any) -> str:
        return _escape(value) if value is not None and value != "" else self.t("unknown")

    def narrative(self, pointer: str, value: Any, *, source_locale: str | None = None) -> str:
        if not isinstance(value, str) or not value:
            return self.t("unknown")
        entry = self.entries.get(pointer)
        if entry:
            digest = hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
            if (entry["source_sha256"] != digest or
                entry["source_content_revision"] != self.state.get("content_revision", self.state["revision"])):
                raise ValueError("stale narrative translation")
        original_lang = (entry or {}).get("source_locale") or source_locale or "und"
        values, langs, missing = {}, {}, {}
        for locale in ("ru", "en"):
            target = (entry or {}).get(locale) or {}
            available = target.get("status") == "available" and isinstance(target.get("text"), str)
            values[locale] = target["text"] if available else value
            langs[locale] = locale if available else original_lang
            missing[locale] = not available
        attrs = " ".join(
            f'data-{locale}="{_escape(values[locale])}" data-{locale}-lang="{_escape(langs[locale])}" '
            f'data-{locale}-missing="{str(missing[locale]).lower()}"' for locale in ("ru", "en")
        )
        current = self.locale
        notice = self.t("unavailable_translation")
        return (
            f'<span data-narrative {attrs} data-source-lang="{_escape(original_lang)}" '
            f'data-translation-missing="{str(missing[current]).lower()}" '
            f'lang="{_escape(langs[current])}">{_escape(values[current])}</span>'
            f'<span class="translation-note" data-missing-notice'
            f'{"" if missing[current] else " hidden"}> {notice}</span>'
        )

    def row(self, label: str, value: str) -> str:
        return f'<div class="field"><dt>{self.t(label)}</dt><dd>{value}</dd></div>'

    def group(self, title: str, body: str) -> str:
        return f'<div class="subsection"><h2>{self.t(title)}</h2>{body}</div>'

    def items(self, values: list[str], empty: str = "unknown") -> str:
        return '<ul class="item-list">' + ''.join(f'<li>{item}</li>' for item in values) + '</ul>' if values else self.t(empty)

    def claim(self, pointer: str, claim: dict[str, Any] | None) -> str:
        if not isinstance(claim, dict):
            return self.t("unknown")
        kind = claim.get("kind", "unknown")
        text = self.narrative(pointer + "/text", claim.get("text"))
        refs = [self.literal(ref) for ref in claim.get("evidence_refs", [])]
        answers = [self.literal(ref) for ref in claim.get("answer_ids", [])]
        meta = f'<span class="claim-kind">{self.t(kind + "_kind") if kind + "_kind" in UI_KEYS else self.literal(kind)}</span>'
        if refs:
            meta += f' · {self.t("refs")}: {", ".join(refs)}'
        if answers:
            meta += f' · {self.t("answer_refs")}: {", ".join(answers)}'
        limitation = claim.get("limitation")
        if limitation:
            meta += f'<p class="limitation">{self.t("limitation")}: {self.narrative(pointer + "/limitation", limitation)}</p>'
        return f'{text}<div class="source-meta">{meta}</div>'

    def constraint_rows(self, brief: dict[str, Any]) -> str:
        constraints = brief.get("constraints") or {}
        rows = []
        for key in ("languages", "deployment", "allowed_licenses", "compatibility", "mandatory_fields"):
            values = constraints.get(key) or []
            rows.append(self.row(key, self.items([self.literal(value) for value in values])))
        no_server = constraints.get("require_no_server")
        rows.append(self.row("require_no_server", self.literal(no_server) if no_server is not None else self.t("unknown")))
        for index, note in enumerate((brief.get("details") or {}).get("constraint_notes", [])):
            claim = note.get("claim") or {}
            ownership = " · ".join(self.literal(note.get(key)) for key in (
                "topic", "strength", "constraint_pointer") if note.get(key) is not None)
            rows.append(self.row("constraint_notes", ownership + " · " + self.claim(
                f"/brief/details/constraint_notes/{index}/claim", claim
            ) + (f'<p>{self.t("consequence")}: {self.narrative(f"/brief/details/constraint_notes/{index}/consequence", note.get("consequence"))}</p>')))
        return '<dl class="detail-list">' + ''.join(rows) + '</dl>'

    def observations(self, summary: dict[str, Any], prefix: str) -> str:
        facts = []
        for index, fact in enumerate(summary.get("facts", [])):
            refs = ', '.join(self.literal(ref) for ref in fact.get("evidence_refs", []))
            facts.append(f'<strong>{self.literal(fact.get("kind"))}</strong>: '
                         f'{self.narrative(f"{prefix}/facts/{index}/value", fact.get("value"))}'
                         f'<small class="source-meta">{self.t("refs")}: {refs or self.t("unknown")}</small>')
        inferences = []
        for index, item in enumerate(summary.get("inferences", [])):
            basis = ', '.join(self.literal(ref) for ref in item.get("basis_fact_ids", []))
            inferences.append(f'{self.narrative(f"{prefix}/inferences/{index}/statement", item.get("statement"))}'
                              f'<small class="source-meta">{self.t("refs")}: {basis or self.t("unknown")}</small>')
        gaps = []
        for index, gap in enumerate(summary.get("gaps", [])):
            gaps.append(f'{self.narrative(f"{prefix}/gaps/{index}/detail", gap.get("detail"))}'
                        f'<small class="source-meta">{self.t("next_check")}: '
                        f'{self.narrative(f"{prefix}/gaps/{index}/next_check", gap.get("next_check"))}</small>')
        return (self.group("facts", self.items(facts)) + self.group("inferences", self.items(inferences))
                + self.group("gaps", self.items(gaps)))

    def goal(self) -> str:
        brief = self.state.get("brief")
        if not brief:
            return self.group("outcome", f'<p class="notice">{self.t("no_goal")}</p>') + self.group(
                "session_summary", self.t("no_brief"))
        details = brief.get("details") or {}
        intro = [self.row("outcome", self.narrative("/brief/goal", brief.get("goal"))),
                 self.row("decision", self.literal(brief.get("decision"))),
                 self.row("project_stage", self.literal(brief.get("project_stage")))]
        for field in ("problem", "target_user", "workflow"):
            intro.append(self.row(field, self.claim("/brief/details/" + field, details.get(field))))
        scenarios = [self.row(field, self.claim("/brief/details/" + field, details.get(field)))
                     for field in ("current_behavior", "target_behavior")]
        acceptance = [self.row("success_criterion", self.narrative("/brief/success_criterion", brief.get("success_criterion"))),
                      self.row("baseline", self.claim("/brief/details/baseline", details.get("baseline")))]
        scope = [self.row("scope", self.claim("/brief/details/scope", details.get("scope")))]
        scope += [self.row("non_goals", self.claim(f"/brief/details/non_goals/{i}", claim))
                  for i, claim in enumerate(details.get("non_goals", []))]
        saved = [name for name in ("scan", "brief", "memo") if self.state.get(name) is not None]
        summary = self.row("saved_deliverables", self.literal(", ".join(saved))) + self.row(
            "brief_version", self.literal(brief.get("brief_version")))
        return (self.group("outcome", '<dl class="detail-list">' + ''.join(intro) + '</dl>')
                + self.group("current_behavior", '<dl class="detail-list">' + ''.join(scenarios) + '</dl>')
                + self.group("success_criterion", '<dl class="detail-list">' + ''.join(acceptance) + '</dl>'
                             + f'<p class="source-meta">{self.t("not_measured")}</p>')
                + self.group("constraints", self.constraint_rows(brief))
                + self.group("scope", '<dl class="detail-list">' + ''.join(scope) + '</dl>')
                + self.group("session_summary", '<dl class="detail-list">' + summary + '</dl>'))

    def questions(self) -> str:
        intake = self.state["intake"]
        questions = intake.get("questions", [])
        by_id = {question["question_id"]: (index, question) for index, question in enumerate(questions)}
        answers = {answer["question_id"]: (index, answer) for index, answer in enumerate(intake.get("answers", []))}
        pending = by_id.get(intake.get("pending_question_id"))
        if pending:
            index, question = pending
            current = '<dl class="detail-list">' + ''.join((
                self.row("current_question", f'<strong>{question["ordinal"]}/10</strong> '
                         + self.narrative(f"/intake/questions/{index}/text", question.get("text"))),
                self.row("rationale", self.narrative(f"/intake/questions/{index}/rationale", question.get("rationale"))),
                self.row("consequence", self.narrative(f"/intake/questions/{index}/decision_consequence", question.get("decision_consequence"))),
            )) + '</dl>'
            examples = self.items([self.narrative(f"/intake/questions/{index}/answer_examples/{i}", item)
                                   for i, item in enumerate(question.get("answer_examples", []))])
        else:
            current, examples = self.t("no_question"), self.t("unknown")
        ledger = []
        for qid, (index, question) in by_id.items():
            saved = answers.get(qid)
            if not saved:
                continue
            answer_index, answer = saved
            status = answer.get("status", "skipped")
            value = self.narrative(f"/intake/answers/{answer_index}/sanitized_value", answer.get("sanitized_value"))
            ledger.append(f'<strong>{question["ordinal"]}. '
                          f'{self.narrative(f"/intake/questions/{index}/text", question.get("text"))}</strong>'
                          f'<p>{self.t(status) if status in UI_KEYS else self.literal(status)}: {value}</p>'
                          f'<small class="source-meta">{self.t("answer_revision")}: '
                          f'{self.literal(answer.get("answer_revision"))} · {self.t("recorded_at")}: '
                          f'{self.literal(answer.get("recorded_at"))}</small>')
        topics: dict[str, list[str]] = {}
        for question in questions:
            status = (answers.get(question["question_id"]) or (None, {}))[1].get("status")
            classification = status if status in ("answered", "skipped") else (
                "pending" if question["question_id"] == intake.get("pending_question_id") else "unasked")
            for topic in question.get("topics", []):
                topics.setdefault(topic, []).append(classification)
        topic_rows = [self.row("question_topics", self.literal(topic) + ": " + ", ".join(
            self.t(status) for status in statuses)) for topic, statuses in topics.items()]
        assumptions = [self.narrative(f"/intake/assumptions/{index}", value)
                       for index, value in enumerate(intake.get("assumptions", []))]
        completion = self.row("question_status", self.literal(intake.get("status"))) + self.row(
            "completion", self.narrative("/intake/completion_reason", intake.get("completion_reason")))
        return (self.group("current_question", current) + self.group("examples", examples + f'<p class="source-meta">{self.t("examples_note")}</p>')
                + self.group("saved_answers", self.items(ledger, "no_answers"))
                + self.group("coverage", '<dl class="detail-list">' + ''.join(topic_rows) + '</dl>')
                + self.group("completion", '<dl class="detail-list">' + completion + '</dl>' + self.items(assumptions))
                + self.group("correction_impact", f'<p>{self.t("correction_warning")}</p>'))

    def scan(self) -> str:
        scan = self.state.get("scan")
        if not scan:
            return self.group("scan_scope", f'<p class="notice">{self.t("no_scan")}</p>')
        manifest, summary = scan.get("manifest") or {}, scan.get("summary") or {}
        counters = manifest.get("counters") or {}
        policy = json.loads((ASSETS.parents[2] / "specs/scanner/scan-policy.yaml").read_text(encoding="utf-8"))
        mode = scan.get("mode")
        if scan.get("policy_version") != policy["schema_version"] or mode not in policy["modes"]:
            raise ValueError("unsupported scan policy")
        ceilings = policy["modes"][mode]
        scope = ''.join((self.row("project", self.literal(manifest.get("root_ref"))),
                         self.row("classification", self.literal(scan.get("classification"))),
                         self.row("scan_status", self.literal(scan.get("status"))),
                         self.row("coverage", self.literal(summary.get("coverage"))),
                         self.row("reason_codes", self.items([self.literal(code) for code in scan.get("reason_codes", [])]))))
        budget = ''.join((self.row("scan_mode", self.literal(mode)),
                          self.row("files", self.literal(counters.get("file_attempts")) + " / " + self.literal(ceilings["max_files"])),
                          self.row("bytes", self.literal(counters.get("bytes_consumed")) + " / " + self.literal(ceilings["max_bytes"])),
                          self.row("seconds", self.literal(counters.get("elapsed_ms")) + " ms / " + self.literal(ceilings["max_seconds"]) + " s"),
                          self.row("visited", self.literal(counters.get("visited_entries"))),
                          self.row("topology", self.literal(counters.get("topology_complete")))))
        source_rows = []
        for record in manifest.get("files", []):
            if record.get("disposition") != "read":
                continue
            findings = [self.narrative(f"/scan/summary/facts/{index}/value", fact.get("value"))
                        for index, fact in enumerate(summary.get("facts", []))
                        if record.get("evidence_ref") in fact.get("evidence_refs", [])]
            source_rows.append(f'<strong>{self.literal(record.get("relative_path"))}</strong> · '
                               f'{self.literal(record.get("disposition"))} · {self.literal(record.get("evidence_ref"))}'
                               + (f'<small class="source-meta">{self.t("facts")}: {"; ".join(findings)}</small>'
                                  if findings else ""))
        exclusions = [self.literal(key) + ": " + self.literal(value)
                      for key, value in (manifest.get("excluded_counts") or {}).items()]
        selection = self.state.get("selection") or {}
        requested = [self.literal(record.get("relative_path")) for record in selection.get("requested_sources", [])]
        return (self.group("scan_scope", '<dl class="detail-list">' + scope + '</dl>')
                + self.group("scan_budget", '<dl class="detail-list">' + budget + '</dl>')
                + self.group("findings", self.observations(summary, "/scan/summary"))
                + self.group("source_ledger", self.items(source_rows) + self.group("exclusions", self.items(exclusions)))
                + self.group("coverage_limit", self.items([self.literal(code) for code in scan.get("reason_codes", [])])
                             + (self.group("selection_request", self.items(requested) + f'<p>{self.t("requested_not_read")}</p>') if requested else ""))
                + self.group("boundary", f'<p>{self.t("scan_boundary")}</p>'))

    def context(self) -> str:
        brief = self.state.get("brief")
        if not brief:
            return self.group("system_outline", f'<p class="notice">{self.t("no_brief")}</p>')
        observations = brief.get("observations") or {}
        details = brief.get("details") or {}
        evidence = []
        for record in observations.get("evidence", []):
            location = self.literal(record.get("relative_path")) if record.get("relative_path") else self.t("unknown")
            supported = [self.narrative(f"/brief/observations/facts/{index}/value", fact.get("value"))
                         for index, fact in enumerate(observations.get("facts", []))
                         if record.get("evidence_id") in fact.get("evidence_refs", [])]
            evidence.append(f'{self.literal(record.get("evidence_id"))} · {self.literal(record.get("kind"))} · '
                            f'{location} · {self.literal(record.get("line_start"))}–{self.literal(record.get("line_end"))}'
                            + (f'<small class="source-meta">{self.t("facts")}: {"; ".join(supported)}</small>'
                               if supported else ""))
        cap_items = [self.narrative(f"/brief/observations/facts/{index}/value", fact.get("value"))
                     for index, fact in enumerate(observations.get("facts", []))
                     if fact.get("kind") in ("capability", "integration")]
        for field in ("problem", "target_user", "workflow", "current_behavior", "target_behavior", "baseline", "scope"):
            if field in details:
                evidence.append(self.t(field) + ": " + self.claim("/brief/details/" + field, details[field]))
        tensions = [self.narrative(f"/brief/details/tensions/{index}/detail", item.get("detail"))
                    + f'<small class="source-meta">{self.t("next_check")}: '
                    + self.narrative(f"/brief/details/tensions/{index}/next_decision", item.get("next_decision")) + '</small>'
                    for index, item in enumerate(details.get("tensions", []))]
        corrections = [self.literal(event.get("correction_id")) + " · " + ", ".join(
            self.literal(item) for item in event.get("invalidates", [])) for event in self.state.get("corrections", [])]
        corrections += [self.literal(item) for item in brief.get("user_corrections", [])]
        return (self.group("outcome", '<dl class="detail-list">' + self.row("outcome", self.narrative("/brief/goal", brief.get("goal")))
                           + self.row("success_criterion", self.narrative("/brief/success_criterion", brief.get("success_criterion"))) + '</dl>')
                + self.group("system_outline", self.observations(observations, "/brief/observations"))
                + self.group("capabilities", self.items(cap_items))
                + self.group("evidence_ledger", self.items(evidence))
                + self.group("constraints", self.constraint_rows(brief) + self.group("tensions", self.items(tensions)))
                + self.group("readiness", '<dl class="detail-list">' + self.row("brief_version", self.literal(brief.get("brief_version")))
                             + self.row("context_status", self.literal(brief.get("context_status"))) + '</dl>'
                             + self.group("corrections", self.items(corrections))))

    def _pack_cards(self) -> dict[int, dict[str, Any]]:
        pack = self.state.get("evidence_pack") or {}
        return {item["card"]["identity"]["github_repository_id"]: item
                for item in pack.get("cards", [])}

    def _narrative_items(self, pointer: str, values: list[str], empty: str = "unknown") -> str:
        return self.items([self.narrative(f"{pointer}/{index}", value)
                           for index, value in enumerate(values)], empty)

    def options(self) -> str:
        memo = self.state.get("memo") or {}
        no_memo_notice = f'<p class="notice">{self.t("no_memo")}</p>' if not self.state.get("memo") else ""
        cards = self._pack_cards()
        paths = [self.literal(item.get("category_id")) + " — " +
                 self.narrative(f"/memo/category_path/{index}/reason", item.get("reason"))
                 for index, item in enumerate(memo.get("category_path", []))]
        recommendations = []
        for index, rec in enumerate(memo.get("recommendations", [])):
            repo_id = rec["github_repository_id"]
            item = cards.get(repo_id)
            card = (item or {}).get("card") or {}
            identity = card.get("identity") or {}
            eligibility = (item or {}).get("eligibility") or {}
            title = self.literal(identity.get("full_name")) + " · " + self.literal(repo_id)
            url = identity.get("url")
            if isinstance(url, str) and url.startswith("https://github.com/"):
                title = f'<a href="{_escape(url)}">{title}</a>'
            activity = card.get("activity") or {}
            delivery = card.get("advisory") or {}
            eligibility_status = eligibility.get("status")
            eligibility_note = (f'<p class="notice">{self.t("blocked_candidate")}</p>'
                                if eligibility_status == "blocked" else
                                f'<p class="notice">{self.t("reference_candidate")}</p>'
                                if eligibility_status == "reference_only" else "")
            rows = [
                self.row("repository", title),
                self.row("role", self.literal(rec.get("role"))),
                self.row("eligibility", self.literal(eligibility.get("status")) + " · " +
                         self.items([self.literal(value) for value in eligibility.get("reason_codes", [])])),
                self.row("catalog_status", self.literal((card.get("catalog") or {}).get("status"))),
                self.row("fit", self.narrative(f"/memo/recommendations/{index}/fit_rationale", rec.get("fit_rationale"))),
                self.row("integration_surface", self.literal(delivery.get("integration_surface"))),
                self.row("matched_fields", self.items([self.literal(value) for value in (item or {}).get("matched_fields", [])])),
                self.row("license", self.literal(((card.get("repository") or {}).get("license") or {}).get("spdx"))),
                self.row("evidence", self.items([self.literal(value) for value in rec.get("evidence_refs", [])])),
                self.row("caveats", self._narrative_items(f"/memo/recommendations/{index}/caveats", rec.get("caveats", []))),
                self.row("next_checks", self._narrative_items(f"/memo/recommendations/{index}/next_checks", rec.get("next_checks", []))),
            ]
            for key in ("created_at", "pushed_at", "last_commit_at", "last_release_at", "observed_at"):
                rows.append(self.row(key, self.literal(activity.get(key))))
            recommendations.append('<article class="candidate"><h3>' + title + '</h3>'
                                   + eligibility_note + '<dl class="detail-list">' + ''.join(rows) + '</dl></article>')
        recommended_ids = {rec["github_repository_id"] for rec in memo.get("recommendations", [])}
        for repo_id, item in cards.items():
            if repo_id in recommended_ids:
                continue
            identity = item["card"]["identity"]
            recommendations.append('<article class="candidate"><h3>'
                                   + self.literal(identity.get("full_name")) + ' · ' + self.literal(repo_id)
                                   + '</h3><p class="notice">' + self.t("unassigned_card")
                                   + '</p><dl class="detail-list">'
                                   + self.row("eligibility", self.literal((item.get("eligibility") or {}).get("status")))
                                   + self.row("matched_fields", self.items([
                                       self.literal(field) for field in item.get("matched_fields", [])]))
                                   + '</dl></article>')
        request = self.state.get("request") or {}
        query = request.get("query") or {}
        retrieval = self.state.get("retrieval") or {}
        pack = self.state.get("evidence_pack") or {}
        pins = (self.state.get("index_manifest") or {}).get("pins") or pack.get("pins") or {}
        pack_bytes = len(json.dumps(pack, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")) if pack else None
        disclosure = [self.row("query", self.items([
            self.literal(term) for variant in query.get("variants", []) for term in variant.get("terms", [])])),
                      self.row("retrieved_hits", self.literal(retrieval.get("retrieved_hits"))),
                      self.row("candidates_count", self.literal(len(retrieval.get("candidates", []))) if retrieval else self.t("unknown")),
                      self.row("cards_count", self.literal(len(pack.get("cards", []))) if pack else self.t("unknown")),
                      self.row("pack_bytes", self.literal(pack_bytes)),
                      self.row("pack_status", self.literal(pack.get("status"))),
                      self.row("truncated", self.literal(pack.get("truncated")) if pack else self.t("unknown")),
                      self.row("reason_codes", self.items([self.literal(value) for value in
                                                          retrieval.get("reason_codes", []) + pack.get("reason_codes", [])])),
                      self.row("snapshot_id", self.literal(pins.get("catalog_snapshot_id"))),
                      self.row("index_format", self.literal(pins.get("index_format_version"))),
                      self.row("source_snapshot_date", self.literal((self.state.get("index_manifest") or {}).get("source_snapshot_date"))),
                      self.row("built_at", self.literal((self.state.get("index_manifest") or {}).get("built_at")))]
        avoid = [self.narrative(f"/memo/avoid_defer_details/{index}/rationale", item.get("rationale"))
                 + f' · {self.literal(item.get("github_repository_id"))}'
                 + f'<small class="source-meta">{self.t("revisit_when")}: '
                 + self.narrative(f"/memo/avoid_defer_details/{index}/revisit_when", item.get("revisit_when"))
                 + ' · ' + ', '.join(self.literal(ref) for ref in item.get("evidence_refs", [])) + '</small>'
                 for index, item in enumerate(memo.get("avoid_defer_details", []))]
        avoid += [self.narrative(f"/memo/avoid_defer/{index}", value)
                  for index, value in enumerate(memo.get("avoid_defer", []))]
        reading = [self.literal(item.get("evidence_ref")) + ' · '
                   + self.narrative(f"/memo/reading_path/{index}/purpose", item.get("purpose"))
                   for index, item in enumerate(memo.get("reading_path", []))]
        return (self.group("recommendation_summary", no_memo_notice + '<dl class="detail-list">'
                           + self.row("recommendation_summary", self.narrative("/memo/summary", memo.get("summary")))
                           + self.row("status", self.literal(memo.get("status")))
                           + self.row("evidence_ceiling", self.literal(memo.get("evidence_ceiling")))
                           + '</dl>' + self._narrative_items("/memo/missing_context", memo.get("missing_context", [])))
                + self.group("category_path", self.items(paths))
                + self.group("candidate_roles", ''.join(recommendations) if recommendations else self.t("unknown"))
                + self.group("retrieval_disclosure", '<dl class="detail-list">' + ''.join(disclosure) + '</dl>')
                + self.group("avoid_defer", self.items(avoid))
                + self.group("reading_path", self.items(reading)))

    def compare(self) -> str:
        memo = self.state.get("memo")
        if not memo:
            return self.group("decision_matrix", f'<p class="notice">{self.t("no_memo")}</p>')
        details = memo.get("comparison_details")
        if not details:
            return (self.group("comparison_scope", self.t("no_comparison_details"))
                    + self.group("decision_matrix", self._narrative_items("/memo/comparison", memo.get("comparison", [])))
                    + self.group("avoid_defer", self._narrative_items("/memo/avoid_defer", memo.get("avoid_defer", [])))
                    + f'<p class="source-meta">{self.t("draft_only")}</p>')
        cells = details.get("cells", [])
        cards = self._pack_cards()
        ids = list(dict.fromkeys([rec["github_repository_id"] for rec in memo.get("recommendations", [])] +
                                 [cell["github_repository_id"] for cell in cells if not cell.get("baseline")]))
        columns = [(repo_id, self.literal(((cards.get(repo_id) or {}).get("card") or {}).get("identity", {}).get("full_name"))
                    + ' · ' + self.literal(repo_id)) for repo_id in ids]
        if details.get("include_no_change"):
            columns.insert(0, (None, self.t("no_change")))
        criteria = list(dict.fromkeys(cell["criterion"] for cell in cells))
        rows = []
        for criterion in criteria:
            entries = []
            for repo_id, _ in columns:
                matches = [(index, cell) for index, cell in enumerate(cells)
                           if cell["criterion"] == criterion and cell.get("github_repository_id") == repo_id
                           and bool(cell.get("baseline")) == (repo_id is None)]
                if not matches:
                    entries.append(f'<td>{self.t("no_matrix_cell")}</td>')
                    continue
                index, cell = matches[0]
                content = self.claim(f"/memo/comparison_details/cells/{index}/claim", cell.get("claim"))
                if cell.get("next_check"):
                    content += '<small class="source-meta">' + self.t("next_check") + ': ' + self.narrative(
                        f"/memo/comparison_details/cells/{index}/next_check", cell["next_check"]) + '</small>'
                entries.append(f'<td>{content}</td>')
            rows.append(f'<tr><th scope="row">{self.literal(criterion)}</th>{"".join(entries)}</tr>')
        matrix = ('<div class="matrix-scroll"><table><thead><tr><th scope="col">' + self.t("decision_matrix")
                  + '</th>' + ''.join(f'<th scope="col">{name}</th>' for _, name in columns)
                  + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>') if rows else self.t("no_comparison_details")
        reasoning = '<dl class="detail-list">' + ''.join([
            self.row(key, self.narrative("/memo/comparison_details/" + pointer, details.get(pointer)))
            for key, pointer in (("selection_rationale", "selection_rationale"),
                                 ("counterargument", "strongest_counterargument"),
                                 ("reconsider_when", "reconsider_when"),
                                 ("next_decision", "next_decision"))]) + '</dl>'
        exclusions = [self.literal(item.get("github_repository_id")) + ' · '
                      + self.narrative(f"/memo/avoid_defer_details/{index}/rationale", item.get("rationale"))
                      for index, item in enumerate(memo.get("avoid_defer_details", []))]
        exclusions += [self.literal(item.get("github_repository_id")) + ' · '
                       + self.items([self.literal(code) for code in (item.get("eligibility") or {}).get("reason_codes", [])])
                       for item in (self.state.get("evidence_pack") or {}).get("exclusions", [])]
        brief = self.state.get("brief") or {}
        return (self.group("comparison_scope", self.narrative("/memo/comparison_details/scope", details.get("scope")))
                + self.group("constraints", self.constraint_rows(brief) if brief else self.t("no_brief"))
                + self.group("decision_matrix", matrix)
                + self.group("selection_rationale", reasoning)
                + self.group("exclusions", self.items(exclusions))
                + f'<p class="source-meta">{self.t("draft_only")}</p>')

    def integration(self) -> str:
        memo = self.state.get("memo") or {}
        plan = memo.get("integration_plan")
        if not plan:
            return self.group("proposed_outcome", f'<p class="notice">{self.t("no_plan")}</p>')
        details = plan.get("details") or {}
        diagram = details.get("diagram")
        if diagram:
            nodes = [self.literal(node.get("component_id")) + ' · '
                     + self.narrative(f"/memo/integration_plan/details/diagram/nodes/{index}/label", node.get("label"))
                     + ' · ' + self.literal(node.get("change")) + ' · '
                     + ', '.join(self.literal(ref) for ref in node.get("evidence_refs", []))
                     for index, node in enumerate(diagram.get("nodes", []))]
            edges = [self.literal(edge.get("from_component_id")) + ' → '
                     + self.literal(edge.get("to_component_id")) + ' · '
                     + self.narrative(f"/memo/integration_plan/details/diagram/edges/{index}/label", edge.get("label"))
                     for index, edge in enumerate(diagram.get("edges", []))]
            proposed = (f'<p class="notice">{self.t("proposed")}</p>'
                        + self.group("diagram_nodes", self.items(nodes))
                        + self.group("diagram_edges", self.items(edges)))
        else:
            proposed = self.t("unknown")
        checks = []
        for index, check in enumerate(details.get("prerequisite_checks", [])):
            text = (self.literal(check.get("kind")) + ' · ' + self.literal(check.get("status")) + ' · '
                    + self.narrative(f"/memo/integration_plan/details/prerequisite_checks/{index}/detail", check.get("detail")))
            refs = check.get("evidence_refs", []) + check.get("answer_ids", [])
            if refs:
                text += f'<small class="source-meta">{self.t("refs")}: '
                text += ', '.join(self.literal(ref) for ref in refs) + '</small>'
            if check.get("next_check"):
                text += f'<small class="source-meta">{self.t("next_check")}: '
                text += self.narrative(f"/memo/integration_plan/details/prerequisite_checks/{index}/next_check",
                                       check["next_check"]) + '</small>'
            checks.append(text)
        checks += [self.narrative(f"/memo/integration_plan/prerequisites/{index}", value)
                   for index, value in enumerate(plan.get("prerequisites", []))]
        dependencies = {entry["step_id"]: entry for entry in details.get("step_dependencies", [])}
        steps = []
        for index, step in enumerate(plan.get("steps", [])):
            dependency = dependencies.get(step["step_id"], {})
            commands = [self.literal(command) for command in step.get("proposed_commands", [])]
            rows = [self.row("affected_components", self.items([
                self.literal(value) for value in step.get("affected_components", [])])),
                    self.row("prerequisites", self._narrative_items(
                        f"/memo/integration_plan/steps/{index}/prerequisites", step.get("prerequisites", []))),
                    self.row("depends_on", self.items([self.literal(value) for value in dependency.get("depends_on", [])])),
                    self.row("safe_paths", self.items([self.literal(value) for value in dependency.get("safe_paths", [])])),
                    self.row("evidence", self.items([self.literal(value) for value in dependency.get("evidence_refs", [])])),
                    self.row("proposed_commands", self.items(commands) + ' · ' + self.literal(step.get("command_status"))),
                    self.row("acceptance", self.narrative(f"/memo/integration_plan/steps/{index}/acceptance", step.get("acceptance")))]
            steps.append('<article class="candidate"><h3>' + self.literal(step.get("step_id")) + '</h3>'
                         + self.narrative(f"/memo/integration_plan/steps/{index}/action", step.get("action"))
                         + '<dl class="detail-list">' + ''.join(rows) + '</dl></article>')
        first = plan.get("first_validation") or {}
        validation = '<dl class="detail-list">' + ''.join([
            self.row("outcome", self.narrative("/memo/integration_plan/first_validation/goal", first.get("goal"))),
            self.row("success_criterion", self.narrative("/memo/integration_plan/first_validation/success_criterion",
                                                       first.get("success_criterion"))),
            self.row("validation_input", self.narrative("/memo/integration_plan/details/validation_input", details.get("validation_input"))),
            self.row("expected_behavior", self.narrative("/memo/integration_plan/details/expected_behavior", details.get("expected_behavior"))),
            self.row("widen_when", self.narrative("/memo/integration_plan/details/widen_when", details.get("widen_when"))),
            self.row("proposed_commands", self.items([self.literal(command) for command in first.get("proposed_commands", [])])),
            self.row("execution_status", self.literal(first.get("status")) + ' · ' + self.t("actual_not_run")),
        ]) + '</dl>'
        handoff = plan.get("handoff") or {}
        handoff_rows = [
            self.row("outcome", self.narrative("/memo/integration_plan/handoff/goal", handoff.get("goal"))),
            self.row("scope", self.narrative("/memo/integration_plan/handoff/scope", handoff.get("scope"))),
            self.row("non_goals", self._narrative_items("/memo/integration_plan/handoff/non_goals", handoff.get("non_goals", []))),
            self.row("evidence", self.items([self.literal(ref) for ref in plan.get("evidence_refs", [])])),
            self.row("first_slice", self.narrative("/memo/integration_plan/steps/0/action",
                                                  plan.get("steps", [{}])[0].get("action"))),
            self.row("acceptance", self.narrative("/memo/integration_plan/steps/0/acceptance",
                                                 plan.get("steps", [{}])[0].get("acceptance"))),
            self.row("stop_conditions", self._narrative_items(
                "/memo/integration_plan/handoff/stop_conditions", handoff.get("stop_conditions", []))),
            self.row("execution_authority", self.literal(handoff.get("execution_authority"))),
            self.row("permission_changes", self.literal(handoff.get("permission_changes"))),
        ]
        intro = '<dl class="detail-list">' + ''.join([
            self.row("proposed_outcome", self.narrative("/memo/integration_plan/goal", plan.get("goal"))),
            self.row("execution_status", self.literal(plan.get("execution_status"))),
            self.row("selected_candidates", self.items([
                self.literal(value) for value in plan.get("selected_github_repository_ids", [])])),
            self.row("brief_version", self.literal(plan.get("brief_version"))),
            self.row("missing_context", self._narrative_items(
                "/memo/integration_plan/unresolved_questions", plan.get("unresolved_questions", []))),
        ]) + '</dl>'
        return (self.group("proposed_outcome", intro + f'<p class="source-meta">{self.t("source_not_execution")}</p>')
                + self.group("proposed_diagram", proposed)
                + self.group("prerequisites", self.items(checks))
                + self.group("steps", ''.join(steps) if steps else self.t("unknown"))
                + self.group("first_validation", validation)
                + self.group("risks", self._narrative_items("/memo/integration_plan/risks", plan.get("risks", [])))
                + self.group("rollback", self._narrative_items("/memo/integration_plan/rollback", plan.get("rollback", [])))
                + self.group("coding_handoff", '<div id="coding-handoff" class="copy-panel" tabindex="0">'
                             + '<dl class="detail-list">' + ''.join(handoff_rows) + '</dl></div>'
                             + f'<p class="source-meta">{self.t("handoff_instruction")}</p>'))


def render_report(state: dict[str, Any]) -> bytes:
    """Render a validated snapshot without state writes, retrieval or translation."""
    try:
        dictionaries = load_locales()
        locale = (state.get("presentation") or {}).get("default_locale", "ru")
        if locale not in dictionaries:
            raise ValueError("invalid saved locale")
        labels = dictionaries[locale]
        content = ViewContent(state, locale, dictionaries)

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
            if view in ("goal", "questions", "scan", "context", "options", "compare", "integration"):
                details = getattr(content, view)()
                if view == "questions":
                    details = (f'<p class="source-meta">{text("questions_count")}: '
                               f'{state["intake"]["questions_asked"]} · {text("answers_count")}: '
                               f'{len(state["intake"]["answers"])}. {text("question_limit")}</p>' + details)
            else:
                details = f'<p class="notice">{text("pending_view")}</p>'
            sections.append(
                f'<section id="{view}" aria-labelledby="heading-{view}" tabindex="-1">'
                f'<p class="eyebrow">{index:02} / 08</p><h1 id="heading-{view}">{text(view)}</h1>'
                f'<p class="availability">{text("source")}: {text(availability)}</p>'
                f'{details}</section>'
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
