from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))
MODULE_PATH = EXPERIMENTS / "janus_trump_r45b_frozen_26_stall_quotient_macro_coverage.py"
spec = importlib.util.spec_from_file_location("janus_trump_r45b", MODULE_PATH)
assert spec is not None and spec.loader is not None
r45b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r45b)


class TrumpR45BFrozen26StallCoverageTests(unittest.TestCase):
    def test_frozen_seed_ledger_is_exact_and_present_in_r43(self) -> None:
        expected = (
            43004,
            43101, 43102, 43103, 43104, 43105, 43106, 43107, 43108, 43109,
            43110, 43111, 43112, 43113, 43115,
            43201, 43203, 43204, 43205, 43206, 43207, 43209, 43210, 43212, 43213, 43216,
        )
        self.assertEqual(r45b.FROZEN_STALL_SEEDS, expected)
        self.assertEqual(len(expected), 26)
        self.assertEqual(len(set(expected)), 26)
        cases = r45b.frozen_case_map()
        self.assertTrue(all(seed in cases for seed in expected))

    def test_structural_signature_is_truth_blind(self) -> None:
        base = {
            "input_measure_CLV": [206, 618, 48],
            "delta_measure_CLV": [3, 15, 0],
            "cycle_count": 2,
            "SA_BVE_applications": 0,
        }
        a = {**base, "Q_macro": True, "selected_var": 26, "selected_terminal": "RUP_UNSAT"}
        b = {**base, "Q_macro": False, "selected_var": None, "selected_terminal": None}
        self.assertEqual(r45b.structural_signature(a), r45b.structural_signature(b))

    def test_mixed_Q_macro_class_produces_transport_failure(self) -> None:
        base = {
            "input_measure_CLV": [10, 30, 8],
            "delta_measure_CLV": [1, 3, 0],
            "cycle_count": 2,
            "SA_BVE_applications": 0,
        }
        rows = [
            {**base, "seed": 1, "Q_macro": True},
            {**base, "seed": 2, "Q_macro": False},
        ]
        original = r45b.FROZEN_STALL_SEEDS
        try:
            r45b.FROZEN_STALL_SEEDS = (1, 2)
            q = r45b.build_quotient(rows)
        finally:
            r45b.FROZEN_STALL_SEEDS = original
        self.assertEqual(q["N_raw_stalls"], 2)
        self.assertEqual(q["K_quotient_classes"], 1)
        self.assertEqual(q["R_uncovered_or_nonexact_membership"], 0)
        self.assertEqual(q["F_Q_macro_transport_failures"], 1)
        self.assertEqual(q["mixed_Q_macro_class_count"], 1)
        self.assertIsNotNone(q["first_transport_failure"])
        self.assertTrue(q["AUDIT_TRANSPORT_ONLY"])
        self.assertFalse(q["RUNTIME_QUOTIENT_COMPRESSION_PROVEN"])

    def test_pure_Q_macro_class_has_zero_transport_failures(self) -> None:
        base = {
            "input_measure_CLV": [10, 30, 8],
            "delta_measure_CLV": [1, 3, 0],
            "cycle_count": 2,
            "SA_BVE_applications": 0,
        }
        rows = [
            {**base, "seed": 1, "Q_macro": True},
            {**base, "seed": 2, "Q_macro": True},
        ]
        original = r45b.FROZEN_STALL_SEEDS
        try:
            r45b.FROZEN_STALL_SEEDS = (1, 2)
            q = r45b.build_quotient(rows)
        finally:
            r45b.FROZEN_STALL_SEEDS = original
        self.assertEqual(q["K_quotient_classes"], 1)
        self.assertEqual(q["R_uncovered_or_nonexact_membership"], 0)
        self.assertEqual(q["F_Q_macro_transport_failures"], 0)
        self.assertEqual(q["mixed_Q_macro_class_count"], 0)

    def test_resource_aggregation_separates_sums_and_peaks(self) -> None:
        rows = [
            {"resource_ledger": {"variables_checked": 3, "RUP_checks": 10, "peak_intermediate_clauses": 9, "peak_intermediate_literals": 20}},
            {"resource_ledger": {"variables_checked": 4, "RUP_checks": 11, "peak_intermediate_clauses": 7, "peak_intermediate_literals": 25}},
        ]
        agg = r45b.aggregate_resources(rows)
        self.assertEqual(agg["sum"]["variables_checked"], 7)
        self.assertEqual(agg["sum"]["RUP_checks"], 21)
        self.assertEqual(agg["peak"]["peak_intermediate_clauses"], 9)
        self.assertEqual(agg["peak"]["peak_intermediate_literals"], 25)


if __name__ == "__main__":
    unittest.main()
