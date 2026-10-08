"""Experimental selection boundaries; fake inference does not prove model quality."""
import copy
import importlib.util
from pathlib import Path
import unittest
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'flashrank_development_tests', ROOT / 'evals/plugin-v1/run_flashrank_development.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def card(repo_id):
    return {'identity': {'github_repository_id': repo_id, 'full_name': f'owner/tool{repo_id}',
                         'full_name_aliases': []},
            'descriptions': {'upstream': 'Public search library', 'catalog': 'Search tool'},
            'repository': {'topics': ['search']}, 'classifications': [{'title': 'Search'}],
            'advisory': {'use_cases': [], 'integration_surface': None, 'best_for': []}}


class Backend:
    def __init__(self, transform=None):
        self.calls = []
        self.transform = transform

    def rank(self, query, passages):
        self.calls.append((query, copy.deepcopy(passages)))
        rows = [dict(p, score=float(p['id'])) for p in passages]
        return self.transform(rows) if self.transform else rows


class FlashRankDevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.result = {'status': 'ok', 'candidates': [
            {'github_repository_id': 1, 'rrf_score': .1},
            {'github_repository_id': 2, 'rrf_score': .09}]}
        self.cards = {i: card(i) for i in (1, 2, 3)}

    def run_adapter(self, backend=None, query='Поиск библиотек'):
        return runner.rerank_pool(self.result, self.cards, query, backend or Backend())

    def test_russian_query_identity_projection_and_raw_evidence_preserved(self):
        before = copy.deepcopy((self.result, self.cards))
        backend = Backend()
        selected = self.run_adapter(backend)
        self.assertEqual(selected['ranked_ids'], [2, 1])
        self.assertEqual((self.result, self.cards), before)
        self.assertEqual(backend.calls[0][0], 'Поиск библиотек')
        self.assertEqual({p['id'] for p in backend.calls[0][1]}, {1, 2})
        self.assertEqual(selected['transport'], 'experimental_selection_adapter')
        self.assertFalse(selected['executed_c9_rrf'])
        self.assertFalse(selected['promotion_ready'])
        self.assertNotIn('rrf_score', selected)

    def test_ties_are_numeric_id_ascending(self):
        backend = Backend(lambda rows: [dict(p, score=.5) for p in reversed(rows)])
        self.assertEqual(self.run_adapter(backend)['ranked_ids'], [1, 2])

    def test_empty_result_does_not_invoke_model(self):
        self.result = {'status': 'no_match', 'candidates': []}
        backend = Backend()
        self.assertEqual(self.run_adapter(backend)['ranked_ids'], [])
        self.assertEqual(backend.calls, [])

    def test_model_may_not_append_drop_or_duplicate_ids(self):
        changes = [lambda rows: rows[:1], lambda rows: rows + [rows[0]],
                   lambda rows: [dict(rows[0], id=3), rows[1]],
                   lambda rows: [dict(rows[0], id=True), rows[1]]]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_adapter(Backend(change))

    def test_nonfinite_missing_boolean_or_string_scores_rejected(self):
        for score in (float('nan'), float('inf'), True, '.4', None):
            with self.subTest(score=score), self.assertRaises(ValueError):
                self.run_adapter(Backend(lambda rows: [dict(p, score=score) for p in rows]))

    def test_tampered_public_projection_rejected(self):
        with self.assertRaises(ValueError):
            self.run_adapter(Backend(lambda rows: [dict(p, text='changed') for p in rows]))

    def test_unavailable_duplicate_unknown_and_over_cap_input_rejected(self):
        bad = [{'status': 'index_unavailable', 'candidates': []},
               {'status': 'ok', 'candidates': [{'github_repository_id': 3}, {'github_repository_id': 3}]},
               {'status': 'ok', 'candidates': [{'github_repository_id': 4}]},
               {'status': 'ok', 'candidates': [{'github_repository_id': i} for i in range(1, 152)]}]
        for result in bad:
            self.result = result
            with self.subTest(result=result['status']), self.assertRaises(ValueError):
                self.run_adapter()

    def test_backend_failure_propagates_without_control_fallback(self):
        def fail(rows):
            raise RuntimeError('model unavailable')
        with self.assertRaisesRegex(RuntimeError, 'model unavailable'):
            self.run_adapter(Backend(fail))

    def test_invalid_or_over_budget_query_rejected_before_backend(self):
        for query in ('', None, 'x' * 8193):
            backend = Backend()
            with self.subTest(query_type=type(query)), self.assertRaises(ValueError):
                self.run_adapter(backend, query)
            self.assertEqual(backend.calls, [])

    def test_archive_ignores_mac_metadata_and_rejects_escape(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'work') as directory:
            folder = Path(directory)
            archive = folder / 'model.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                for name in runner.MODEL_FILES:
                    bundle.writestr(f'{runner.MODEL}/{name}', b'fixture')
                bundle.writestr('__MACOSX/._model', b'metadata')
                bundle.writestr(f'{runner.MODEL}/.DS_Store', b'metadata')
            runner.unpack_model_archive(archive, folder / 'safe')
            self.assertEqual({p.name for p in (folder / 'safe' / runner.MODEL).iterdir()}, runner.MODEL_FILES)
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr(f'{runner.MODEL}/../../escaped', b'bad')
            with self.assertRaises(ValueError):
                runner.unpack_model_archive(archive, folder / 'unsafe')


if __name__ == '__main__':
    unittest.main()
