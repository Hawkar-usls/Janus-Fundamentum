import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from janus_trump_osiris_r3_natural_residuals import (  # noqa: E402
    R2_DENSITY_THRESHOLD,
    R2_MAX_PAIR_PROPOSALS,
    R2_MIN_VARS_FOR_MEET,
    verify_sat,
)
from janus_trump_osiris_r3b_proof_carrying_recovery import (  # noqa: E402
    R3B_MIN_FAMILIES,
    R3B_MIN_RESIDUALS,
    R3B_SELECTED_RESIDUAL_CAP,
    evaluate_r3b,
    probe_family_stratified_residuals,
)


class TrumpOsirisR3BRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = probe_family_stratified_residuals()

    def test_r2_rule_is_unchanged(self):
        self.assertEqual(R2_DENSITY_THRESHOLD, 0.70)
        self.assertEqual(R2_MIN_VARS_FOR_MEET, 4)
        self.assertEqual(R2_MAX_PAIR_PROPOSALS, 12)

    def test_family_stratified_pretruth_acquisition(self):
        self.assertGreaterEqual(len(self.rows), R3B_MIN_RESIDUALS)
        self.assertLessEqual(len(self.rows), R3B_SELECTED_RESIDUAL_CAP)
        families = {r["source"]["family"] for r in self.rows}
        self.assertGreaterEqual(len(families), R3B_MIN_FAMILIES)
        for row in self.rows:
            w = row["pretruth_witness"]
            self.assertIsNone(w["truth"])
            self.assertIsNone(w["candidate_result"])
            self.assertIsNone(w["verification_result"])

    def test_recovery_candidates_match_independent_verifier(self):
        for row in self.rows[:12]:
            with self.subTest(source=row["source"]):
                out = evaluate_r3b(row)
                self.assertTrue(out["checks"]["baseline_exact"])
                self.assertTrue(out["checks"]["terminal_match"])
                self.assertTrue(out["checks"]["sat_witness_replay"])
                self.assertTrue(out["checks"]["verified_experience_eligible"])

    def test_fallback_sat_is_proof_carrying_when_exposed(self):
        exposed = 0
        for row in self.rows:
            if row["pretruth_witness"]["route_prediction"] != "EXACT_FALLBACK":
                continue
            out = evaluate_r3b(row)
            if out["candidate"]["terminal"] == "SAT":
                exposed += 1
                self.assertIsNotNone(out["candidate"]["witness"])
                witness = {int(k): bool(v) for k, v in out["candidate"]["witness"].items()}
                self.assertTrue(verify_sat(row["cnf"], witness))
                if exposed >= 3:
                    break
        self.assertGreaterEqual(exposed, 1)


if __name__ == "__main__":
    unittest.main()
