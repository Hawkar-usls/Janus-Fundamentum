#!/usr/bin/env python3
"""Exact source binary implication paths, parity consequence and sound abstain."""
from __future__ import annotations
import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d5_binary_scc import (
    source_proven_implied_xor,replay_equation_certificate,
    check_path_from_original,implication_graph,components,equivalence_map
)

def all_solutions(rows,n):
    for bs in itertools.product((False,True),repeat=n):
        if all(any(bs[abs(l)-1]==(l>0) for l in c) for c in rows):
            yield bs

def xor_holds(example, assignment):
    return (sum(int(assignment[v-1]) for v in example["variables"])%2)==example["rhs"]

class ImplicationSccSourceWitness(unittest.TestCase):
    def test_hidden_xor_after_positive_equivalence_with_original_source_paths(self):
        # x == y; source's 3-variable XOR clauses are split across x/y.
        # Opposite binary pair on x,y alone is already known XOR and not "new".
        rows=[(-1,2),(1,-2),(1,3,4),(-1,-3,4),(-2,3,-4),(2,-3,-4)]
        d=source_proven_implied_xor(rows,4)
        self.assertEqual(d["status"],"WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS")
        self.assertGreaterEqual(d["new_implied_XOR_equations_beyond_prior_canonical_baseline"],1)
        examples=d["sample_witnesses_original_source_replayed"]
        self.assertIn(([1,3,4],1),[(x["variables"],x["rhs"]) for x in examples])
        for cert in examples:
            self.assertTrue(replay_equation_certificate(rows,cert))
            for solution in all_solutions(rows,4):
                self.assertTrue(xor_holds(cert,solution))

    def test_hidden_xor_after_negative_equivalence(self):
        # x == not(y), ternary source XOR block split across x and y.
        rows=[(-1,-2),(1,2),(1,3,4),(-1,-3,4),(2,3,-4),(-2,-3,-4)]
        d=source_proven_implied_xor(rows,4)
        self.assertEqual(d["status"],"WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS")
        self.assertTrue(d["sample_witnesses_original_source_replayed"])
        for cert in d["sample_witnesses_original_source_replayed"]:
            self.assertTrue(replay_equation_certificate(rows,cert))
            for solution in all_solutions(rows,4):
                self.assertTrue(xor_holds(cert,solution))

    def test_only_original_xor_does_not_count_as_novel(self):
        rows=[(1,2),(-1,-2)]
        d=source_proven_implied_xor(rows,2)
        self.assertEqual(d["status"],"WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS")
        self.assertEqual(d["new_implied_XOR_equations_beyond_prior_canonical_baseline"],0)

    def test_canonical_formula_can_have_no_implications(self):
        rows=[(1,2,3),(1,-2,-3)]
        d=source_proven_implied_xor(rows,3)
        self.assertEqual(d["status"],"WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS")
        self.assertEqual(d["nontrivial_source_proven_signed_variable_aliases"],0)
        self.assertEqual(d["new_implied_XOR_equations_beyond_prior_canonical_baseline"],0)

    def test_binary_only_contradiction_fails_closed(self):
        rows=[(1,2),(1,-2),(-1,2),(-1,-2)]
        d=source_proven_implied_xor(rows,2)
        self.assertEqual(d["status"],"ABSTAIN_BINARY_ONLY_SCC_CONTRADICTION_UNCERTIFIED")
        self.assertIsNone(d["new_implied_equations"])
        self.assertEqual(d["SAT_UNSAT"],"NOT_ATTEMPTED")

    def test_forged_source_path_rejected(self):
        rows=[(-1,2),(1,-2),(1,3,4),(-1,-3,4),(-2,3,-4),(2,-3,-4)]
        d=source_proven_implied_xor(rows,4)
        example=next(x for x in d["sample_witnesses_original_source_replayed"]
                     if x["variables"]==[1,3,4])
        import copy
        forged=copy.deepcopy(example)
        witness=next(p for p in forged["substitutions"] if p["positive_original_variable"]==2)
        self.assertTrue(witness["forward"])
        witness["forward"][0][2]=3  # valid index but wrong source clause
        self.assertFalse(replay_equation_certificate(rows,forged))
        forged=copy.deepcopy(example)
        forged["original_clause_indices"][0]=200
        self.assertFalse(replay_equation_certificate(rows,forged))

    def test_random_small_original_models_entail_all_reported_new_parities(self):
        import random
        rng=random.Random(20261101057)
        for n in range(2,6):
            for i in range(20):
                rows=[tuple((v if rng.randrange(2) else -v)
                           for v in rng.sample(list(range(1,n+1)),
                                               rng.randrange(1,min(n,3)+1)))
                      for _ in range(rng.randrange(2,15))]
                d=source_proven_implied_xor(rows,n)
                self.assertIn(d["status"],(
                    "ABSTAIN_BINARY_ONLY_SCC_CONTRADICTION_UNCERTIFIED",
                    "WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS"))
                if d["status"].startswith("ABSTAIN"):continue
                for cert in d["sample_witnesses_original_source_replayed"]:
                    self.assertTrue(replay_equation_certificate(rows,cert))
                    for solution in all_solutions(rows,n):
                        self.assertTrue(xor_holds(cert,solution))

    def test_nonbinary_alias_is_not_invented(self):
        # A 3-literal implied equivalence cannot be inferred using only binary SCC.
        rows=[(-1,2,3),(1,-2,-3)]
        d=source_proven_implied_xor(rows,3)
        self.assertEqual(d["nontrivial_source_proven_signed_variable_aliases"],0)

    def test_malformed_source_abstains(self):
        for rows,n in [([(0,)],1), ([(2,)],1), ([(True,)],1),
                       ([(1,)],5001), ([(1,)]*30001,2)]:
            d=source_proven_implied_xor(rows,n)
            self.assertTrue(d["status"].startswith("ABSTAIN"))

if __name__=="__main__":unittest.main()
