from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))
MODULE_PATH = EXPERIMENTS / "janus_trump_r44_43004_quotient_transport_stall_class.py"
spec = importlib.util.spec_from_file_location("janus_trump_r44", MODULE_PATH)
assert spec is not None and spec.loader is not None
r44 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44)


class TrumpR44QuotientTransportStallClassTests(unittest.TestCase):
    def test_frozen_universe_and_sealed_counterexample_identity(self) -> None:
        cases = list(r44.r43.frozen_search_cases())
        self.assertEqual(len(cases), 83)
        label, seed, formula = cases[6]
        self.assertEqual(seed, 43004)
        self.assertEqual(
            r44.r42.formula_hash(formula),
            "eab8907cd5e97c244548797f226a91dfd0d43c196fb4461fb8880234c7de43a6",
        )

    def test_truth_blind_candidate_detects_mixed_Q_transport(self) -> None:
        base = {
            "input_measure_CLV": [206, 618, 48],
            "terminal_measure_CLV": [203, 603, 48],
            "delta_measure_CLV": [3, 15, 0],
            "cycle_count": 2,
            "SA_BVE_applications": 0,
        }
        rows = [
            {**base, "ordinal": 1, "label": "DECIDED", "seed": 1, "semantic_decided": True},
            {**base, "ordinal": 2, "label": "STALLED", "seed": 2, "semantic_decided": False},
        ]
        q = r44.build_candidate_quotient(rows)
        self.assertEqual(q["N_raw_states"], 2)
        self.assertEqual(q["K_quotient_classes"], 1)
        self.assertEqual(q["R_uncovered_or_nonexact_membership"], 0)
        self.assertEqual(q["F_transport_failures"], 1)
        self.assertFalse(q["CANDIDATE_QUOTIENT_TRANSPORT_SOUND"])
        self.assertEqual(q["mixed_Q_class_count"], 1)

    def test_truth_blind_candidate_accepts_pure_Q_class(self) -> None:
        base = {
            "input_measure_CLV": [10, 30, 8],
            "terminal_measure_CLV": [8, 24, 7],
            "delta_measure_CLV": [2, 6, 1],
            "cycle_count": 1,
            "SA_BVE_applications": 0,
        }
        rows = [
            {**base, "ordinal": 1, "label": "A", "seed": 1, "semantic_decided": True},
            {**base, "ordinal": 2, "label": "B", "seed": 2, "semantic_decided": True},
        ]
        q = r44.build_candidate_quotient(rows)
        self.assertEqual(q["K_quotient_classes"], 1)
        self.assertEqual(q["F_transport_failures"], 0)
        self.assertTrue(q["CANDIDATE_QUOTIENT_TRANSPORT_SOUND"])

    def test_pyramid_adversarial_controls(self) -> None:
        controls = r44.pyramid_controls((1, 2, 3, 4, 5, 6))
        self.assertTrue(controls["pass"])
        for row in controls["depth_results"]:
            N = 4 ** row["depth"]
            self.assertEqual(row["symmetric"]["K"], 1)
            self.assertEqual(row["symmetric"]["F"], 0)
            self.assertGreater(row["broken_unsafe"]["F"], 0)
            self.assertEqual(row["boundary_dependency"]["K"], N)


if __name__ == "__main__":
    unittest.main()
