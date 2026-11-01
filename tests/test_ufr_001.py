#!/usr/bin/env python3
"""Independent falsification-oriented tests of the proposed UFR mapping."""
import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments' / 'direct'))
from janus_ufr_001 import (canonicalize, find_verified_match, normalize,
                           structural_signature,
                           transport_model, verify_model, verify_renaming)


def brute(rows, kind):
    source = normalize(rows)
    vs = sorted({abs(lit) for row in source for lit in row})
    for bits in itertools.product((False, True), repeat=len(vs)):
        model = dict(zip(vs, bits))
        if verify_model(source, model, kind):
            return model
    return None


class TestUFR(unittest.TestCase):
    def test_handpicked_positive_and_negative(self):
        a = ((1, -2), (2, 3), (-1, -3))
        b = ((7, -5), (5, 11), (-7, -11))
        m = find_verified_match(a, b)
        self.assertIsNotNone(m)
        self.assertTrue(verify_renaming(a, b, m))
        self.assertIsNone(find_verified_match(a, ((7, 5), (5, 11), (-7, -11))))
        self.assertFalse(verify_renaming(a, b, {1: 7, 2: 7, 3: 11}))
        self.assertFalse(verify_renaming(a, b, {1: 7, 2: 5}))
        self.assertRaises(ValueError, canonicalize, ((0,),))

    def test_exact_one_multiplicity_and_empty(self):
        self.assertFalse(verify_model(((1, 1),), {1: False}, 'EXACT_ONE'))
        self.assertFalse(verify_model(((1, 1),), {1: True}, 'EXACT_ONE'))
        self.assertTrue(verify_model(((1, -1),), {1: True}, 'EXACT_ONE'))
        self.assertFalse(verify_model(((),), {}, 'SAT'))
        self.assertFalse(verify_model(((),), {}, 'EXACT_ONE'))
        self.assertIsNotNone(find_verified_match(((1, 1, -2),), ((9, 9, -8),), 'EXACT_ONE'))
        self.assertIsNone(find_verified_match(((1, 1),), ((9,),), 'EXACT_ONE'))

    def test_limited_fallback_is_sound(self):
        a = ((1, 2, 3), (-1, -2, -3))
        ca = canonicalize(a, max_candidates=1)
        self.assertFalse(ca.exhaustive)
        self.assertTrue(verify_renaming(a, ca.key, ca.mapping()))

    def test_random_relabelings_and_models_both_kinds(self):
        random_gen = random.Random(20261101)
        for kind in ('SAT', 'EXACT_ONE'):
            for n in (1, 2, 3, 4, 5, 6):
                for _ in range(45):
                    rows = tuple(tuple(random_gen.choice((-1, 1)) * random_gen.randrange(1, n + 1)
                                       for _ in range(random_gen.randrange(1, 4)))
                                 for _ in range(random_gen.randrange(1, 8)))
                    # Unused variables are irrelevant to the formal match.
                    names = sorted({abs(l) for r in rows for l in r})
                    targets = random_gen.sample(range(20, 100), len(names))
                    mapping = dict(zip(names, targets))
                    transformed = tuple(tuple((1 if l > 0 else -1) * mapping[abs(l)] for l in row)
                                        for row in rows)
                    can = canonicalize(rows, kind)
                    self.assertTrue(verify_renaming(rows, can.key, can.mapping(), kind))
                    self.assertEqual(
                        structural_signature(normalize(rows)),
                        structural_signature(normalize(transformed)),
                        (kind, rows, transformed))
                    match = find_verified_match(rows, transformed, kind)
                    self.assertIsNotNone(match, (kind, rows, transformed))
                    self.assertTrue(verify_renaming(rows, transformed, match, kind))
                    model = brute(rows, kind)
                    target_model = brute(transformed, kind)
                    self.assertEqual(model is None, target_model is None)
                    if model is not None:
                        mapped_model = transport_model(model, match)
                        self.assertTrue(verify_model(transformed, mapped_model, kind))

    def test_c023_canonical_fast_path_identical_to_full_normalization(self):
        from janus_tear_policy0a_masked_tseitin import canonical_cnf
        rng = random.Random(20261101)
        for n in range(1, 9):
            for case in range(25):
                raw = [tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                             for _ in range(rng.randint(0, 4)))
                       for _ in range(rng.randint(1, 18))]
                cnf = canonical_cnf(raw)
                for budget in (1, 120, 720):
                    ref = canonicalize(cnf, max_candidates=budget)
                    fast = canonicalize(cnf, max_candidates=budget,
                                        already_c023_cnf=True)
                    self.assertEqual(ref, fast, (n, case, budget))
                    self.assertTrue(verify_renaming(cnf, fast.key,
                                                     fast.mapping(), 'SAT'))

    def test_distinct_shapes_cannot_collide(self):
        self.assertNotEqual(canonicalize(((1, 2), (2, 3))).key,
                            canonicalize(((1, 2), (2, -3))).key)
        self.assertIsNone(find_verified_match(((1, 2),), ((1, -2), (3,))))
        with self.assertRaises(ValueError):
            canonicalize(((1,),), 'NOT_A_KIND')


if __name__ == '__main__':
    unittest.main()
