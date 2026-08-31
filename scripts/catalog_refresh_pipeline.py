"""Batch catalog refresh without LLM calls or canonical writes.

Uses the frozen enrich_catalog run, its public GET transport and cumulative
budgets. Saved research is a discovery pool, never fresh verification or review.
"""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
import re
import time
import tomllib
from collections import Counter
from pathlib import Path

import enrich_catalog as e

TERMINAL = {'complete_card', 'verified_identity_alias', 'excluded_below_star_threshold'}
FAILURES = {'fetch_error', 'budget_exhausted'}
DEFAULT_POOLS = [e.ROOT / 'research/github_search_candidates_2026-05-23.json',
                 e.ROOT / 'research/github_business_search_candidates_html_2026-05-23.json']


def candidate_pool(paths, source, taxonomy):
    """Collect explicit repo names/category hints only; ignore old Stars/rankings."""
    known = {r['fullName'].casefold() for r in source.values()}
    known.update(a.casefold() for r in source.values() for a in r.get('aliases', []) if isinstance(a, str))
    leaves = {c['id'] for c in taxonomy['categories'] if c['kind'] == 'category'}
    result = {}

    def visit(node, path):
        if isinstance(node, list):
            for item in node:
                visit(item, path)
        elif isinstance(node, dict):
            name = node.get('fullName', node.get('full_name', ''))
            if isinstance(name, str) and e.NAME.fullmatch(name) and name.casefold() not in known:
                hints = [node.get(k) for k in ('primaryCategory', 'category', 'source_category')]
                hints += node.get('matched_categories', []) if isinstance(node.get('matched_categories'), list) else []
                hints = {h for h in hints if isinstance(h, str) and h in leaves}
                entry = result.setdefault(name.casefold(), {'fullName': name, 'categoryHints': [], 'sources': [], 'sourceEvidence': []})
                entry['categoryHints'] = sorted(set(entry['categoryHints']) | hints)
                if str(path) not in entry['sources']:
                    entry['sources'].append(str(path))
                if isinstance(node.get('discovery'), dict) and node['discovery'].get('provider') in ('ossinsight', 'ecosystems'):
                    evidence = {k: node['discovery'].get(k) for k in ('provider', 'sourceUrl', 'retrievedAt', 'sourceSyncedAt', 'inputSha256', 'dataLicense', 'status')}
                    if evidence not in entry['sourceEvidence']:
                        entry['sourceEvidence'].append(evidence)
            for value in node.values():
                if isinstance(value, (dict, list)):
                    visit(value, path)

    for path in paths:
        visit(e.load(path), path.resolve())
    return [result[k] for k in sorted(result)]


def prepare(run, pools, batch_size=25, replacement_limit=3):
    if batch_size < 1 or replacement_limit < 1:
        raise ValueError('Limits must be positive')
    target = run / 'pipeline-plan.json'
    if target.exists():
        raise ValueError('Pipeline already prepared; do not silently change frozen discovery/budgets')
    collector = e.Collector(run)
    config = {'version': '1.0.0', 'createdAt': e.now(),
              'pipelineSha256': e.sha(__file__), 'collectorPlanSha256': e.sha(run / 'plan.json'),
              'maxRepositoriesPerBatch': batch_size, 'maxCandidatesPerExclusion': replacement_limit,
              'poolPins': {str(p.resolve()): e.sha(p) for p in pools},
              'pool': candidate_pool(pools, collector.source, collector.taxonomy),
              'scope': 'public_GET_no_credentials_no_LLM_candidate_projection_only'}
    e.atomic_json(target, config)
    e.atomic_json(run / 'pipeline-state.json', {'candidates': {}, 'replacementAttempts': {}, 'replacements': {}})
    return {'prepared': True, 'inputRecords': len(collector.source), 'discoveryCandidates': len(config['pool']),
            'batchLimit': batch_size, 'credentialUse': False, 'networkPerformed': False}


