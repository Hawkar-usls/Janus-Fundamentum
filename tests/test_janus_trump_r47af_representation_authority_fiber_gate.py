import importlib.util
from pathlib import Path
import unittest


P = Path(__file__).resolve().parents[1] / 'experiments' / 'janus_trump_r47af_representation_authority_fiber_gate.py'
spec = importlib.util.spec_from_file_location('r47af', P)
r47af = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r47af)


class TestR47AFFiberAuthority(unittest.TestCase):
    def test_clv_explicit_collision(self):
        sat_f = r47af.canonical_formula(((1,), (2,), (1, 2)))
        unsat_f = r47af.canonical_formula(((1,), (-1,), (1, 2)))
        self.assertEqual(r47af.clv_representation(sat_f), (3, 4, 2))
        self.assertEqual(r47af.clv_representation(unsat_f), (3, 4, 2))
        self.assertTrue(r47af.exact_sat(sat_f))
        self.assertFalse(r47af.exact_sat(unsat_f))

    def test_generic_falsifier_finds_lossy_fiber(self):
        domain = list(r47af.finite_formula_domain())
        collision = r47af.find_fiber_collision(domain, r47af.clv_representation)
        self.assertTrue(collision['found'])
        self.assertNotEqual(collision['sat_a'], collision['sat_b'])

    def test_identity_positive_control_has_no_collision(self):
        domain = list(r47af.finite_formula_domain())
        collision = r47af.find_fiber_collision(domain, r47af.exact_representation)
        self.assertFalse(collision['found'])

    def test_firewalls(self):
        d = r47af.audit()
        self.assertEqual(d['negative_control']['verdict'], 'QUARANTINED_INSUFFICIENT_REPRESENTATION')
        self.assertEqual(d['positive_control']['SEMANTIC_AUTHORITY'], 'GRANTED_FOR_IDENTITY_CONTROL')
        self.assertTrue(d['positive_control']['ALGORITHMIC_AUTHORITY'].startswith('NOT_GRANTED'))
        self.assertEqual(d['UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE'], 'OPEN')
        self.assertEqual(d['SAT_IN_P'], 'NOT_PROVED')
        self.assertEqual(d['P_VS_NP'], 'OPEN')
        self.assertFalse(d['TRUMP_finished'])


if __name__ == '__main__':
    unittest.main()
