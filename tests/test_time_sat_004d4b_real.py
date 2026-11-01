#!/usr/bin/env python3
"""TIME-SAT-004D4B: frozen original metadata and mixed partition no-loss tests."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d4b_real_pilot import (
    ARMS,REPEATS,CPU,WALL,AS_BYTES,frozen_sources,original_model_replay
)
from janus_time_sat_004d4_mixed_xor import (
    extract_mixed_xor,representation_satisfied
)

def parity(vars_,rhs):
    return [tuple(-v if mask>>i&1 else v for i,v in enumerate(vars_))
            for mask in range(1<<len(vars_)) if (mask.bit_count()&1)!=rhs]

class FourPublicMixedTests(unittest.TestCase):
    def test_frozen_exact_four_source_hashes(self):
        x=frozen_sources()
        self.assertEqual(len(x),4)
        self.assertEqual([c["GBD_id_NOT_SHA256"] for c in x],[
            "247e42e46495f1c4b8707e497af8c93e",
            "1707c4c24e66b2cfe6c03955b638bebf",
            "16ca57f2cdffd5b0260fc771017e1f04",
            "7db30d12cb06f0dc2f30abff80d96d6a"])
        for c in x:
            self.assertEqual(len(c["decoded_CNF_SHA256"]),64)
            self.assertEqual(len(c["original_transfer_SHA256"]),64)

    def test_true_mixed_sources_only_proven_xor_removed(self):
        source=parity([1,2,3],0)+[(2,4),(-4,5)]
        p=extract_mixed_xor(source,5)
        self.assertEqual(p["status"],"SOURCE_PARTITION_VERIFIED")
        self.assertEqual(p["complete_xor_equation_count"],1)
        self.assertEqual(p["source_xor_clauses"],4)
        self.assertEqual(p["source_residual_clauses"],2)
        self.assertEqual(sorted(p["xor_source_clause_indices"]+
                                p["residual_source_clause_indices"]),
                         list(range(len(source))))
        for mask in range(1<<5):
            values={i+1:bool(mask>>i&1) for i in range(5)}
            direct=all(any(values[abs(l)]==(l>0) for l in c)
                       for c in source)
            self.assertEqual(direct,representation_satisfied(p,values))

    def test_no_xor_and_duplicates_never_disappear(self):
        original=[(1,2,3),(2,-3,4),(1,-1),()]
        p=extract_mixed_xor(original,4)
        self.assertEqual(p["status"],"SOURCE_PARTITION_VERIFIED")
        self.assertEqual(p["complete_xor_equation_count"],0)
        self.assertEqual(p["source_residual_clauses"],4)

    def test_original_model_replay_rejects_forged_assignments(self):
        source=[(1,2),(-2,3)]
        self.assertTrue(original_model_replay(source,3,[1,2,3]))
        self.assertFalse(original_model_replay(source,3,[-1,-2,3]))
        self.assertFalse(original_model_replay(source,3,[1,2]))
        self.assertFalse(original_model_replay(source,3,[1,2,2]))

    def test_cost_and_engine_contract_frozen(self):
        self.assertEqual((REPEATS,CPU,WALL,AS_BYTES),(2,8,11,2_147_483_648))
        self.assertEqual(ARMS,("janus_mixed_native_xor",
                               "cryptominisat_original_cnf",
                               "cadical195_original_cnf"))

if __name__=="__main__":unittest.main()
