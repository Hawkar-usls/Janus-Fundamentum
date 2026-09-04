import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).parents[1] / 'experiments' / 'janus_trump_r47ag_r44bw_congruence_quotient_fiber_authority.py'
spec = importlib.util.spec_from_file_location('r47ag', P)
r47ag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r47ag)


class R47AGTests(unittest.TestCase):
    def test_explicit_equality_collapse_preserves_sat(self):
        f = r47ag.canonical_formula([
            (-1, 2), (1, -2),
            (1,),
            (2, 3),
        ])
        q, cls = r47ag.exact_congruence_quotient(f)
        self.assertEqual(cls[1], cls[2])
        self.assertEqual(r47ag.exact_sat(f), r47ag.exact_sat(q))
        self.assertTrue(r47ag.exact_sat(f))

    def test_equality_plus_antiequality_stays_unsat(self):
        f = r47ag.canonical_formula([
            (-1, 2), (1, -2),
            (1, 2), (-1, -2),
        ])
        q, cls = r47ag.exact_congruence_quotient(f)
        self.assertEqual(cls[1], cls[2])
        self.assertFalse(r47ag.exact_sat(f))
        self.assertFalse(r47ag.exact_sat(q))

    def test_antiequality_is_not_misread_as_equality(self):
        f = r47ag.canonical_formula([(1, 2), (-1, -2)])
        _, cls = r47ag.exact_congruence_quotient(f)
        self.assertNotEqual(cls[1], cls[2])
        self.assertTrue(r47ag.exact_sat(f))

    def test_dense_rename_preserves_sat(self):
        f = r47ag.canonical_formula([(7,), (-7, 41), (-41, 99)])
        g = r47ag.dense_rename(f)
        self.assertEqual(r47ag.exact_sat(f), r47ag.exact_sat(g))
        self.assertEqual(r47ag.variables(g), [1, 2, 3])

    def test_generator_keeps_equality_certificates_detectable(self):
        base = r47ag.canonical_formula([(1, 2), (-1, 2)])
        f = r47ag.expand_with_certified_equalities(base, 2)
        cls = r47ag.explicit_equality_classes(f)
        self.assertEqual(cls[1], cls[3])
        self.assertEqual(cls[1], cls[5])
        self.assertEqual(cls[2], cls[4])
        self.assertEqual(cls[2], cls[6])
        self.assertEqual(r47ag.exact_sat(base), r47ag.exact_sat(f))

    def test_full_adversarial_audit(self):
        d = r47ag.audit()
        self.assertEqual(d['base_formulas'], 93)
        self.assertGreaterEqual(d['origins_checked'], 372)
        self.assertEqual(d['semantic_preservation_mismatches'], 0)
        self.assertEqual(d['mixed_sat_unsat_fibers'], 0)
        self.assertGreater(d['nontrivial_fibers'], 0)
        self.assertGreaterEqual(d['max_fiber_size'], 4)
        self.assertEqual(d['finite_falsifier_result'], 'NO_COUNTEREXAMPLE_FOUND')
        self.assertEqual(d['universal_basis'], 'TWO_DIRECTION_MODEL_PROJECTION_AND_LIFT_PROOF')
        self.assertEqual(d['SAT_semantic_authority'], 'THEOREM_AUTHORITY_GRANTED_FOR_EXACT_QUOTIENT')
        self.assertEqual(
            d['generic_SAT_algorithmic_authority'],
            'NOT_GRANTED_NO_POLYNOMIAL_DECIDER_ON_ARBITRARY_QUOTIENT',
        )
        self.assertEqual(d['P_VS_NP'], 'OPEN')
        self.assertFalse(d['TRUMP_finished'])


if __name__ == '__main__':
    unittest.main()
