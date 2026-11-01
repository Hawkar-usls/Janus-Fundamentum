#!/usr/bin/env python3
"""Falsification controls for the opt-in UFR-C023 certificate extension."""
from copy import deepcopy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments' / 'direct'))

from janus_tear_policy0a_context_obstruction import complete_width_four_core
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import canonical_cnf
from janus_ufr_001_certified_fc import UFRFCTracePolicy, replay_ufr, serialize_ufr


def renamed_twin_unsat_cnf():
    selector = 1
    clauses = [(selector,) + row for row in complete_width_four_core(1)]
    clauses += [(-selector,) + row for row in complete_width_four_core(5)]
    # Non-affine common marker prevents root affine interception.
    clauses.append((10, 11, 12))
    return canonical_cnf(clauses), 12


def rejected(cnf, count, cert):
    try:
        replay_ufr(cnf, count, cert)
    except (AssertionError, KeyError, TypeError, ValueError, IndexError):
        return True
    return False


class TestCertifiedUFR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cnf, cls.count = renamed_twin_unsat_cnf()
        cls.policy = UFRFCTracePolicy(max_candidates=720)
        cls.result, cls.root = cls.policy.solve(cls.cnf, cls.count)
        cls.cert = serialize_ufr(cls.policy, cls.root) if cls.root is not None else None

    def test_adversarial_fixture_has_real_iso_edge(self):
        self.assertIs(self.result.answer, False)
        self.assertIsNotNone(self.root)
        self.assertGreaterEqual(self.policy.iso_hits, 1, {'states': [(x['id'], x.get('branch_var'), x.get('terminal'), len(x['key'])) for x in self.policy.states.values()], 'iso_checks':self.policy.iso_checks, 'fallbacks':self.policy.iso_fallbacks, 'calls':len(self.policy.calls)})
        self.assertIs(replay_ufr(self.cnf, self.count, self.cert), False)
        self.assertEqual(
            sum(call['terminal'] == 'ISOMORPHIC_CACHE_HIT'
                for call in self.cert['calls'].values()),
            self.policy.iso_hits)

    def test_against_original_c023(self):
        baseline = FCTracePolicy()
        baseline_result, baseline_root = baseline.solve(self.cnf, self.count)
        self.assertIs(baseline_result.answer, False)
        self.assertIsNotNone(baseline_root)
        self.assertIs(verify_fc_trace(self.cnf, self.count, baseline, baseline_root), False)
        self.assertLessEqual(self.result.unique_states, baseline_result.unique_states)

    def test_corrupt_isomorphic_edge_rejected(self):
        self.assertGreaterEqual(self.policy.iso_hits, 1)
        iso_id = next(k for k, c in self.cert['calls'].items()
                      if c['terminal'] == 'ISOMORPHIC_CACHE_HIT')
        corruptions = (
            ('cache_target', -123456),
            ('renaming', ((2, 99999),)),
            ('result', True),
            ('context', (99999,)),
            ('key', ((888,),)),
            ('pre_result', ((888,),)),
        )
        for field, value in corruptions:
            with self.subTest(field=field):
                bad = deepcopy(self.cert)
                bad['calls'][iso_id][field] = value
                self.assertTrue(rejected(self.cnf, self.count, bad))
        future = deepcopy(self.cert)
        future['calls'][iso_id]['cache_target'] = max(self.cert['states'])
        # Reject forward references if the future target has not completed.
        if future['calls'][iso_id]['cache_target'] != self.cert['calls'][iso_id]['cache_target']:
            self.assertTrue(rejected(self.cnf, self.count, future))

    def test_original_verifier_still_rejects_extended_schema(self):
        # The original strict C023 replay must NOT silently accept iso edges.
        from janus_tear_policy0a_fc_serialized_verifier import replay_serialized
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
            replay_serialized(self.cnf, self.count, self.cert)

    def test_bounded_fallback_delegates_to_strict_c023(self):
        bounded = UFRFCTracePolicy(max_variables=0)
        result, root = bounded.solve(self.cnf, self.count)
        self.assertIs(result.answer, False)
        self.assertEqual(bounded.iso_hits, 0)
        self.assertIs(replay_ufr(self.cnf, self.count,
                     serialize_ufr(bounded, root)), False)


if __name__ == '__main__':
    unittest.main()
