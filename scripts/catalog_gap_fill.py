"""Fill only missing catalog values; propose low-Star replacements without swaps.

The official GitHub CLI owns credentials and REST. This module owns the catalog
gap list, checkpoint reuse, public-only selection and sparse evidence-backed edits.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import time
import urllib.parse
from collections import Counter
from pathlib import Path

import enrich_catalog as e
from catalog_refresh_pipeline import extracted_hints, write_csv
from github_cli_transport import GitHubCLITransport

UNKNOWN = {'', 'unknown', 'not available', 'not_available', 'n/a', 'noassertion', 'pending'}
FACT_FIELDS = set(e.FACTS) | {'license.spdx', 'license.name', 'license.source', 'license.confidence'}
GROUP_FIELDS = {'languages': {'languages'},
                'head_commit': {'activity.lastCommitAt', 'activity.lastCommitSha', 'activity.lastCommitBranch'},
                'release': {'activity.lastReleaseAt'}}


def replacement_candidate(item, category, language):
    text = ((item.get('full_name') or '') + ' ' + (item.get('description') or '')).lower()
    if re.search(r'awesome|curated.list|interview|list of|collection of resources', text):
        return False
    if category == 'payment_processing_sdks':
        if not re.search(r'\b(sdk|library|libraries)\b', text) or re.search(r'\b(ui|user interface|wallet|vpn|react native|android|ios)\b', text):
            return False
        family = {'JavaScript', 'TypeScript'} if language in {'JavaScript', 'TypeScript'} else {language}
        if language and item.get('language') not in family:
            return False
    return True


def get_value(row, field):
    if field in row:
        return row[field]
    value = row
    for part in field.split('.'):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def missing(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().casefold() in UNKNOWN
    if isinstance(value, (list, dict)):
        return not value or (isinstance(value, list) and all(missing(x) for x in value))
    return False  # False and zero are valid factual observations.


def targets(row, contract):
    semantic = {f['id'] for f in contract['fields'] if f['source'].startswith('curator:')}
    supported = FACT_FIELDS | set().union(*GROUP_FIELDS.values()) | semantic
    fields = {field for field in supported if missing(get_value(row, field))}
    fields.discard('secondaryCategories')  # Empty secondary membership is legitimate.
    if not missing(row.get('description')):
        fields.discard('catalogDescription')  # Do not duplicate an existing description.
    stars = row.get('stars')
    check_stars = missing(stars) or not isinstance(stars, int) or isinstance(stars, bool) or stars < 500
    groups = {group for group, keys in GROUP_FIELDS.items() if fields & keys}
    if fields & semantic or 'description' in fields:
        groups.add('readme')
    if 'stack' in fields:
        groups.add('manifests')
    return {'fields': sorted(fields), 'groups': sorted(groups), 'checkStars': check_stars,
            'semanticFields': sorted(fields & semantic), 'actionable': bool(fields or check_stars)}


def prepare(run, reuse=None):
    old_plan = e.load(reuse / 'plan.json') if reuse else None
    result = e.create_plan(run, e.ROOT / 'data/catalog_manifest.json', e.ROOT / 'specs/catalog/taxonomy.yaml',
                           e.ROOT / 'specs/catalog/enrichment-field-contract.json',
                           max_requests=old_plan['maxRequests'] if old_plan else 25000)
    if reuse:
        if old_plan['pins']['input.json']['sha256'] != result['pins']['input.json']['sha256']:
            raise ValueError('Reuse requires exactly the same input; do not silently merge snapshots')
        for name in ('records', 'curation'):
            if (reuse / name).exists():
                shutil.copytree(reuse / name, run / name)
        for name in ('checkpoint.json', 'request-log.jsonl'):
            if (reuse / name).exists():
                shutil.copy2(reuse / name, run / name)
        e.atomic_json(run / 'migration.json', {
            'sourceRun': str(reuse.resolve()), 'sourcePlanSha256': e.sha(reuse / 'plan.json'),
            'checkpointSha256BeforeAuth': e.sha(run / 'checkpoint.json'),
            'requestsAndBytesPreserved': True, 'oldPlan': old_plan,
            'scope': 'owner_authorized_auth_and_gap_only_successor_not_counter_reset'})
        for key in ('maxBytes', 'maxResponseBytes', 'timeoutSeconds', 'maxRetries', 'maxRedirects',
                    'maxManifests', 'maxSecondsPerInvocation'):
            result[key] = old_plan[key]
    result['scope'] = 'authorized_public_GET_missing_fields_only_replacements_are_proposals'
    e.atomic_json(run / 'plan.json', result)
    if reuse:
        collector = e.Collector(run)
        # Rebind derived observation timestamps to this plan. Upstream block
        # observations and factual values retain their original evidence dates.
        for ident in collector.state['records']:
            record = e.load(collector.record_path(ident))
            if not record.get('aliasOf'):
                normalized = collector.normalize(record, collector.source[ident], record.get('curation'))
                e.atomic_json(collector.record_path(ident), normalized)
        collector.verify()
    contract = e.load(run / 'field-contract.json')
    source = e.load(run / 'input.json')
    selected = {r['id']: targets(r, contract) for r in source['repositories']}
    config = {'version': 1, 'createdAt': e.now(), 'scriptSha256': e.sha(__file__),
              'transportSha256': e.sha(Path(__file__).with_name('github_cli_transport.py')),
              'collectorPlanSha256': e.sha(run / 'plan.json'),
              'sourceRun': str(reuse.resolve()) if reuse else None,
              'targets': {k: v for k, v in selected.items() if v['actionable']}}
    e.atomic_json(run / 'gap-plan.json', config)
    e.atomic_json(run / 'gap-state.json', {'processed': [], 'searches': {}, 'proposals': {}, 'verification': {}})
    return {'queuedRepositories': len(config['targets']), 'storedLowOrUnknownStars': sum(v['checkStars'] for v in selected.values()),
            'missingFields': dict(Counter(f for v in selected.values() for f in v['fields'])), 'networkPerformed': False}


class GapFill:
    def __init__(self, run, transport=None):
        self.run = Path(run)
        self.config = e.load(self.run / 'gap-plan.json')
        for field, path in [('scriptSha256', Path(__file__)),
                            ('transportSha256', Path(__file__).with_name('github_cli_transport.py')),
                            ('collectorPlanSha256', self.run / 'plan.json')]:
            if self.config[field] != e.sha(path):
                raise ValueError('Gap pipeline changed; explicit migration required')
        self.state = e.load(self.run / 'gap-state.json')
        self.c = e.Collector(self.run, transport)
        self.categories = {x['key']: x for x in e.load(self.run / 'input.json')['categories']}

    def save(self):
        e.atomic_json(self.run / 'gap-state.json', self.state)

    def preflight(self):
        # Old anonymous waiting state is retained as history, not reused as an
        # authenticated account's quota. A failed probe restores the wait.
        previous = self.c.state.get('retryNotBefore', 0)
        self.c.state.setdefault('priorAnonymousQuota', {'retryNotBefore': previous,
                                                       'lastRateLimit': self.c.state.get('lastRateLimit')})
        self.c.state['retryNotBefore'] = 0
        self.c.state.pop('haltReason', None)
        response = self.c.request(e.API + '/rate_limit')
        core = response.get('data', {}).get('resources', {}).get('core', {})
        if response['status'] != 'observed' or core.get('limit', 0) <= 60:
            self.c.state['retryNotBefore'] = max(previous, self.c.state['retryNotBefore'])
            self.c.state['haltReason'] = 'authenticated_quota_not_confirmed'
            self.c.save_state()
            raise RuntimeError('Authenticated GitHub quota was not confirmed; no anonymous collection')
        resources = response['data']['resources']
        result = {'observedAt': response['observedAt'], 'transport': 'official_github_cli',
                  'core': core, 'search': resources.get('search'), 'tokenPersisted': False}
        e.atomic_json(self.run / 'auth-preflight.json', result)
        if core.get('remaining', 0) < 50:
            self.c.state['retryNotBefore'] = core.get('reset', time.time() + 60)
        self.c.save_state()
        return result

    def process(self, ident):
        item = self.config['targets'][ident]
        record = self.c.process(ident, blocks=set(item['groups']))
        e.atomic_json(self.run / 'extracted' / self.c.record_path(ident).name, extracted_hints(record))
        if ident not in self.state['processed']:
            self.state['processed'].append(ident)
        self.save()
        return record

    def search_replacement(self, ident):
        """Search results are leads; metadata validates identity/Stars, never category fit."""
        if ident in self.state['proposals']:
            return
        row = self.c.source[ident]
        category = self.categories.get(row['primaryCategory'], {})
        searches = self.state['searches'].setdefault(ident, [])
        title = category.get('title', row['primaryCategory'])
        terms = re.sub(r'[^A-Za-z0-9 +.-]', ' ', title).split()[:4]
        keyword = ' '.join(terms)
        language = e.load(self.c.record_path(ident)).get('values', {}).get('language')
        keywords = ['topic:payments', 'topic:payment', 'payment library', 'braintree'] if row['primaryCategory'] == 'payment_processing_sdks' else [keyword, terms[0] if terms else keyword]
        queries = [k + ' in:name,description is:public stars:>=500 archived:false' for k in keywords]
        known_names = {r['fullName'].casefold() for r in self.c.source.values()}
        known_ids = {r.get('githubRepositoryId') for r in self.c.source.values() if r.get('githubRepositoryId')}
        for path in (self.run / 'records').glob('*.json'):
            record = e.load(path)
            known_ids.add(record.get('values', {}).get('githubRepositoryId'))
        candidates = {}
        for query in queries:
            cached = next((s for s in searches if s['query'] == query and s['status'] == 'observed'), None)
            if cached:
                response = cached
            else:
                url = e.API + '/search/repositories?' + urllib.parse.urlencode({'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': 30, 'page': 1})
                raw = self.c.request(url)
                response = {'query': query, 'status': raw['status'], 'observedAt': raw['observedAt'], 'url': url, 'items': [],
                            'incompleteResults': raw.get('data', {}).get('incomplete_results')}
                for item in raw.get('data', {}).get('items', []):
                    if item.get('private') is False and item.get('visibility') == 'public' and e.NAME.fullmatch(item.get('full_name', '')):
                        response['items'].append({key: item.get(key) for key in ('id', 'full_name', 'stargazers_count', 'description', 'language')})
                searches.append(response)
                self.save()
            if response['status'] != 'observed':
                return
            for item in response['items']:
                if item['full_name'].casefold() not in known_names and item['id'] not in known_ids and replacement_candidate(item, row['primaryCategory'], language):
                    candidates[item['id']] = item
            if len(candidates) >= 3:
                break
        verified = []
        for item in list(candidates.values())[:3]:
            name = item['full_name']
            response = self.state['verification'].get(name.casefold())
            if not response or response['status'] != 'observed':
                raw = self.c.request(e.API + '/repos/' + name)
                data = raw.get('data', {})
                response = {'status': raw['status'], 'observedAt': raw['observedAt'], 'url': e.API + '/repos/' + name}
                if raw['status'] == 'observed' and data.get('private') is False and data.get('visibility') == 'public':
                    response['data'] = {key: data.get(key) for key in ('id', 'full_name', 'html_url', 'stargazers_count', 'description', 'language', 'archived', 'fork')}
                self.state['verification'][name.casefold()] = response
                self.save()
            data = response.get('data', {})
            stars = data.get('stargazers_count')
            if response['status'] != 'observed':
                return
            if isinstance(stars, int) and not isinstance(stars, bool) and stars >= 500 and data.get('archived') is False and data.get('id') not in known_ids and data.get('full_name', '').casefold() not in known_names and replacement_candidate(data, row['primaryCategory'], language):
                verified.append({'fullName': data['full_name'], 'githubRepositoryId': data['id'], 'stars': stars,
                                 'description': e.clean_excerpt(data.get('description') or ''), 'url': data.get('html_url'),
                                 'language': data.get('language'), 'archived': data.get('archived'),
                                 'observedAt': response['observedAt'], 'categoryHint': row['primaryCategory'],
                                 'status': 'public_identity_and_stars_verified_fit_and_card_review_required'})
        self.state['proposals'][ident] = {'excludedFullName': row['fullName'], 'candidates': verified,
                                         'automaticReplacement': False,
                                         'status': 'review_required' if verified else 'no_candidate_in_bounded_search'}
        self.save()

    def reports(self):
        edits, review, progress = [], [], []
        outcomes = Counter()
        for ident, item in self.config['targets'].items():
            source = self.c.source[ident]
            path = self.c.record_path(ident)
            record = e.load(path) if path.exists() else None
            values = record.get('values', {}) if record else {}
            status = 'not_started'
            if record:
                status = 'evidence_available' if ident not in self.state['processed'] else 'processed'
                if values.get('identityStatus') == 'conflict':
                    status = 'identity_conflict'
                elif record['status'] == 'excluded_below_star_threshold':
                    status = 'replacement_required'
                elif any(b['status'] in ('fetch_error', 'budget_exhausted') for b in record['blocks'].values()):
                    status = 'retry_required'
                if status not in ('identity_conflict', 'replacement_required') and values.get('identityStatus') == 'resolved':
                    for field in item['fields']:
                        value = values.get(field)
                        if missing(value) or (field in item['semanticFields'] and field not in record.get('curation', {}).get('fields', {})):
                            continue
                        if field == 'stars' and not item['checkStars']:
                            continue
                        edits.append({'sourceId': ident, 'field': field, 'before': get_value(source, field),
                                      'after': value, 'evidenceArtifact': str(path.relative_to(self.run)),
                                      'scope': 'missing_value_only'})
                    if item['checkStars'] and isinstance(values.get('stars'), int) and values['stars'] >= 500 and source.get('stars') != values['stars'] and 'stars' not in item['fields']:
                        edits.append({'sourceId': ident, 'field': 'stars', 'before': source.get('stars'), 'after': values['stars'],
                                      'evidenceArtifact': str(path.relative_to(self.run)), 'scope': 'verified_low_or_unknown_star_correction'})
                if status != 'replacement_required':
                    unresolved = [f for f in item['fields'] if (f in item['semanticFields'] and f not in record.get('curation', {}).get('fields', {})) or missing(values.get(f))]
                    if unresolved:
                        review.append({'sourceId': ident, 'fields': unresolved,
                                       'evidenceArtifact': str(path.relative_to(self.run)), 'scope': 'no_automatic_semantic_acceptance'})
            outcomes[status] += 1
            progress.append({'sourceId': ident, 'fullName': source['fullName'], 'status': status,
                             'missingFields': ';'.join(item['fields']), 'checkStars': item['checkStars']})
        report = self.run / 'gap-reports'
        report.mkdir(exist_ok=True)
        e.atomic_json(report / 'patches.json', {'inputSha256': self.c.plan['pins']['input.json']['sha256'], 'canonicalWritten': False, 'edits': edits})
        e.atomic_json(report / 'review.json', {'items': review})
        e.atomic_json(report / 'replacement-proposals.json', {'items': self.state['proposals']})
        write_csv(report / 'progress.csv', progress)
        field_rows = []
        by_field = Counter(x['field'] for x in edits)
        for definition in self.c.contract['fields']:
            field = definition['id']
            empty = sum(missing(get_value(r, field)) for r in self.c.source.values())
            field_rows.append({'field': field, 'inputRows': len(self.c.source), 'missingBefore': empty,
                               'proposedEdits': by_field[field], 'notFreshnessAudit': True})
        write_csv(report / 'field-completeness.csv', field_rows)
        summary = {'scope': 'missing_fields_and_low_star_proposals_only', 'selectedRows': len(self.config['targets']),
                   'processedThisSuccessor': len(self.state['processed']), 'outcomes': dict(outcomes),
                   'proposedFieldEdits': len(edits), 'replacementLists': len(self.state['proposals']),
                   'cumulativeTransportAttempts': self.c.state['requests'], 'cumulativeBytes': self.c.state['bytes'],
                   'canonicalWritten': False, 'LLMCalls': 0}
        e.atomic_json(report / 'summary.json', summary)
        return summary

    def execute(self, max_requests=150, max_records=25):
        self.preflight()
        start = self.c.state['requests']
        original_cap = self.c.plan['maxRequests']
        self.c.plan['maxRequests'] = min(original_cap, start + max_requests)
        attempted = 0
        # Confirmed exclusions from the previous run get proposals first.
        queue = sorted(self.config['targets'], key=lambda k: (self.c.state['records'].get(k) != 'excluded_below_star_threshold', not self.config['targets'][k]['checkStars'], self.c.plan['queue'].index(k)))
        for ident in queue:
            if attempted >= max_records or self.c.state.get('haltReason') or time.time() < self.c.state['retryNotBefore'] or self.c.state['requests'] >= self.c.plan['maxRequests'] or time.monotonic() - self.c.started >= self.c.plan['maxSecondsPerInvocation']:
                break
            path = self.c.record_path(ident)
            old = e.load(path) if path.exists() else None
            failed = old and any(b['status'] in ('fetch_error', 'budget_exhausted') for b in old['blocks'].values())
            if ident in self.state['processed'] and not failed and (not old or old['status'] != 'excluded_below_star_threshold' or ident in self.state['proposals']):
                continue
            record = self.process(ident)
            attempted += 1
            if record['status'] == 'excluded_below_star_threshold' and record['values'].get('identityStatus') == 'resolved':
                self.search_replacement(ident)
        result = self.reports()
        stop = self.c.state.get('haltReason') or ('rate_limit_wait' if time.time() < self.c.state['retryNotBefore'] else
               'request_budget' if self.c.state['requests'] >= self.c.plan['maxRequests'] else
               'record_budget' if attempted >= max_records else
               'elapsed_time_budget' if time.monotonic() - self.c.started >= self.c.plan['maxSecondsPerInvocation'] else 'queue_collected_or_review_pending')
        return {**result, 'attemptedThisInvocation': attempted, 'newTransportAttempts': self.c.state['requests'] - start, 'stopReason': stop}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'preflight', 'run', 'report'])
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--reuse-run', type=Path)
    parser.add_argument('--max-requests', type=int, default=150)
    parser.add_argument('--max-records', type=int, default=25)
    args = parser.parse_args()
    if args.max_requests < 1 or args.max_records < 1:
        parser.error('Budgets must be positive')
    if args.mode == 'prepare':
        result = prepare(args.run_dir, args.reuse_run)
    else:
        with e.single_writer(args.run_dir):
            transport = GitHubCLITransport() if args.mode in ('run', 'preflight') else None
            job = GapFill(args.run_dir, transport)
            result = job.preflight() if args.mode == 'preflight' else job.reports() if args.mode == 'report' else job.execute(args.max_requests, args.max_records)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
