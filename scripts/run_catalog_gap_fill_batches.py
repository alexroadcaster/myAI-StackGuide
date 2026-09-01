"""Run bounded CAT-05 gap-fill invocations until a durable stop condition.

This driver does not own credentials, HTTP, catalog writes or counters. Each round
uses the pinned gap-fill pipeline and its single-writer/checkpoint boundaries.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import enrich_catalog as e
from catalog_gap_fill import GapFill
from github_cli_transport import GitHubCLITransport


CONTINUE_REASONS = {"elapsed_time_budget", "record_budget", "request_budget"}


def run_batches(run_dir: Path, max_rounds: int, requests_per_round: int, records_per_round: int):
    rounds = []
    for round_number in range(1, max_rounds + 1):
        with e.single_writer(run_dir):
            result = GapFill(run_dir, GitHubCLITransport()).execute(
                max_requests=requests_per_round,
                max_records=records_per_round,
            )
        result = {"round": round_number, **result}
        rounds.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
        if result["stopReason"] not in CONTINUE_REASONS:
            break
        if result["attemptedThisInvocation"] == 0 and result["newTransportAttempts"] <= 1:
            break
    return {
        "roundsCompleted": len(rounds),
        "final": rounds[-1],
        "stoppedAfterConfiguredRounds": len(rounds) == max_rounds
        and rounds[-1]["stopReason"] in CONTINUE_REASONS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--max-rounds", type=int, default=1)
    parser.add_argument("--requests-per-round", type=int, default=1000)
    parser.add_argument("--records-per-round", type=int, default=250)
    args = parser.parse_args()
    if min(args.max_rounds, args.requests_per_round, args.records_per_round) < 1:
        parser.error("All budgets must be positive")
    print(
        json.dumps(
            run_batches(
                args.run_dir,
                args.max_rounds,
                args.requests_per_round,
                args.records_per_round,
            ),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
