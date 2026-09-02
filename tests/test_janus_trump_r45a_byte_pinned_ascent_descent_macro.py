from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))
MODULE_PATH = EXPERIMENTS / "janus_trump_r45a_byte_pinned_ascent_descent_macro.py"
spec = importlib.util.spec_from_file_location("janus_trump_r45a", MODULE_PATH)
assert spec is not None and spec.loader is not None
r45a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r45a)


class TrumpR45ABytePinnedMacroTests(unittest.TestCase):
    def test_exact_dp_replay_does_not_require_immediate_descent(self) -> None:
        formula = r45a.r33.canonical_formula([
            (1, 2, 3),
            (1, -2, 4),
            (-1, 5, 6),
            (-1, -5, 7),
        ])
        record = r45a.exact_dp_record(formula, 1)
        self.assertIsNotNone(record)
        assert record is not None
        replay = r45a.independent_dp_replay(formula, record)
        self.assertTrue(replay["pass"])
        self.assertTrue(r45a.polynomial_envelope(formula, record)["pass"])

    def test_tampered_resolvent_certificate_is_rejected(self) -> None:
        formula = r45a.r33.canonical_formula([(1, 2), (-1, 2)])
        record = r45a.exact_dp_record(formula, 1)
        self.assertIsNotNone(record)
        assert record is not None
        tampered = json.loads(json.dumps(record))
        tampered["full_non_tautological_resolvents"] = []
        replay = r45a.independent_dp_replay(formula, tampered)
        self.assertFalse(replay["pass"])
        self.assertFalse(replay["resolvents_ok"])

    def test_sat_terminal_reconstructs_across_dp_and_r33(self) -> None:
        formula = r45a.r33.canonical_formula([(1, 2), (-1, 2)])
        row = r45a.macro_candidate_for_var(formula, 1)
        self.assertIsNotNone(row)
        assert row is not None
        self.assertTrue(row["semantic_terminal_verified"])
        self.assertTrue(row["normalization"]["semantic_sat"])
        self.assertTrue(row["SAT_reconstruction"]["pass"])
        self.assertTrue(r45a.independent_macro_replay(formula, row)["pass"])

    def test_unsat_terminal_transfers_back_through_exact_dp(self) -> None:
        formula = r45a.r33.canonical_formula([
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ])
        row = r45a.macro_candidate_for_var(formula, 1)
        self.assertIsNotNone(row)
        assert row is not None
        self.assertTrue(row["semantic_terminal_verified"])
        self.assertFalse(row["normalization"]["semantic_sat"])
        self.assertTrue(r45a.independent_macro_replay(formula, row)["pass"])

    def test_selector_is_deterministic_and_replay_checked(self) -> None:
        formula = r45a.r33.canonical_formula([
            (1, 2),
            (-1, 2),
            (3, 4),
            (-3, 4),
        ])
        a = r45a.select_macro(formula)
        b = r45a.select_macro(formula)
        self.assertEqual(a["candidate_digest_sha256"], b["candidate_digest_sha256"])
        self.assertEqual(
            a["selected"]["var"] if a["selected"] else None,
            b["selected"]["var"] if b["selected"] else None,
        )
        if a["selected"] is not None:
            self.assertTrue(a["selected_independent_replay"]["pass"])
        self.assertTrue(a["global_polynomial_scan_bounds"]["pass"])


if __name__ == "__main__":
    unittest.main()
