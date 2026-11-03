#!/usr/bin/env python3
"""R4 pre-solve CNF feature calibration; no R4 labels in training."""
from hashlib import sha256
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c5_r4_model as m
import janus_time_sat_004e12c5_r4_benchmark as b
import janus_time_sat_004e12c5_r4_audit as audit

class R4FrozenGeneralizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit=m.train()

    def test_prior_only_training_13_unique_sha_12_unique_grid_sizes(self):
        p,protocolsha=m.load_frozen()
        self.assertEqual(self.fit["prereg_sha256"],protocolsha)
        self.assertEqual(self.fit["training_original_source_count"],13)
        self.assertEqual(self.fit["training_distinct_side_size_count"],12)
        self.assertEqual(len(set(self.fit["training_SHAs"])),13)
        self.assertEqual(sum(len(v["original_SHA256"]) for v in self.fit["groups"]),13)
        self.assertTrue(all(x["training_historical_only"] for x in m.historical_samples()))
        self.assertEqual(len(m.canonical(self.fit)),len(m.canonical(m.train())))

    def test_leave_one_entire_size_out_and_nonzero_uncertainty(self):
        self.assertEqual(len(self.fit["leave_one_side_out_absolute_log_residuals"]),12)
        self.assertGreaterEqual(self.fit["leave_one_side_out_median_absolute_log_gain_error"],0)
        self.assertTrue(all(v>=0 for v in self.fit["leave_one_side_out_absolute_log_residuals"]))
        self.assertEqual(len({q["side"] for q in self.fit["groups"]}),12)

    def test_new_multi_family_inputs_have_unique_sha_and_no_training_leak(self):
        hashes=[]
        for case,kind,dim,seed in m.CASES:
            n,rows=m.source(case)
            x=m.r1.original_sha(rows,n)
            hashes.append(x)
            self.assertNotIn(x,self.fit["training_SHAs"])
            self.assertGreater(len(rows),0)
            f,c=m.cnf_profile(rows,n)
            self.assertEqual(tuple(f),m.FEAT_KEYS)
            self.assertGreater(f["log1p_clauses"],0)
            if kind=="LIGHTSOUT_PLANTED_SAT":
                self.assertEqual(c["status"],"EXACT_XOR_COVER_PASS")
                self.assertEqual(f["is_proven_square_lightsout_topology"],1)
            elif kind=="RANDOM_PLANTED_XOR_COMPLETE":
                self.assertEqual(c["status"],"EXACT_XOR_COVER_PASS")
                self.assertEqual(f["is_proven_square_lightsout_topology"],0)
            else:
                self.assertNotEqual(c["status"],"EXACT_XOR_COVER_PASS")
        self.assertEqual(len(set(hashes)),8)

    def test_selector_is_past_only_and_abstains_on_unknown_and_partial_cnf(self):
        for case,kind,dim,seed in m.CASES:
            n,rows=m.source(case)
            chosen,cover,pred,reason,feat,elapsed=m.choose(rows,n,self.fit)
            self.assertLess(elapsed,2.0)
            if kind!="LIGHTSOUT_PLANTED_SAT":
                self.assertEqual(chosen,"cryptominisat_original_cnf",case)
                self.assertIsNone(pred)
            else:
                self.assertIn(chosen,("janus_gf2","cryptominisat_native_xor"))
                self.assertIsNotNone(pred)
                self.assertGreater(pred["predicted_gf2_full_cold_s"],0)
                self.assertGreater(pred["predicted_fastest_external_full_cold_s"],0)
                self.assertEqual(len(set(pred["neighbor_distinct_grid_sizes"])),5)
                if chosen=="janus_gf2":
                    self.assertGreaterEqual(pred["risk_lower_bound_gain"],1.2)
                    self.assertGreaterEqual(pred["predicted_gain"],1.4)
            self.assertEqual(chosen,m.choose(rows,n,self.fit)[0])

    def test_missing_xor_clause_and_grid_relabel_fail_closed(self):
        n,rows=m.source("r4_lo_31")
        partial=rows[:-1]
        chosen,proof,pred,reason,_,_=m.choose(partial,n,self.fit)
        self.assertEqual(chosen,"cryptominisat_original_cnf")
        self.assertIsNone(proof)
        self.assertIsNone(pred)
        with self.assertRaises(AssertionError):
            m.r3.gf2(partial,n)
        def swap(lit):
            v=abs(lit)
            new=2 if v==1 else 1 if v==2 else v
            return new if lit>0 else -new
        renamed=[[swap(lit) for lit in row] for row in rows]
        f,cert=m.cnf_profile(renamed,n)
        self.assertEqual(cert["status"],"EXACT_XOR_COVER_PASS")
        self.assertEqual(f["is_proven_square_lightsout_topology"],0)
        engine,_,pred,_,_,_=m.choose(renamed,n,self.fit)
        self.assertEqual(engine,"cryptominisat_original_cnf")
        self.assertIsNone(pred)

    def test_fitted_checkpoint_replay_sha_enforced(self):
        with TemporaryDirectory() as directory:
            file=Path(directory)/"fit.json"
            file.write_bytes(m.canonical(self.fit))
            valid=sha256(file.read_bytes()).hexdigest()
            read=b.load_fit(file,valid)
            self.assertEqual(read["training_SHAs"],self.fit["training_SHAs"])
            with self.assertRaises(AssertionError):
                b.load_fit(file,"0"*64)
            file.write_bytes(file.read_bytes()+b" ")
            with self.assertRaises(AssertionError):
                b.load_fit(file,valid)

    def test_audit_fails_closed_on_missing_host(self):
        with self.assertRaisesRegex(AssertionError,"R4_BOTH_HOSTS_REQUIRED"):
            audit.check([])
        with self.assertRaisesRegex(AssertionError,"R4_BOTH_HOSTS_REQUIRED"):
            audit.check([{}])

if __name__=="__main__":
    unittest.main()