def extracted_hints(record):
    """Parse literal runtime dependency declarations. Never label them reviewed Stack."""
    facts = []
    issues = []
    for key, block in record['blocks'].items():
        if not key.startswith('file:') or block.get('status') != 'observed':
            continue
        data = block['data']
        if data.get('truncated'):
            issues.append(key + ':truncated_manifest')
            continue
        text = data.get('excerpt', '')
        names = []
        try:
            if key == 'file:package.json':
                names = list(json.loads(text).get('dependencies', {}))
            elif key == 'file:pyproject.toml':
                names = tomllib.loads(text).get('project', {}).get('dependencies', [])
            elif key == 'file:Cargo.toml':
                names = list(tomllib.loads(text).get('dependencies', {}))
            elif key == 'file:requirements.txt':
                names = [line.strip() for line in text.splitlines() if re.match(r'^[A-Za-z0-9][A-Za-z0-9_.-]*(?:[<>=!~\[; ]|$)', line)]
            elif key == 'file:go.mod':
                names = re.findall(r'^\s*(?:require\s+)?([\w.-]+\.[\w./-]+)\s+v\S+', text, re.M)
            elif key == 'file:composer.json':
                names = list(json.loads(text).get('require', {}))
        except (ValueError, TypeError, AttributeError):
            issues.append(key + ':parse_error')
            continue
        for name in names[:80]:
            if isinstance(name, str):
                facts.append({'declaration': e.clean_excerpt(name)[:240], 'evidenceRef': key,
                              'path': data.get('path'), 'ref': data.get('ref')})
    metadata = record['blocks'].get('metadata', {}).get('data', {})
    return {'status': 'source_declarations_not_reviewed_stack', 'dependencies': facts, 'issues': issues,
            'upstreamDescription': metadata.get('description'),
            'descriptionNeedsSummary': not bool((metadata.get('description') or '').strip())}


