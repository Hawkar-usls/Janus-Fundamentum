#!/usr/bin/env python3
"""TIME-SAT-004D6 original-resolution witness falsification and truth tables."""
from __future__ import annotations
from copy import deepcopy
import itertools
import random
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d6_bounded_resolution import source_derived_xor
from janus_time_sat_004d6_replay import replay_all
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor


def target_xor(vs,rhs,aux):
    """Each forbidden parity mask needs TWO clauses with opposite aux signs."""
    rows=[]
    for bits in itertools.product((0,1),repeat=len(vs)):
        if sum(bits)%2==rhs:continue
        core=tuple((-v if b else v) for v,b in zip(vs,bits))
        rows.extend([core+(aux,),core+(-aux,)])
    return rows


def models(rows,n):
    for bits in itertools.product((False,True),repeat=n):
        if all(any(bits[abs(v)-1]==(v>0) for v in c) for c in rows):
            yield bits


def satisfies(clause,bits):
    return any(bits[abs(l)-1]==(l>0) for l in clause)


class BoundedResolution(unittest.TestCase):
    def test_hidden_ternary_xor_from_auxiliary_resolution(self):
        source=target_xor([1,2,3],1,4)
        prior=extract_paged_mixed_xor(source,4)
        self.assertEqual(prior["complete_xor_equation_count"],0)
        evidence=source_derived_xor(source,4)
        self.assertEqual(evidence["status"],"SOURCE_RESOLUTION_BOUNDED_PASS")
        self.assertGreater(evidence["total_new_resolvents"],0)
        self.assertGreaterEqual(evidence["new_complete_xor_sign_mask_equations"],1)
        self.assertTrue(replay_all(source,4,evidence))
        self.assertIn(([1,2,3],1),
                      [(x["variables"],x["rhs"]) for x in evidence["new_witness_examples"]])
        valid=list(models(source,4))
        self.assertGreater(len(valid),0)
        for x in evidence["new_witness_examples"]:
            self.assertTrue(any(i>=len(source) for i in x["clause_ids"]))
            for bits in valid:
                self.assertEqual(sum(bits[i-1] for i in x["variables"])%2,x["rhs"])

    def test_source_model_entails_every_resolution_step(self):
        source=target_xor([1,2,3],0,4)+[(1,5),(-3,5)]
        output=source_derived_xor(source,5)
        self.assertTrue(replay_all(source,5,output))
        satisfying=list(models(source,5))
        self.assertGreater(len(satisfying),0)
        for proof in output["resolution_proof_DAG"]:
            for bitset in satisfying:
                self.assertTrue(satisfies(proof["clause"],bitset))

    def test_source_synthetic_proof_tampering_detected(self):
        source=target_xor([1,2,3],1,4)
        output=source_derived_xor(source,4)
        self.assertTrue(replay_all(source,4,output))
        forged=deepcopy(output)
        forged["resolution_proof_DAG"][0]["clause"][0]*=-1
        self.assertFalse(replay_all(source,4,forged))
        forged=deepcopy(output)
        forged["resolution_proof_DAG"][0]["pivot"]=3
        self.assertFalse(replay_all(source,4,forged))
        forged=deepcopy(output)
        forged["resolution_proof_DAG"][0]["parents"][0]=len(source)+1000
        self.assertFalse(replay_all(source,4,forged))
        forged=deepcopy(output)
        forged["new_witness_examples"][0]["clause_ids"][0]=len(source)+1000
        self.assertFalse(replay_all(source,4,forged))
        forged=deepcopy(output)
        forged["new_complete_xor_sign_mask_equations"]+=1
        self.assertFalse(replay_all(source,4,forged))

    def test_incomplete_parity_source_does_not_invent_xor(self):
        source=target_xor([1,2,3],1,4)[:-1]
        result=source_derived_xor(source,4)
        self.assertTrue(replay_all(source,4,result))
        self.assertNotIn(([1,2,3],1),
                         [(x["variables"],x["rhs"]) for x in result["new_witness_examples"]])

    def test_random_small_soundness_with_full_truth_tables(self):
        rng=random.Random(20261102006)
        for n in range(2,6):
            for rep in range(12):
                source=[]
                for i in range(rng.randrange(2,16)):
                    vs=rng.sample(range(1,n+1),rng.randrange(1,min(n,4)+1))
                    source.append(tuple(v if rng.randrange(2) else -v for v in vs))
                result=source_derived_xor(source,n)
                self.assertTrue(replay_all(source,n,result))
                for assignment in models(source,n):
                    for step in result["resolution_proof_DAG"]:
                        self.assertTrue(satisfies(step["clause"],assignment))
                    for cert in result["new_witness_examples"]:
                        self.assertEqual(sum(assignment[v-1] for v in cert["variables"])%2,
                                         cert["rhs"])

    def test_invalid_source_fails_closed(self):
        for rows,n in [([(0,)],1), ([(True,)],1), ([(3,)],2),
                       ([(1,)],0), ([(1,)],5001), ([(1,)]*30001,1)]:
            x=source_derived_xor(rows,n)
            self.assertTrue(x["status"].startswith("ABSTAIN"))

    def test_tautology_and_duplicate_does_not_forge_parity(self):
        rows=[(1,-1),(1,1),(1,2),(-1,-2),(1,2)]
        result=source_derived_xor(rows,2)
        self.assertTrue(replay_all(rows,2,result))
        self.assertEqual(result["new_complete_xor_sign_mask_equations"],0)

    def test_no_alias_required_synthetic_positive(self):
        from janus_time_sat_004d5_binary_scc import source_proven_implied_xor
        source=target_xor([1,2,3],1,4)
        scc=source_proven_implied_xor(source,4)
        self.assertEqual(scc["nontrivial_source_proven_signed_variable_aliases"],0)
        self.assertEqual(scc["new_implied_XOR_equations_beyond_prior_canonical_baseline"],0)
        result=source_derived_xor(source,4)
        self.assertGreater(result["new_complete_xor_sign_mask_equations"],0)

if __name__=="__main__":
    unittest.main()
