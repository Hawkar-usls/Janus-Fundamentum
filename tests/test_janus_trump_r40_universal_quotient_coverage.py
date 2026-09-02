from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "experiments" / "janus_trump_r40_universal_quotient_coverage.py"
spec = importlib.util.spec_from_file_location("janus_trump_r40", MODULE_PATH)
assert spec is not None and spec.loader is not None
r40 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r40)


class TrumpR40UniversalQuotientCoverageTests(unittest.TestCase):
    def test_symmetric_pyramid_compresses_with_total_transport(self) -> None:
        states = r40.generate_fixture(4, "symmetric")
        result = r40.evaluate_partition(states, r40.safe_signature, "SAFE")
        self.assertEqual(result["N_raw_states"], 4**4)
        self.assertEqual(result["K_quotient_classes"], 1)
        self.assertEqual(result["R_uncovered_or_nonexact_membership"], 0)
        self.assertEqual(result["F_transport_failures"], 0)
        self.assertTrue(result["QUOTIENT_COMPRESSION_OBSERVED"])
        self.assertTrue(result["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"])

    def test_broken_branch_is_split_and_unsafe_coarsening_is_rejected(self) -> None:
        states = r40.generate_fixture(4, "broken")
        safe = r40.evaluate_partition(states, r40.safe_signature, "SAFE")
        unsafe = r40.evaluate_partition(states, r40.unsafe_level_only_signature, "UNSAFE")
        self.assertEqual(safe["K_quotient_classes"], 2)
        self.assertEqual(safe["F_transport_failures"], 0)
        self.assertFalse(safe["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"])
        self.assertEqual(safe["representative_property_failures"], 1)
        self.assertEqual(unsafe["K_quotient_classes"], 1)
        self.assertGreater(unsafe["F_transport_failures"], 0)
        self.assertFalse(unsafe["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"])

    def test_boundary_dependency_preserves_exponential_identity(self) -> None:
        states = r40.generate_fixture(5, "boundary")
        result = r40.evaluate_partition(states, r40.safe_signature, "SAFE")
        self.assertEqual(result["N_raw_states"], 4**5)
        self.assertEqual(result["K_quotient_classes"], result["N_raw_states"])
        self.assertEqual(result["R_uncovered_or_nonexact_membership"], 0)
        self.assertEqual(result["F_transport_failures"], 0)
        self.assertFalse(result["QUOTIENT_COMPRESSION_OBSERVED"])
        self.assertTrue(result["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"])

    def test_finite_success_never_sets_polynomiality(self) -> None:
        result = r40.run_r40((1, 2, 3, 4, 5, 6))
        self.assertEqual(
            result["verdict"],
            "R40_FINITE_QUOTIENT_COVERAGE_CERTIFIED__POLYNOMIALITY_OPEN",
        )
        self.assertTrue(result["status"]["QUOTIENT_COMPRESSION_OBSERVED"])
        self.assertTrue(result["status"]["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"])
        self.assertTrue(result["status"]["NEGATIVE_CONTROL_UNIVERSAL_CLAIM_REJECTED"])
        self.assertTrue(result["status"]["BOUNDARY_DEPENDENCY_BLOCKS_COMPRESSION"])
        self.assertFalse(result["status"]["POLYNOMIALITY_PROVEN"])
        self.assertFalse(result["proof_ladder"]["R39_UNIVERSAL_FIXPOINT_REMAINDER_OBLIGATION_CLOSED"])
        self.assertEqual(result["SAT_IN_P"], "NOT_PROVED")
        self.assertEqual(result["P_VS_NP"], "OPEN")


if __name__ == "__main__":
    unittest.main()
