#!/usr/bin/env python3
"""NOVIKOV-002: independent falsification of bounded partial-state consistency."""
from __future__ import annotations
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_novikov_002 import (
    UNSET, MAX_VARIABLES, Meter, propagate, _exact_one_forces,
    search, independently_model, validated,
)
from janus_ufr_001 import normalize, verify_model
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from time import perf_counter


def independent_truth(rows,n,kind):
    clean=normalize(rows)
    return [x for x in range(1<<n) if verify_model(clean,{
        v:bool(x & (1<<(v-1))) for v in range(1,n+1)},kind)]


def meter():
    return Meter(20000,1000000,perf_counter()+15)


class PartialConsistencyTests(unittest.TestCase):
    def test_failed_literal_forces_before_complete_model(self):
        rows=((-1,2),(-1,-2),(1,3))
        clean=validated(rows,3,"SAT")
        partial=[UNSET]*3
        self.assertTrue(propagate(clean,partial,"SAT",meter()))
        self.assertEqual(partial,[UNSET]*3)
        base=search(rows,3,policy="unit")
        look=search(rows,3,policy="lookahead",probe_width=2)
        self.assertEqual(base.status,look.status)
        self.assertEqual(look.status,"SAT")
        self.assertGreater(look.failed_literal_probes,0)
        self.assertGreater(look.rejected_probe_branches,0)
        self.assertTrue(look.model_independently_verified)

    def test_exact_one_repeated_and_opposite_literal_semantics(self):
        for row, expected in [
            ((1,1),[]),
            ((1,-1),[0,1]),
            ((1,1,-2),[0]),
            ((1,1,1),[]),
            ((1,-1,2),[0,1]),
        ]:
            with self.subTest(row=row):
                real=[x for x in range(4) if independently_model((row,),2,"EXACT_ONE",x)]
                # Do not trust handwritten expected for this negative-control
                # test: independently verify literal multiplicity.
                self.assertEqual(real,expected)
                result=search((row,),2,"EXACT_ONE",policy="lookahead")
                self.assertEqual(result.status,"SAT" if expected else "UNSAT")
                if result.status=="SAT":
                    self.assertIn(result.model,expected)
                else:
                    self.assertTrue(result.unsat_independent_exhaustive_check)

    def test_random_sat_and_exact_one_are_complete_vs_independent_truth(self):
        rng=random.Random(20261101)
        counts=0
        for kind in ("SAT","EXACT_ONE"):
            for n in range(2,9):
                for _ in range(25):
                    rows=tuple(tuple(
                        rng.choice((-1,1))*rng.randint(1,n)
                        for __ in range(rng.randint(0,5)))
                        for ___ in range(rng.randint(0,10)))
                    truth=independent_truth(rows,n,kind)
                    for policy in ("unit","lookahead"):
                        result=search(rows,n,kind,policy=policy,probe_width=2,
                                      max_nodes=10000,max_visits=400000,seconds=3.0)
                        self.assertEqual(result.status,"SAT" if truth else "UNSAT")
                        self.assertEqual(result.model in truth,bool(truth))
                        self.assertTrue(
                            result.model_independently_verified if truth
                            else result.unsat_independent_exhaustive_check)
                        self.assertGreater(len(result.source_sha256),60)
                        counts+=1
        self.assertEqual(counts,700)

    def test_small_exhaustive_propagation_sound_on_every_partial_state(self):
        rng=random.Random(202611011)
        for kind in ("SAT","EXACT_ONE"):
            for n in range(2,5):
                for _ in range(18):
                    rows=tuple(tuple(rng.choice((-1,1))*rng.randint(1,n)
                                     for __ in range(rng.randint(0,5)))
                                for ___ in range(rng.randint(0,7)))
                    clean=validated(rows,n,kind)
                    for trit in range(3**n):
                        seed=[]
                        t=trit
                        for _ in range(n):
                            seed.append((UNSET,0,1)[t%3])
                            t//=3
                        assignments=[
                            x for x in independent_truth(rows,n,kind)
                            if all(bit==UNSET or bit==((x>>i)&1)
                                   for i,bit in enumerate(seed))
                        ]
                        projected=seed[:]
                        valid=propagate(clean,projected,kind,meter())
                        # Local consistency is necessary but not sufficient:
                        # an impossible partial state can remain locally supported.
                        if assignments:
                            self.assertTrue(valid)
                            for x in assignments:
                                self.assertTrue(all(bit==UNSET or bit==((x>>i)&1)
                                            for i,bit in enumerate(projected)))

    def test_adversarial_false_hints_do_not_affect_correctness(self):
        # Probing is not permitted to use a promised future complete model.
        for kind,rows,n in (
            ("SAT",((1,),(-1,)),3),
            ("SAT",((1,2),(-1,-2)),3),
            ("EXACT_ONE",((1,1),(1,-1)),3),
            ("EXACT_ONE",((1,-1),),3),
        ):
            expected=bool(independent_truth(rows,n,kind))
            for policy in ("unit","lookahead"):
                observed=search(rows,n,kind,policy=policy)
                self.assertEqual(observed.status=="SAT",expected)

    def test_budget_exhaustion_is_unknown_not_unsat(self):
        # n=240 with no constraints has 2^240 candidate assignments but
        # very shallow SAT branch path. A one-node budget must be UNKNOWN.
        for policy in ("unit","lookahead"):
            x=search((),240,policy=policy,max_nodes=1,max_visits=20,seconds=1)
            self.assertEqual(x.status,"UNKNOWN")
            self.assertEqual(x.certificate_status,"UNKNOWN_RESOURCE_LIMIT")
            self.assertIsNone(x.model)
        with self.assertRaises(ValueError):
            search(((241,),),240)
        with self.assertRaises(ValueError):
            search(((0,),),3)
        with self.assertRaises(ValueError):
            search(((1,),),241)
        with self.assertRaises(ValueError):
            search(((1,),),3,max_nodes=0)
        with self.assertRaises(ValueError):
            search(((1,),),3,probe_width=100)
        with self.assertRaises(ValueError):
            search(((1,),),3,policy="oracle_says_unsat")

    def test_maj3_k4_real_formula_resource_capped_and_separate_proof(self):
        rows,n=maj3_lifted_tseitin_cnf(4,K4_EDGES)
        self.assertEqual((n,len(rows)),(18,1024))
        results=[]
        for policy in ("unit","lookahead"):
            r=search(rows,n,policy=policy,max_nodes=120,
                     max_visits=100000,seconds=5)
            self.assertIn(r.status,("UNSAT","UNKNOWN"))
            self.assertFalse(r.model_independently_verified)
            self.assertFalse(r.unsat_independent_exhaustive_check)
            self.assertIn(r.certificate_status,(
                "UNKNOWN_RESOURCE_LIMIT","DPLL_UNSAT_NO_PORTABLE_PROOF"))
            results.append(r)
        self.assertEqual(results[0].source_sha256,results[1].source_sha256)


if __name__=="__main__":
    unittest.main()
