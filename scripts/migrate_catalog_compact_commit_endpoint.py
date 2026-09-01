"""Migrate a saved CAT-05 run to bounded Git-object commit collection.

The migration updates only the frozen field contract and integrity pins. It
preserves the source snapshot, records, request log, counters, and curation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import enrich_catalog as e


ROOT = Path(__file__).resolve().parents[1]


def atomic_copy(source: Path, target: Path) -> None:
    temporary = target.with_suffix(target.suffix + '.tmp')
    with temporary.open('wb') as handle:
        handle.write(source.read_bytes())
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, target)


def migrate(run: Path, contract: Path) -> dict:
    required = ('plan.json', 'gap-plan.json', 'field-contract.json', 'checkpoint.json')
    missing = [name for name in required if not (run / name).is_file()]
    if missing:
        raise ValueError('Saved run is incomplete: ' + ', '.join(missing))

    with e.single_writer(run):
        plan_path = run / 'plan.json'
        gap_plan_path = run / 'gap-plan.json'
        frozen_contract = run / 'field-contract.json'
        plan = e.load(plan_path)
        gap_plan = e.load(gap_plan_path)

        old_plan_sha = e.sha(plan_path)
        if gap_plan.get('collectorPlanSha256') != old_plan_sha:
            raise ValueError('Gap plan does not pin the current collector plan')
        old_contract_sha = e.sha(frozen_contract)
        if plan.get('pins', {}).get('field-contract.json', {}).get('sha256') != old_contract_sha:
            raise ValueError('Frozen field contract does not match its plan pin')
        if gap_plan.get('scriptSha256') != e.sha(ROOT / 'scripts' / 'catalog_gap_fill.py'):
            raise ValueError('Gap pipeline changed; migrate it separately')
        if gap_plan.get('transportSha256') != e.sha(ROOT / 'scripts' / 'github_cli_transport.py'):
            raise ValueError('GitHub transport changed; migrate it separately')

        old_collector_sha = plan.get('collectorSha256')
        atomic_copy(contract, frozen_contract)
        new_contract_sha = e.sha(frozen_contract)
        plan['pins']['field-contract.json'] = {
            'sha256': new_contract_sha,
            'origin': str(contract.resolve()),
        }
        plan['collectorSha256'] = e.sha(ROOT / 'scripts' / 'enrich_catalog.py')
        e.atomic_json(plan_path, plan)
        gap_plan['collectorPlanSha256'] = e.sha(plan_path)
        e.atomic_json(gap_plan_path, gap_plan)

        checkpoint = e.load(run / 'checkpoint.json')
        result = {
            'migration': 'compact_git_object_commit_and_terminal_unsupported_source_v1',
            'oldCollectorSha256': old_collector_sha,
            'newCollectorSha256': plan['collectorSha256'],
            'oldContractSha256': old_contract_sha,
            'newContractSha256': new_contract_sha,
            'oldCollectorPlanSha256': old_plan_sha,
            'newCollectorPlanSha256': gap_plan['collectorPlanSha256'],
            'recordsPreserved': len(checkpoint.get('records', {})),
            'requestsPreserved': checkpoint.get('requests', 0),
            'bytesPreserved': checkpoint.get('bytes', 0),
            'canonicalWritten': False,
        }
        artifact = run / 'compact-commit-endpoint-migration.json'
        if artifact.exists():
            artifact = run / 'compact-commit-endpoint-migration-02.json'
        e.atomic_json(artifact, result)
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--contract', type=Path,
                        default=ROOT / 'specs' / 'catalog' / 'enrichment-field-contract.json')
    args = parser.parse_args()
    print(json.dumps(migrate(args.run_dir.resolve(), args.contract.resolve()), ensure_ascii=False))


if __name__ == '__main__':
    main()
