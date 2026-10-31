"""DOVOD-SHA historic negative-control: no ML execution or proof claim."""
import ast
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/"archive"/"nas_dovod_sha_20261031"

class DovodScientificBoundaries(unittest.TestCase):
    def test_original_script_parses_without_import_or_execution(self):
        content=(ROOT/"original"/"DOVOD-SHA.py").read_text(encoding="utf-8")
        ast.parse(content)
        self.assertIn("TRAIN_STEPS",content)
        self.assertIn("THRESHOLD_LOSS",content)
    def test_real_leakage_report_is_negative_control(self):
        data=json.loads((ROOT/"reports"/"leakage_audit.json").read_text())
        self.assertEqual(data["train_sequences"],200)
        self.assertEqual(data["test_sequences"],50)
        self.assertFalse(data["train_test_independence"])
        self.assertEqual(data["exact_cross_split_duplicate_test_sequences"],25)
        self.assertEqual(data["shared_block_id_count"],50)
        self.assertTrue(data["memorization_explanation_possible"])
    def test_nas_policy_and_claims_are_frozen(self):
        methodology=json.loads((ROOT/"reports"/"methodology_audit.json").read_text())
        gate=json.loads((ROOT/"configs"/"preregistered_gate_profile.json").read_text())
        resources=json.loads((ROOT/"reports"/"resource_estimate.json").read_text())
        self.assertEqual(methodology["claim_level"],"NO_SHA256_PREDICTABILITY_CLAIM")
        self.assertEqual(gate["claim_level"],"NO_SHA256_PREDICTABILITY_CLAIM")
        self.assertFalse(gate["adaptive_threshold_changes_allowed"])
        self.assertFalse(resources["nas_training_allowed"])
        self.assertFalse(methodology["test_data"]["holdout"])
        self.assertAlmostEqual(methodology["threshold"]["uniform_byte_cross_entropy"],math.log(256),places=6)
        self.assertFalse(methodology["checkpoint_persistence"])
    def test_no_new_weights_or_checkpoint_assets(self):
        self.assertFalse(list(ROOT.rglob("*.pt")))
        self.assertFalse(list(ROOT.rglob("*.pkl")))
        self.assertFalse(list(ROOT.rglob("*.ckpt")))

if __name__=="__main__":
    unittest.main()
