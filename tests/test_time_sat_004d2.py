"""TIME-SAT-004D2: independent original CNF replay and specialized baselines."""
from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d2_compare import (
    ARMS,CPU_LIMIT,RAM_LIMIT,SOURCE_SHA,full_verify,run_one,verify_source
)
from janus_time_sat_004d1_xor import group_parity_equations,check_original_cnf

def enc(v,rhs):
    return [tuple(-x if mask>>i&1 else x for i,x in enumerate(v))
            for mask in range(1<<len(v)) if (mask.bit_count()&1)!=rhs]

class Compare004D2Tests(unittest.TestCase):
    def test_same_external_original_sha_and_all_original_source_clauses(self):
        f=Path("experiments/time_sat_004_external/lightsout_01d6fa8_verified/original.cnf")
        original=verify_source(f)
        self.assertEqual(len(original),9216)
        self.assertEqual(sum(len(r) for r in original),45312)
        x=group_parity_equations(original,625)
        self.assertEqual(x["status"],"EXACT_XOR_COVER_PASS")
        self.assertEqual(len(x["equations"]),625)
        self.assertEqual(full_verify(original,625,{k:False for k in range(1,626)}),
                         check_original_cnf(original,625,0))

    def test_all_specialized_paths_agree_on_synthetic_XOR_and_verify_source(self):
        from pycryptosat import Solver
        from pysat.solvers import Solver as PySolver
        rng=random.Random(202611010422)
        for _ in range(10):
            n=5
            eq=[(rng.sample(range(1,n+1),rng.randrange(2,5)),rng.randrange(2))
                for i in range(4)]
            rows=[c for variables,rhs in eq for c in enc(variables,rhs)]
            cover=group_parity_equations(rows,n)
            self.assertEqual(cover["status"],"EXACT_XOR_COVER_PASS")
            a=Solver(threads=1)
            for x in cover["equations"]:
                a.add_xor_clause(list(x["variables"]),bool(x["rhs"]))
            result,assignment=a.solve()
            with PySolver(name="cadical195",bootstrap_with=rows) as b:
                other=b.solve()
            self.assertEqual(result,other)
            if result:
                self.assertTrue(full_verify(rows,n,{i:assignment[i] for i in range(1,n+1)}))

    def test_crypto_CNF_vs_direct_XOR_on_actual_CNF(self):
        source=verify_source(Path("experiments/time_sat_004_external/lightsout_01d6fa8_verified/original.cnf"))
        for arm in ("janus_gf2","cryptominisat_native_xor","cryptominisat_original_cnf"):
            with self.subTest(arm=arm):
                got=run_one(arm,source)
                self.assertEqual(got["verdict"],"SAT_ORIGINAL_CNF_INDEPENDENTLY_VERIFIED")
                self.assertEqual(got["original_CNF_SHA256"],SOURCE_SHA)

    def test_tampering_source_fails_closed(self):
        import tempfile
        path=Path("experiments/time_sat_004_external/lightsout_01d6fa8_verified/original.cnf")
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/"modified.cnf"
            b=path.read_bytes()
            bad.write_bytes(b+b"c forged\n")
            with self.assertRaises(AssertionError):verify_source(bad)

    def test_full_validation_rejects_wrong_assignment_and_empty_clause(self):
        self.assertFalse(full_verify(((1,),),1,{1:False}))
        self.assertFalse(full_verify(((),),1,{1:True}))
        self.assertTrue(full_verify(((1,-2),),2,{1:True,2:True}))

    def test_budgets_and_arms_fixed(self):
        self.assertEqual(CPU_LIMIT,8)
        self.assertEqual(RAM_LIMIT,2147483648)
        self.assertEqual(len(ARMS),5)

if __name__=="__main__":unittest.main()
