"""Development request envelope; never changes C9 pins or treats unknowns as fit.

Codex/interview supplies structured exclusions and unresolved decisions. This
boundary validates that interpretation; it is not a natural-language parser.
Dependency evidence describes documented configuration alternatives, not all
possible integrations. Missing evidence always remains unknown.
"""
from __future__ import annotations

SCHEMA = 'cp04_recommendation_request_v1'


def prepare(query, intent, *, excluded_repository_ids=(), excluded_dependencies=(), unresolved=()):
    ids = list(excluded_repository_ids)
    dependencies = list(excluded_dependencies)
    if any(type(i) is not int or i <= 0 for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('invalid repository exclusions')
    if any(not isinstance(s, str) or not s.strip() or s != s.casefold().strip() for s in dependencies):
        raise ValueError('dependencies must be normalized names')
    if len(dependencies) != len(set(dependencies)) or (query is not None and len(ids) > query['max_candidates']) or len(dependencies) > 16:
        raise ValueError('exclusion budget exceeded')
    if any(set(d) != {'dimension', 'question', 'options'} or not d['question'] or len(d['options']) < 2 for d in unresolved):
        raise ValueError('invalid unresolved decision')
    if not unresolved and (not isinstance(query, dict) or not isinstance(intent, dict)):
        raise ValueError('resolved request needs query and intent')
    return dict(schema_version=SCHEMA, status='needs_clarification' if unresolved else 'ready',
                catalog_query=query, intent=intent,
                exclusions=dict(repository_ids=ids, dependencies=dependencies),
                unresolved=list(unresolved))


def select(request, ranked_ids, evidence, *, limit):
    """Preserve surviving order, refill from the ranked pool, annotate unknowns."""
    if request['schema_version'] != SCHEMA or type(limit) is not int or limit < 1:
        raise ValueError('invalid selection request')
    if request['status'] == 'needs_clarification':
        return dict(status='needs_clarification', selected_ids=[], questions=request['unresolved'])
    if len(ranked_ids) != len(set(ranked_ids)):
        raise ValueError('duplicate ranked identity')
    product_ids = set(request['exclusions']['repository_ids'])
    dependencies = set(request['exclusions']['dependencies'])
    kept, excluded, unknown, conditional = [], [], [], []
    for rid in ranked_ids:
        if rid in product_ids:
            excluded.append(dict(github_repository_id=rid, reason='explicit_product_exclusion', source_urls=[]))
            continue
        if dependencies:
            fact = evidence.get(rid)
            if fact is None:
                unknown.append(rid)
            else:
                if not fact.get('source_urls') or not fact.get('alternatives'):
                    raise ValueError('unsourced or incomplete dependency fact')
                modes = fact['alternatives']
                if any(not isinstance(m, list) or any(not isinstance(d, str) for d in m) for m in modes):
                    raise ValueError('invalid deployment alternatives')
                if all(dependencies.intersection(mode) for mode in modes):
                    excluded.append(dict(github_repository_id=rid, reason='documented_dependency_conflict', source_urls=fact['source_urls']))
                    continue
                # An available configuration is not proof of the actual integration.
                conditional.append(rid)
                unknown.append(rid)
        kept.append(rid)
    selected = kept[:limit]
    return dict(status='ready', selected_ids=selected, excluded=excluded,
                verification_required=[r for r in unknown if r in selected],
                conditional_configuration_ids=[r for r in conditional if r in selected])


def execute(request, retrieve, evidence, *, limit):
    """Do not retrieve or build a pack until material decisions are resolved."""
    if request['status'] == 'needs_clarification':
        return select(request, [], evidence, limit=limit)
    return select(request, retrieve(), evidence, limit=limit)