class Pipeline:
    def __init__(self, run, transport=None):
        self.run = Path(run)
        self.config = e.load(self.run / 'pipeline-plan.json')
        if self.config['pipelineSha256'] != e.sha(__file__) or self.config['collectorPlanSha256'] != e.sha(self.run / 'plan.json'):
            raise ValueError('Pipeline/collector plan changed; an explicit migration is required')
        for path, digest in self.config['poolPins'].items():
            if e.sha(path) != digest:
                raise ValueError('Discovery pool changed; an explicit migration is required')
        self.state = e.load(self.run / 'pipeline-state.json')
        self.c = e.Collector(self.run, transport)
        self.original = copy.deepcopy(self.c.source)
        self.c.source.update(self.state['candidates'])

    def save(self):
        e.atomic_json(self.run / 'pipeline-state.json', self.state)

    def record(self, ident):
        path = self.c.record_path(ident)
        return e.load(path) if path.exists() else None

    def stop_reason(self):
        if time.time() < self.c.state['retryNotBefore']:
            return 'rate_limit_wait'
        if self.c.state['requests'] >= self.c.plan['maxRequests'] or self.c.state['bytes'] >= self.c.plan['maxBytes']:
            return 'cumulative_budget_exhausted'
        if time.monotonic() - self.c.started >= self.c.plan['maxSecondsPerInvocation']:
            return 'invocation_time_budget'
        return None

    def review(self, ident):
        path = self.run / 'curation' / self.c.record_path(ident).name
        return e.load(path) if path.exists() else None

    def needs_collection(self, ident):
        record = self.record(ident)
        if record is None:
            return True
        if any(b['status'] in FAILURES for b in record['blocks'].values()):
            return True
        if record.get('status') in TERMINAL:
            return False
        if not record.get('values'):
            return True
        review = self.review(ident)
        return review is not None and review != record.get('curation')

    def collect(self, ident):
        record = self.c.process(ident, self.review(ident))
        if not record.get('aliasOf'):
            e.atomic_json(self.run / 'extracted' / self.c.record_path(ident).name, extracted_hints(record))
        return record

    def replacements(self):
        """One-to-one swaps require complete reviewed cards, category fit and uniqueness."""
        used = set()
        result = {}
        original_names = {r['fullName'].casefold() for r in self.original.values()}
        original_ids = {r.get('githubRepositoryId') for r in self.original.values()} - {None}
        for ident in self.original:
            record = self.record(ident)
            if record and record['blocks'].get('metadata', {}).get('status') == 'observed':
                original_ids.add(record['blocks']['metadata']['data']['githubRepositoryId'])
        for excluded, candidates in self.state['replacementAttempts'].items():
            record = self.record(excluded)
            if not record or record.get('status') != 'excluded_below_star_threshold':
                continue
            if record['values'].get('identityStatus') != 'resolved':
                continue
            for ident in candidates:
                candidate = self.record(ident)
                if not candidate or candidate.get('status') != 'complete_card':
                    continue
                if any(b['status'] in FAILURES for b in candidate['blocks'].values()):
                    continue
                value = candidate['values']
                identity = value['githubRepositoryId']
                if identity in used or identity in original_ids or value['fullName'].casefold() in original_names:
                    continue
                if value['primaryCategory'] != self.original[excluded]['primaryCategory']:
                    continue
                if value['stars'] < self.c.min_stars or not value['eligibility']['dataGatePassed']:
                    continue
                if self.c.source[ident].get('discovery', {}).get('replacementFor') != excluded:
                    raise ValueError('Replacement registration mismatch')
                result[excluded] = ident
                used.add(identity)
                break
        return result

    def next_replacement(self, excluded):
        if self.record(excluded)['values'].get('identityStatus') != 'resolved':
            return None
        if excluded in self.replacements():
            return None
        attempts = self.state['replacementAttempts'].setdefault(excluded, [])
        for ident in attempts:
            if self.needs_collection(ident):
                return ident
        # A source-backed candidate awaiting content review is already a useful
        # replacement lead. Do not spend requests collecting more alternatives.
        if any(self.record(i) and self.record(i).get('status') == 'needs_review_or_retry' for i in attempts):
            return None
        if len(attempts) >= self.config['maxCandidatesPerExclusion']:
            return None
        category = self.original[excluded]['primaryCategory']
        known = {r['fullName'].casefold() for r in self.c.source.values()}
        for candidate in self.config['pool']:
            if candidate['fullName'].casefold() in known or category not in candidate['categoryHints']:
                continue
            ident = 'gh-replacement:' + candidate['fullName'].casefold()
            source = {'id': ident, 'fullName': candidate['fullName'], 'catalogStatus': 'candidate',
                      'primaryCategory': category, 'stars': None,
                      'discovery': {'replacementFor': excluded, 'sourceFiles': candidate['sources'],
                                    'sourceEvidence': candidate['sourceEvidence'],
                                    'status': 'historical_search_hint_not_verified_category'}}
            self.state['candidates'][ident] = source
            self.c.source[ident] = source
            attempts.append(ident)
            self.save()  # Register identity before any network I/O; resume reuses it.
            return ident
        return None

    def batch(self):
        count = 0
        stop = None
        for ident in self.c.plan['queue']:
            stop = self.stop_reason()
            if stop or count >= self.config['maxRepositoriesPerBatch']:
                break
            if self.needs_collection(ident):
                self.collect(ident)
                count += 1
            record = self.record(ident)
            if record and record.get('status') == 'excluded_below_star_threshold':
                while count < self.config['maxRepositoriesPerBatch'] and not self.stop_reason():
                    replacement = self.next_replacement(ident)
                    if replacement is None:
                        break
                    self.collect(replacement)
                    count += 1
            # No LLM turn or curator decision between repositories. Pending
            # semantic fields are durably queued by reports() below.
        self.state['replacements'] = self.replacements()
        self.save()
        result = self.reports()
        return {**result, 'processedThisBatch': count,
                'stopReason': self.stop_reason() or stop or ('batch_limit' if count >= self.config['maxRepositoriesPerBatch'] else 'queue_collected_or_review_pending')}

    def reports(self):
        self.c.verify()
        self.state['replacements'] = self.replacements()
        self.save()
        rows, exceptions, active, exclusions = [], [], [], []
        states = Counter()
        coverage = {f['id']: Counter() for f in self.c.contract['fields']}
        freshness = []
        failed_records = 0
        for ident, source in self.c.source.items():
            record = self.record(ident)
            status = record.get('status', 'interrupted') if record else 'not_started'
            values = record.get('values', {}) if record else {}
            original = ident in self.original
            identity_conflict = values.get('identityStatus') == 'conflict'
            external_alias = record and record.get('aliasOf') and record['aliasOf'] not in self.original
            if identity_conflict or external_alias:
                status = 'identity_review_required'
            failed = [k for k, b in record['blocks'].items() if b['status'] in FAILURES] if record else []
            failed_records += bool(failed)
            if original:
                states[status] += 1
                observations = {x['field']: x['status'] for x in values.get('fieldObservations', [])}
                for key in coverage:
                    coverage[key][observations.get(key, 'not_attempted')] += 1
            if record:
                for key, block in record['blocks'].items():
                    freshness.append({'sourceId': ident, 'block': key, 'status': block['status'],
                                      'observedAt': block.get('observedAt'), 'url': block.get('url')})
                if not record.get('aliasOf'):
                    e.atomic_json(self.run / 'extracted' / self.c.record_path(ident).name, extracted_hints(record))
            rows.append({'sourceId': ident, 'fullName': source['fullName'], 'originalInput': original,
                         'status': status, 'storedStars': source.get('stars'), 'verifiedStars': values.get('stars'),
                         'mandatoryMissing': ';'.join(record.get('missingMandatory', [])) if record else 'not_started',
                         'replacementSourceId': self.state['replacements'].get(ident, '')})
            if record and (status not in TERMINAL or failed):
                exceptions.append({'sourceId': ident, 'fullName': source['fullName'],
                                   'missingMandatory': record.get('missingMandatory', []),
                                   'failedBlocks': failed,
                                   'identityReviewRequired': bool(identity_conflict or external_alias),
                                   'recordPath': str(self.c.record_path(ident).resolve()),
                                   'extractedPath': str((self.run / 'extracted' / self.c.record_path(ident).name).resolve())})
            if not original:
                continue
            if status == 'excluded_below_star_threshold':
                replacement = self.state['replacements'].get(ident)
                exclusions.append({'sourceId': ident, 'observedStars': values['stars'],
                                   'replacementSourceId': replacement, 'historyPath': str(self.c.record_path(ident)),
                                   'disposition': 'replaced' if replacement else 'excluded_replacement_unresolved'})
                if replacement:
                    active.append({'kind': 'verified_replacement', 'replaces': ident,
                                   'values': self.record(replacement)['values']})
            elif status != 'verified_identity_alias':
                active.append({'kind': 'verified_card' if status == 'complete_card' else 'unrefreshed_snapshot',
                               'values': values if status == 'complete_card' else source})
        field_rows = []
        for field in self.c.contract['fields']:
            counts = coverage[field['id']]
            filled = counts['observed'] + counts['derived_reviewed']
            field_rows.append({'field': field['id'], 'mandatory': field['id'] in self.c.contract['mandatory_fields'],
                               'inputRecords': len(self.original), 'filled': filled,
                               'filledPercent': round(100 * filled / len(self.original), 2) if self.original else 0,
                               **{s: counts[s] for s in ('observed', 'derived_reviewed', 'source_absent', 'not_attempted', 'fetch_error', 'budget_exhausted')}})
        report = self.run / 'reports'
        report.mkdir(exist_ok=True)
        write_csv(report / 'repository-progress.csv', rows)
        write_csv(report / 'field-completeness.csv', field_rows)
        write_csv(report / 'block-freshness.csv', freshness)
        e.atomic_json(report / 'review-queue.json', {'scope': 'exceptions_only_no_raw_readme_dump', 'items': exceptions})
        e.atomic_json(report / 'exclusion-replacements.json', {'items': exclusions, 'attempts': self.state['replacementAttempts']})
        e.atomic_json(report / 'active-candidate.json', {
            'scope': 'intermediate_mixed_projection_not_canonical_or_release',
            'containsUnrefreshedRows': any(x['kind'] == 'unrefreshed_snapshot' for x in active),
            'rows': active})
        summary = {'inputRecords': len(self.original), 'inputStates': dict(states),
                   'replacementCandidates': len(self.state['candidates']), 'resolvedReplacements': len(self.state['replacements']),
                   'cumulativeGetAttempts': self.c.state['requests'], 'cumulativeBytes': self.c.state['bytes'],
                   'retryNotBefore': self.c.state['retryNotBefore'], 'lastRateLimit': self.c.state.get('lastRateLimit'),
                   'reviewQueueSize': len(exceptions), 'LLMCalls': 0, 'canonicalWritten': False,
                   'wholeCorpusComplete': all(states[s] == 0 for s in ('not_started', 'needs_review_or_retry', 'interrupted', 'identity_review_required'))
                       and not failed_records and all(x['replacementSourceId'] for x in exclusions)}
        e.atomic_json(report / 'summary.json', summary)
        return summary


def write_csv(path, rows):
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        # Guard spreadsheet readers from formula injection in upstream strings.
        writer.writerow({k: "'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else v for k, v in row.items()})
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(buffer.getvalue(), encoding='utf-8')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'batch', 'report'])
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--pool', type=Path, action='append', help='Saved public search JSON or explicit fullName/primaryCategory seeds')
    parser.add_argument('--batch-size', type=int, default=25)
    parser.add_argument('--replacement-limit', type=int, default=3)
    args = parser.parse_args()
    with e.single_writer(args.run_dir):
        if args.mode == 'prepare':
            result = prepare(args.run_dir, args.pool if args.pool is not None else DEFAULT_POOLS,
                             args.batch_size, args.replacement_limit)
        else:
            pipeline = Pipeline(args.run_dir)
            result = pipeline.batch() if args.mode == 'batch' else pipeline.reports()
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
