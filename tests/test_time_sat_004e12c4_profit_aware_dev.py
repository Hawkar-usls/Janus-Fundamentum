#!/usr/bin/env python3
"""E12C4 development-only checks: never time or learn on frozen held-out sources."""
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
import janus_time_sat_004e12c4_profit_aware_dev as e


class E12C4InternalDevTests(unittest.TestCase):
    def test_internal_split_disjoint_unique_originals_two_per_family(self):
        lock = e.cohort_manifest()
        d, h = lock["catalog"]["development"], lock["catalog"]["heldout_internal"]
        self.assertEqual(len(d), 2 * len(e.FAMILIES))
        self.assertEqual(len(h), 2 * len(e.FAMILIES))
        self.assertFalse(lock["holdout_timed"])
        self.assertFalse(lock["holdout_external"])
        self.assertEqual(len({x["original_sha256"] for x in d + h}), len(d + h))
        for name in e.FAMILIES:
            self.assertEqual(sum(x["family"] == name for x in d), 2)
            self.assertEqual(sum(x["family"] == name for x in h), 2)

    def test_near_70_threshold_actually_straddles_and_is_not_a_speed_label(self):
        for target in e.COVERAGES:
            src = e.generate("coverage_%s" % str(target), e.DEVELOPMENT[0][1])
            rows, n = src["rows"], src["n"]
            idx = e.c1.source_index_all_widths(rows, n)
            selection = [z for z in idx["equations"] if z["width"] in (5, 6)]
            f = e.features(rows, n, selection)
            self.assertEqual(len(selection), 12)
            self.assertLess(abs(f["coverage"] - target), 0.002)
            self.assertEqual(e.choose(rows, n)["decision"], "RAW")

    def test_satisfying_model_replayed_under_all_registered_isomorphisms(self):
        for f in e.FAMILIES:
            if f == "unsat_parity_guard":
                continue
            src = e.generate(f, 202611049001)
            for v in e.VARIANTS:
                t = e.transform(src, v)
                self.assertTrue(e._model_ok(t["rows"], t["model"]))
                self.assertEqual(
                    Counter(map(lambda r: tuple(sorted(r)), src["rows"])),
                    Counter(map(lambda r: tuple(sorted(r)), t["rows"]))
                ) if v != "renamed_polarity" else self.assertNotEqual(
                    t["variant_sha256"], e.digest(src["cnf"]))

    def test_unsat_genuine_independent_exhaustion_after_all_variants(self):
        for seed in (202611049101, 202611049102):
            src = e.generate("unsat_parity_guard", seed)
            for v in e.VARIANTS:
                t = e.transform(src, v)
                self.assertEqual(
                    e.independent_truth_table(t["rows"], t["n"]),
                    "INTERNAL_EXHAUSTIVE_UNSAT_VERIFIED")
                self.assertIsNone(t["model"])

    def test_exact_residual_conservation_incomplete_duplicates_and_guards(self):
        src = e.generate("mixed_partial", 202611049201)
        for v in e.VARIANTS:
            t = e.transform(src, v)
            idx = e.c1.source_index_all_widths(t["rows"], t["n"])
            self.assertEqual(len(idx["equations"]), 8)
            selected = [z for z in idx["equations"] if z["width"] in (5, 6)]
            residual = e._proof_and_residual(t["rows"], t["n"], selected)
            used = {i for z in selected for i in z["original_clause_indices"]}
            self.assertEqual(residual, [r for i, r in enumerate(t["rows"]) if i not in used])
            self.assertEqual(
                Counter(tuple(sorted(r)) for r in t["rows"]),
                Counter(tuple(sorted(t["rows"][i])) for i in used) +
                Counter(tuple(sorted(r)) for r in residual))

    def test_profit_gate_needs_two_source_sha_and_certification(self):
        s = e.generate("coverage_0.75", 202611049301)
        idx = e.c1.source_index_all_widths(s["rows"], s["n"])
        f = e.features(s["rows"], s["n"], idx["equations"])
        def receipt(sha, censored=False):
            return {"original_sha256": sha, "features": f, "paired_full_cold": [{
                "raw_status": "UNKNOWN_CPU_LIMIT" if censored else "VERIFIED",
                "xor_status": "VERIFIED", "raw_s": 4.0, "xor_s": 1.0}]}
        a, b = "a"*64, "b"*64
        one = e.fit_development([receipt(a)])
        self.assertEqual(e.choose(s["rows"], s["n"], one)["decision"], "RAW")
        both = e.fit_development([receipt(a), receipt(b)])
        for v in e.VARIANTS:
            t = e.transform(s, v)
            picked = e.choose(t["rows"], t["n"], both)
            self.assertEqual(picked["decision"], "XOR_INTERNAL_DEVELOPMENT")
            self.assertEqual(len(picked["equations"]), 12)
            self.assertEqual(
                len(picked["cnf_clauses"]) + 32*12, len(t["rows"]))
        uncertain = e.fit_development([receipt(a), receipt(b, True)])
        self.assertEqual(e.choose(s["rows"], s["n"], uncertain)["decision"], "RAW")
        with self.assertRaises(AssertionError):
            e.fit_development([receipt(a)], forbidden_source_shas=(a,))
        with self.assertRaises(AssertionError):
            e.fit_development([receipt(a), receipt(a)])

    def test_partial_mask_alone_is_never_an_xor_certificate(self):
        vars_ = (1,2,3,4,5,6)
        block = e._block(vars_, 0)
        for missing in (0, 12, 31):
            rows = [r for i, r in enumerate(block) if i != missing]
            chosen = e.choose(rows, 6)
            self.assertEqual(chosen["decision"], "RAW")
            self.assertEqual(chosen["cnf_clauses"], rows)

    def test_timeout_never_receives_finite_regret_and_unknown_unsat_is_not_verified(self):
        self.assertEqual(e.pair_result({"status": "UNKNOWN_CPU_LIMIT"},
                                       {"status": "SAT_VERIFIED"})["regret"], "INDETERMINATE")
        self.assertEqual(e.pair_result({"status": "UNSAT_REPORTED_NO_PROOF"},
                                       {"status": "UNSAT_PROOF_VERIFIED"})["regret"], "INDETERMINATE")
        self.assertEqual(e.independent_truth_table([[1]], 30), "UNVERIFIED_TOO_LARGE")
        self.assertEqual(e.pair_result({"status":"SAT_VERIFIED","full_cold_s":4.0},
                                       {"status":"SAT_VERIFIED","full_cold_s":2.0})
                         ["raw_over_candidate"], 2.0)

if __name__ == "__main__":
    unittest.main()
