import importlib.util
import unittest
from itertools import combinations
from pathlib import Path

P = Path(__file__).parents[1] / 'experiments' / 'janus_trump_r44cf_blackbox_polynomial_lift_or_generic_3color_solver.py'
spec = importlib.util.spec_from_file_location('r44cf', P)
r44cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44cf)


class R44CFTests(unittest.TestCase):
    def test_size_accounting(self):
        self.assertEqual(r44cf.image_size(5, 7), {'variables': 15, 'target_clauses': 27, 'source_clauses': 62, 'total_clauses': 89})

    def test_triangle_yes_k4_no(self):
        triangle = [(0,1),(1,2),(0,2)]
        k4 = list(combinations(range(4), 2))
        self.assertTrue(r44cf.blackbox_lift_decision(3, triangle, r44cf.exact_transport_decider_for_audit))
        self.assertFalse(r44cf.blackbox_lift_decision(4, k4, r44cf.exact_transport_decider_for_audit))

    def test_polynomial_exponent_lifts(self):
        for k in range(9):
            self.assertTrue(r44cf.polynomial_lift_certificate(k)['polynomial_preserved_under_composition'])

    def test_finite_audit_and_firewalls(self):
        d = r44cf.audit(4)
        self.assertEqual(d['universal_statement'], 'IF_R44CC_IMAGE_GLOBAL_TRANSPORT_IN_P_THEN_GRAPH_3COLOR_IN_P')
        self.assertEqual(d['polynomial_transport_solver_exists'], 'NOT_PROVED')
        self.assertEqual(d['generic_polynomial_3color_solver_exists'], 'NOT_PROVED')
        self.assertFalse(d['additional_polynomial_invariant_ruled_out'])
        self.assertFalse(d['TRUMP_finished'])
        self.assertEqual(d['SAT_IN_P'], 'NOT_PROVED')
        self.assertEqual(d['P_VS_NP'], 'OPEN')


if __name__ == '__main__':
    unittest.main()
