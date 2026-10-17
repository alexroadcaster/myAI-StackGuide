"""Objective rejection checks; no recommendation-quality assertions."""
import importlib.util
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals/plugin-v1"))
SPEC = importlib.util.spec_from_file_location("vertical_eval", ROOT / "evals/plugin-v1/evaluate_vertical_slice.py")
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


class VerticalEvalTests(unittest.TestCase):
    def test_source_public_card_is_accepted_and_tampered_provenance_or_eligibility_rejected(self):
        snapshot = json.loads((EVAL.ASSETS / "catalog.snapshot.json").read_bytes())
        card = next(card for card in snapshot["cards"] if card["identity"]["github_repository_id"] == 37489525)
        query = json.loads((ROOT / "tests/fixtures/plugin_contracts.json").read_bytes())["positive"]["retrieval/catalog-query.schema.json"]
        cards = {37489525: card}
        entry = {"card": card, "eligibility": EVAL.MATCHER.match_candidate(card, query)}
        EVAL.validate_public_entry(entry, query, cards)
        changed_activity = copy.deepcopy(entry)
        changed_activity["card"]["activity"]["observations"][0]["source_field"] = "invented-date-field"
        changed_evidence = copy.deepcopy(entry)
        changed_evidence["card"]["evidence"][0]["source_ref"] = "fixture:invented"
        changed_eligibility = copy.deepcopy(entry)
        changed_eligibility["eligibility"]["status"] = "primary_eligible"
        for candidate in (changed_activity, changed_evidence, changed_eligibility):
            with self.assertRaisesRegex(ValueError, "source|eligibility"):
                EVAL.validate_public_entry(candidate, query, cards)

    def test_missing_or_changed_source_binding_is_rejected(self):
        valid = EVAL.source_bindings()
        EVAL.check_sources(valid)
        changed = dict(valid, **{"plugins/myai-stackguide/scripts/intake.py": "0" * 64})
        missing = dict(valid)
        del missing["plugins/myai-stackguide/assets/session-contracts.json"]
        for bindings in (changed, missing):
            with self.subTest(kind="changed" if bindings is changed else "missing"), self.assertRaisesRegex(ValueError, "source"):
                EVAL.check_sources(bindings)

    def test_mixed_public_pack_pins_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "pins"):
            EVAL.check_pins({"retrieval": {"pins": {"index_sha256": "0" * 64}},
                             "evidence_pack": {"pins": {"index_sha256": "1" * 64}}},
                            {"pins": {"index_sha256": "0" * 64}})

    def test_false_current_publication_revision_is_rejected(self):
        names = ["start", "answer", "commit-scan", "commit-context", "commit-matching", "commit-memo",
                 "correct", "retry-publication", "commit-matching", "commit-memo", "finalize", "start"]
        revisions = [1, 2, 3, 4, 5, 6, 7, 7, 8, 9, 10, 1]
        events = []
        for index, (command, revision) in enumerate(zip(names, revisions)):
            stamp = {"run_id": "successor" if index == 11 else "original", "revision": revision,
                     "content_revision": revision}
            events.append({"command": command, "response": {"publication_status": "current",
                "failure_reason": None, "saved": dict(stamp), "current": dict(stamp),
                "published": dict(stamp), "render_attempts": 1, "retry": "none"}})
        EVAL.check_lifecycle(events)
        forged = copy.deepcopy(events)
        forged[5]["response"]["published"]["revision"] += 1
        with self.assertRaisesRegex(ValueError, "publication|lifecycle"):
            EVAL.check_lifecycle(forged)


if __name__ == "__main__":
    unittest.main()
