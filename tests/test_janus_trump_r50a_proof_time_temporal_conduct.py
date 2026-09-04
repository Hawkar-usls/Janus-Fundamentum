from __future__ import annotations

import itertools
import unittest

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50a_proof_time_temporal_conduct as prooftime


class R50AProofTimeTests(unittest.TestCase):
    def setUp(self):
        self.formula = r33.canonical_formula([
            (1, 2, 3),
            (-1, 2, -3),
            (1, -2, -3),
            (-1, -2, 3),
        ])

    def first_model(self, formula):
        f = r33.canonical_formula(formula)
        variables = list(r33.variables(f))
        for bits in itertools.product((False, True), repeat=len(variables)):
            assignment = dict(zip(variables, bits))
            if r33.eval_formula(f, assignment):
                return assignment
        return None

    def test_wait_is_explicit_nonexecution_before_authority(self):
        token = r50a.operational_token(self.formula, 1)
        receipt = prooftime.wait_for_authority(self.formula, token)
        self.assertEqual(receipt["status"], "WAIT_FOR_AUTHORITY")
        self.assertFalse(receipt["execution_allowed"])
        self.assertTrue(receipt["logical_time_only"])
        self.assertFalse(receipt["wall_clock_used"])
        self.assertEqual(receipt["events"][-1]["phase"], "WAIT_FOR_AUTHORITY")

    def test_recompute_can_authorize_current_exact_token(self):
        token = r50a.operational_token(self.formula, 1)
        auth = prooftime.authorize_after_recompute(self.formula, token)
        self.assertEqual(auth["status"], "AUTHORIZED_CURRENT")
        self.assertTrue(auth["carrier_matches_current_recomputation"])
        self.assertTrue(auth["direct_exact_dp_authorized"])
        self.assertTrue(auth["execution_allowed"])
        self.assertEqual([e["phase"] for e in auth["events"]], ["WAIT_FOR_AUTHORITY", "RECOMPUTE", "VERIFY"])

    def test_tampered_carrier_never_gains_authority(self):
        token = r50a.operational_token(self.formula, 1)
        tampered = dict(token)
        tampered["chi_star"] += 1
        auth = prooftime.authorize_after_recompute(self.formula, tampered)
        self.assertEqual(auth["status"], "WAIT_FOR_AUTHORITY")
        self.assertFalse(auth["carrier_matches_current_recomputation"])
        self.assertFalse(auth["execution_allowed"])
        self.assertFalse(auth["events"][-1]["pass"])

    def test_direct_step_has_proof_time_receipt(self):
        token = r50a.operational_token(self.formula, 1)
        step = r50a._direct_dp_transition(self.formula, token)
        receipt = prooftime.audit_temporal_step(self.formula, step)
        self.assertEqual(receipt["status"], "PASS")
        phases = [e["phase"] for e in receipt["events"]]
        self.assertEqual(phases, [
            "OBSERVE", "EXPOSE", "WAIT_FOR_AUTHORITY", "RECOMPUTE", "VERIFY",
            "EXECUTE", "REPLAY", "RETURN_OR_RECONSTRUCT", "SEAL_OR_REMAIN_OPEN",
        ])
        self.assertEqual([e["logical_tick"] for e in receipt["events"]], list(range(len(receipt["events"]))))

    def test_reverse_return_completes_style_obligation(self):
        token = r50a.operational_token(self.formula, 1)
        step = r50a._direct_dp_transition(self.formula, token)
        model = self.first_model(step["successor"])
        self.assertIsNotNone(model)
        result = prooftime.audit_reverse_return(self.formula, step, model)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["reverse_replay"]["pass"])
        self.assertTrue(r33.eval_formula(self.formula, result["reverse_replay"]["assignment"]))


if __name__ == "__main__":
    unittest.main()
