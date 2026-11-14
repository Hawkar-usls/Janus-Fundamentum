#!/usr/bin/env python3
"""Fail-closed, negative and positive development checks; no external witness."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
EXT=ROOT/"experiments"/"time_sat_004_external"
sys.path.insert(0,str(EXT))
from time_sat_004d9b_science_demo import demonstrate, cases, satisfying_assignments
from time_sat_004d9b_trust_gate import approved_policy, _check_lock_structure
from time_sat_004d9b_benchmark import protocol, source_info, EXPECTED_ARMS
from time_sat_004d9b_up_cleanroom_baseline import baseline_case, full_xor_signmasks, rank as clean_rank

class ReviewerPackageTest(unittest.TestCase):
    def test_math_demo_positive_null_negative_and_bruteforce(self):
        result=demonstrate()
        data={r["case"]:r for r in result["examples"]}
        self.assertEqual(set(data),set(cases()))
        self.assertGreaterEqual(data["guarded_source_derived_rank"]["coefficient_rank_increment"],1)
        self.assertEqual(data["explicit_xor_no_increment"]["coefficient_rank_increment"],0)
        self.assertEqual(data["linear_combination_no_increment"]["coefficient_rank_increment"],0)
        self.assertEqual(data["not_every_cnf_is_parity"]["derived_xor"],[])
        self.assertEqual(result["independent_third_party_validation"],"NOT_PERFORMED")
        self.assertEqual(result["end_to_end_solver_speedup"],"NOT_MEASURED")
        for name,case in cases().items():
            self.assertGreater(len(satisfying_assignments(case["rows"],case["n"])),0)
            self.assertEqual(data[name]["independent_truth_table_entailment"],"PASS")
            self.assertEqual(data[name]["independent_resolution_dag_replay"],"PASS")

    def test_unit_propagation_recovers_toy_xor_without_janus(self):
        guarded=cases()["guarded_source_derived_rank"]
        direct=baseline_case(guarded["n"],guarded["rows"])
        self.assertEqual(direct["status"],"UP_AND_COMPLETE_SIGNMASK_XOR_BASELINE_READY")
        self.assertEqual(direct["unit_assignments"],{"4":False})
        post={(tuple(x["variables"]),x["rhs"]) for x in direct["post_UP_equations"]}
        self.assertIn(((1,2,3),1),post)
        self.assertIn(((4,),0),{(tuple(x["variables"]),x["rhs"])
                                 for x in direct["baseline_equations"]})
        janus=demonstrate()["examples"][0]
        janus_equations={(tuple(x["variables"]),x["rhs"])
                         for x in janus["explicit_xor"]+janus["derived_xor"]}
        baseline={(tuple(x["variables"]),x["rhs"])
                  for x in direct["baseline_equations"]}
        self.assertEqual(clean_rank(baseline|janus_equations,4)-clean_rank(baseline,4),0)
        self.assertEqual(clean_rank(baseline,4),2)

    def test_original_empty_policy_stays_git_sha_frozen(self):
        old=EXT/"PREREGISTERED_004D9_EXTERNAL_WITNESS_INTAKE_20261102.json"
        blob=subprocess.run(["git","hash-object",str(old)],check=True,text=True,
                            capture_output=True).stdout.strip()
        self.assertEqual(blob,"83f17049fdcc663dd8acc8f878e0ca9bc73623cf")
        source=json.loads(old.read_text())
        self.assertEqual(source["custodian"]["authorized_external_custodians"],[])
        self.assertEqual(source["locked_candidate_cohort"],[])

    def test_no_caller_selected_trust_root_no_external_admission(self):
        self.assertIsNone(approved_policy())
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"out.json"
            result=subprocess.run([sys.executable,str(EXT/"time_sat_004d9b_trust_gate.py"),
                                  "--preflight","--out",str(path)],check=True,
                                  text=True,capture_output=True)
            obj=json.loads(path.read_text())
            self.assertEqual(obj["actual_external_SAT_cases_admitted"],0)
            self.assertEqual(obj["status"],"WAITING_FOR_OUTSIDE_ADMIN_APPROVAL_AND_CODE_PINNED_LOCKFILE")
            self.assertIn("004D9B_TRUST_GATE",result.stdout)

    @staticmethod
    def fake_lock():
        h=lambda s:sha256(s.encode()).hexdigest()
        return {"schema":"JANUS-TIME-SAT-004D9B-INDEPENDENT-CUSTODIAN-TRUST-LOCK-V1",
                "external_review":{"status":"APPROVED_OUT_OF_BAND",
                    "reviewer_identity":"SYNTHETIC_ONLY_NOT_REAL",
                    "institution":"TEST_ONLY",
                    "signed_review_reference":"SYNTHETIC_TEST_ONLY",
                    "signed_review_sha256":h("review")},
                "custodian":{"authorized_external_custodians":["synthetic-lab-fixture"],
                    "trusted_ed25519_public_keys_base64":{"synthetic-lab-fixture":"synthetic-public-key"}},
                "locked_candidate_cohort":[
                    {"family":"toy-family-"+str(i),"candidate_id":"toy-"+str(i),
                     "external_issuer_id":"synthetic-lab-fixture",
                     "source_sha256":h("cnf-"+str(i)),
                     "model_sha256":h("model-"+str(i)),
                     "n_variables":3,"n_clauses":4,"n_literal_occurrences":12}
                    for i in range(3)],
                "input_limits":{"max_source_bytes":134217728,"max_source_variables":5000,
                                "max_source_clauses":30000,"max_source_literals":120000,
                                "max_model_bytes":200000},
                "no_post_hoc_replacement":True,
                "negative_and_timeout_cases_retained":True,
                "algorithm_commit_sha256":h("example-only-algorithm")}

    def test_adversarial_new_trust_lock_structure(self):
        valid=self.fake_lock()
        self.assertIs(_check_lock_structure(valid),valid) # syntax only, NOT identity proof
        for modification in ("duplicate_source","duplicate_family","self_issuer",
                             "missing_review","oversized_budget","false_negative_policy"):
            case=deepcopy(valid)
            if modification=="duplicate_source":
                case["locked_candidate_cohort"][1]["source_sha256"]=case["locked_candidate_cohort"][0]["source_sha256"]
            elif modification=="duplicate_family":
                case["locked_candidate_cohort"][1]["family"]=case["locked_candidate_cohort"][0]["family"]
            elif modification=="self_issuer":
                case["custodian"]["trusted_ed25519_public_keys_base64"]["JANUS"]="arbitrary"
                case["custodian"]["authorized_external_custodians"].append("JANUS")
            elif modification=="missing_review":
                case["external_review"]["status"]="NONE"
            elif modification=="oversized_budget":
                case["input_limits"]["max_source_clauses"]=999999999
            elif modification=="false_negative_policy":
                case["negative_and_timeout_cases_retained"]=False
            if modification=="duplicate_family":
                case["locked_candidate_cohort"][2]["family"]=case["locked_candidate_cohort"][0]["family"]
            with self.subTest(modification=modification):
                with self.assertRaises(ValueError):_check_lock_structure(case)

    def test_pinned_protocol_and_all_four_cold_arms(self):
        p=protocol()
        self.assertEqual(tuple(p["arms"]),EXPECTED_ARMS)
        self.assertEqual(p["paired_repetitions"],3)
        self.assertEqual(p["unsat_proof"],"NOT_IMPLEMENTED_REJECT_UNSAT_AS_UNVERIFIED")
        self.assertTrue(p["verify_sat_model_against_every_original_clause"])
        for name in cases():
            n,rows,source_sha=source_info(name)
            self.assertEqual(n,cases()[name]["n"])
            self.assertEqual(len(source_sha),64)
            self.assertEqual(rows,cases()[name]["rows"])

if __name__=="__main__":
    unittest.main()
