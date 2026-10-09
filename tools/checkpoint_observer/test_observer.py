import unittest
from unittest.mock import patch
import observer

class ObserverTests(unittest.TestCase):
    def test_scope(self):
        self.assertTrue(observer.relevant('research/R5_E120_NEW.md'))
        self.assertTrue(observer.relevant('registry/TRUMP_CURRENT_STATE.json'))
        self.assertFalse(observer.relevant('docs/marketing.md'))
        self.assertFalse(observer.relevant('experiments/r5_e120.py'))

    def test_claims_do_not_promote_proof(self):
        with patch('observer.source', return_value='P=NP PROVED\nGate: PASSED\nheuristic proof'):
            r = observer.record('a', 'b', ['research/R5_E120.md'], [])
        self.assertEqual(r['p_vs_np'], 'OPEN')
        self.assertEqual(r['independent_proof_verification'], 'NOT_PERFORMED')
        self.assertIn('NO_RUN_ON_EXACT_COMMIT', observer.render(r))

    def test_deletion_is_not_retraction(self):
        with patch('observer.source', side_effect=[None, 'Gate: FAILED']):
            r = observer.record('a', 'b', ['research/R5_E120.md'], [])
        self.assertEqual(r['files'][0]['change'], 'deleted')
        self.assertEqual(r['scientific_delta'], 'REQUIRES_SCIENTIFIC_REVIEW')
        self.assertTrue(r['files'][0]['previous_source_reported_excerpts'])

if __name__ == '__main__':
    unittest.main()

class CatchupTests(unittest.TestCase):
    def test_all_commits_and_delayed_ci(self):
        import tempfile
        import subprocess
        import os
        import sys
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = os.getcwd()
            os.chdir(root)
            try:
                def g(*a):
                    return subprocess.check_output(['git', *a], text=True, stderr=subprocess.DEVNULL).strip()
                g('init'); g('config', 'user.name', 'Test'); g('config', 'user.email', 'test@example.invalid')
                g('commit', '--allow-empty', '-m', 'baseline')
                baseline = g('rev-parse', 'HEAD')
                (root / 'research').mkdir()
                shas = []
                for i in range(2):
                    (root / f'research/R5_E{i}.md').write_text(f'Gate: OPEN\nObservation {i}')
                    g('add', 'research'); g('commit', '-m', 'checkpoint')
                    shas.append(g('rev-parse', 'HEAD'))
                g('update-ref', 'refs/remotes/origin/main', shas[-1])
                state = root / 'state'
                with patch.object(observer, 'BASELINE', baseline), patch.object(sys, 'argv', ['observer', '--state-dir', str(state)]), patch.object(observer, 'runs', return_value=[]):
                    observer.main(); observer.main()
                import json
                manifest = json.loads((state / 'manifest.json').read_text())
                self.assertEqual(manifest['reports'], shas)
                saved = (state / 'manifest.json').read_text()
                with patch.object(sys, 'argv', ['observer', '--state-dir', str(state)]), patch.object(observer, 'runs', side_effect=RuntimeError('API unavailable')):
                    with self.assertRaises(RuntimeError):
                        observer.main()
                self.assertEqual((state / 'manifest.json').read_text(), saved)
                ci = [{'id': 1, 'attempt': 1, 'name': 'R5 Frontier Verification', 'status': 'completed', 'conclusion': 'success', 'url': 'https://example.invalid', 'head_sha': shas[0]}]
                with patch.object(sys, 'argv', ['observer', '--state-dir', str(state)]), patch.object(observer, 'runs', side_effect=lambda sha: ci if sha == shas[0] else []):
                    observer.main()
                self.assertEqual(json.loads((state / f'{shas[0]}.json').read_text())['r5_runs_exact_commit'], ci)
            finally:
                os.chdir(old)
