import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from janus_trump_osiris_r3_natural_residuals import (  # noqa: E402
    R2_DENSITY_THRESHOLD,
    R2_MAX_PAIR_PROPOSALS,
    R2_MIN_VARS_FOR_MEET,
    R3_MAX_RESIDUALS,
    R3_MIN_RESIDUALS,
    R3_PROBE_MAX_DEPTH,
    evaluate_residual,
    probe_natural_residuals,
)


class TrumpOsirisR3NaturalResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = probe_natural_residuals()

    def test_frozen_constants(self):
        self.assertEqual(R2_DENSITY_THRESHOLD, 0.70)
        self.assertEqual(R2_MIN_VARS_FOR_MEET, 4)
        self.assertEqual(R2_MAX_PAIR_PROPOSALS, 12)
        self.assertEqual(R3_PROBE_MAX_DEPTH, 2)
        self.assertEqual(R3_MAX_RESIDUALS, 48)
        self.assertEqual(R3_MIN_RESIDUALS, 24)

    def test_probe_yields_pretruth_solver_native_residuals(self):
        self.assertGreaterEqual(len(self.rows), R3_MIN_RESIDUALS)
        self.assertLessEqual(len(self.rows), R3_MAX_RESIDUALS)
        self.assertGreaterEqual(len({r["source"]["family"] for r in self.rows}), 4)
        for row in self.rows:
            w = row["pretruth_witness"]
            self.assertIsNone(w["truth"])
            self.assertIsNone(w["candidate_result"])
            self.assertIsNone(w["verification_result"])
            self.assertTrue(w["witness_sha256"])
            self.assertTrue(w["formula_sha256"])
            self.assertIn(w["route_prediction"], {"TRY_EXACT_MEET", "EXACT_FALLBACK"})

    def test_pretruth_witnesses_are_unique(self):
        hashes = [r["pretruth_witness"]["witness_sha256"] for r in self.rows]
        self.assertEqual(len(hashes), len(set(hashes)))

    def test_first_natural_residuals_verify_exactly(self):
        for row in self.rows[:8]:
            with self.subTest(source=row["source"]):
                out = evaluate_residual(row)
                self.assertTrue(out["checks"]["baseline_exact"])
                self.assertTrue(out["checks"]["terminal_match"])
                self.assertTrue(out["checks"]["sat_witness_replay"])
                self.assertTrue(out["checks"]["verified_experience_eligible"])
                self.assertIsNotNone(out["verified_experience"])


if __name__ == "__main__":
    unittest.main()
