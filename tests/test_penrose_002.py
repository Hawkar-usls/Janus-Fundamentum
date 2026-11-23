#!/usr/bin/env python3
"""Independent negative and positive tests for three-contour causal receipts."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
from janus_penrose_002_integration import (
    REQUIRED_EDGES, STAGES, build_bundle, build_receipts,
    check_dependencies, digest, get_fixture, inspect_proof_and_oracle,
    source_id, verify_bundle,
)


class CrossContourCausalAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.wire = build_bundle(
            "TSEITIN_K4_NONAFFINE_WRAPPED", samples=12, max_iso_edges=5)

    def test_positive_real_ufr_proof_and_both_oracle_and_verifier(self):
        report = self.report
        self.assertTrue(verify_bundle(report, self.wire))
        self.assertFalse(report["stage_payloads"]["INDEPENDENT_REPLAY"]["answer"])
        self.assertGreaterEqual(
            report["stage_payloads"]["UFR_ORACLE_COVARIANCE"]
                  ["verified_iso_edges_in_proof"], 1)
        self.assertGreaterEqual(
            report["stage_payloads"]["UFR_ORACLE_COVARIANCE"]
                  ["oracle_checked_iso_edges"], 1)
        self.assertEqual(report["stage_payloads"]["SCHEDULE_AUDIT"]["passed"], True)
        self.assertEqual(set(report["stage_receipts"]), set(STAGES))

    def test_cyclic_dependency_rejected_with_independent_penrose_witness(self):
        extra = REQUIRED_EDGES + (("FINAL_GATE", "UFR_PRODUCE"),)
        with self.assertRaisesRegex(AssertionError, "circular dependency"):
            check_dependencies(extra)
        report = deepcopy(self.report)
        report["dependencies"].append(["FINAL_GATE", "UFR_PRODUCE"])
        with self.assertRaisesRegex(AssertionError, "circular dependency"):
            verify_bundle(report, self.wire)

    def test_missing_dependency_and_future_to_source_rejected(self):
        missing = tuple(edge for edge in REQUIRED_EDGES
                        if edge != ("UFR_CERTIFICATE", "INDEPENDENT_REPLAY"))
        with self.assertRaisesRegex(AssertionError, "missing mandatory"):
            check_dependencies(missing)
        with self.assertRaises(AssertionError):
            check_dependencies(REQUIRED_EDGES + (("FINAL_GATE", "SOURCE"),))
        with self.assertRaises(AssertionError):
            check_dependencies(REQUIRED_EDGES + (("FINAL_GATE", "FINAL_GATE"),))

    def test_forged_stage_summary_final_claim_or_chain_rejected(self):
        for stage, key, wrong_value in (
            ("UFR_PRODUCE", "iso_hits", 100_000),
            ("ORACLE_COMPILE", "qubits_estimate", 1),
            ("SCHEDULE_AUDIT", "passed", False),
            ("ORACLE_TRUTH", "all_match", False),
            ("FINAL_GATE", "accepted", False),
        ):
            with self.subTest(stage=stage):
                forged = deepcopy(self.report)
                forged["stage_payloads"][stage][key] = wrong_value
                with self.assertRaises(AssertionError):
                    verify_bundle(forged, self.wire)
        forged_receipt = deepcopy(self.report)
        forged_receipt["stage_receipts"]["FINAL_GATE"] = "0" * 64
        with self.assertRaisesRegex(AssertionError, "receipt"):
            verify_bundle(forged_receipt, self.wire)

    def test_formally_correct_receipts_do_not_make_false_claims_true(self):
        forged = deepcopy(self.report)
        forged["stage_payloads"]["ORACLE_TRUTH"]["all_match"] = False
        forged["stage_receipts"] = build_receipts(
            forged["stage_payloads"], tuple(map(tuple, forged["dependencies"])))
        with self.assertRaisesRegex(AssertionError, "independent evidence"):
            verify_bundle(forged, self.wire)

    def test_wrong_source_and_certificate_bytes_detected(self):
        replaced = deepcopy(self.report)
        replaced["fixture"] = "RENAMED_TWIN_POSITIVE_CONTROL"
        with self.assertRaises((AssertionError, ValueError, KeyError)):
            verify_bundle(replaced, self.wire)
        changed_proof = self.wire.replace("__ufr_tuple_v1__", "__fake_tuple_v1__", 1)
        self.assertNotEqual(changed_proof, self.wire)
        with self.assertRaisesRegex(AssertionError, "proof bytes"):
            verify_bundle(self.report, changed_proof)
        stolen = deepcopy(self.report)
        from hashlib import sha256
        stolen["proof_file_sha256"] = sha256(changed_proof.encode()).hexdigest()
        with self.assertRaises((AssertionError, ValueError, KeyError)):
            verify_bundle(stolen, changed_proof)

    def test_dag_rank_constructive_and_stage_sources_match(self):
        report = self.report
        rank = dict(check_dependencies().ranks)
        for upstream, downstream in REQUIRED_EDGES:
            self.assertLess(rank[upstream], rank[downstream])
        cnf, n = get_fixture("TSEITIN_K4_NONAFFINE_WRAPPED")
        self.assertEqual(source_id(cnf, n),
                         report["stage_payloads"]["SOURCE"]["source_sha256"])
        self.assertEqual(report["stage_payloads"]["INDEPENDENT_REPLAY"]
                         ["trusted_source_sha256"], source_id(cnf, n))
        self.assertTrue(report["stage_payloads"]["FINAL_GATE"]
                        ["production_c023_unchanged"])
        self.assertEqual(report["stage_payloads"]["FINAL_GATE"]
                         ["classical_simulator_only"], True)

    def test_strict_input_and_workload_bounds(self):
        with self.assertRaises(ValueError):
            get_fixture("UNTRUSTED_EXTERNAL_FORMULA")
        with self.assertRaises(ValueError):
            inspect_proof_and_oracle(
                "TSEITIN_K4_NONAFFINE_WRAPPED", self.wire, sample_count=999)
        self.assertEqual(len(STAGES), 9)
        self.assertEqual(len(REQUIRED_EDGES), 14)


if __name__ == "__main__":
    unittest.main()
