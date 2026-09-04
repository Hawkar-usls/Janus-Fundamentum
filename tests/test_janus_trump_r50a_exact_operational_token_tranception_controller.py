from __future__ import annotations

import itertools
import unittest

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a


class R50AExactControllerTests(unittest.TestCase):
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

    def test_operational_token_is_exact_and_tamper_evident(self):
        token = r50a.operational_token(self.formula, 1)
        self.assertTrue(token["bipolar"])
        self.assertTrue(token["direct_exact_dp_authorized"])
        self.assertTrue(r50a.verify_operational_token(self.formula, token)["pass"])
        bad = dict(token)
        bad["chi_star"] += 1
        self.assertFalse(r50a.verify_operational_token(self.formula, bad)["pass"])

    def test_all_tokens_are_exposed_without_ranker(self):
        tokens = r50a.expose_exact_tokens(self.formula)
        self.assertEqual([t["pivot"] for t in tokens], sorted(r33.variables(self.formula)))
        self.assertEqual(len(tokens), len(r33.variables(self.formula)))

    def test_exact_step_has_no_heuristic_authority(self):
        step = r50a.exact_step(self.formula)
        self.assertFalse(step["heuristic_ranking_used"])
        self.assertIn(step["kind"], {"NONTERMINAL", "TERMINAL"})
        if step["kind"] == "NONTERMINAL":
            self.assertLessEqual(step["successor_max_width"], 4)

    def test_direct_carrier_executes_only_after_recompute_and_replay(self):
        token = r50a.operational_token(self.formula, 1)
        step = r50a._direct_dp_transition(self.formula, token)
        self.assertEqual(step["lane"], "BLUEFIELD_EXACT_TOKEN__R49H_DIRECT_DP")
        self.assertTrue(step["token_verification"]["pass"])
        self.assertTrue(step["transition_certificate"]["DP_independent_replay"]["pass"])
        self.assertTrue(step["transition_certificate"]["polynomial_intermediate_envelope"]["pass"])
        self.assertLessEqual(step["successor_max_width"], 4)
        self.assertTrue(step["strict_variable_descent"])

    def test_tranception_reverse_returns_valid_predecessor_model(self):
        token = r50a.operational_token(self.formula, 1)
        step = r50a._direct_dp_transition(self.formula, token)
        model = self.first_model(step["successor"])
        self.assertIsNotNone(model)
        replay = r50a.reverse_sat_witness(self.formula, step, model)
        self.assertTrue(replay["pass"])
        self.assertTrue(r33.eval_formula(self.formula, replay["assignment"]))

    def test_demo_keeps_p_vs_np_open(self):
        out = r50a.demo()
        self.assertEqual(out["verdict"], "PASS")
        self.assertFalse(out["firewall"]["HEURISTIC_RANKER_AUTHORITY"])
        self.assertEqual(out["firewall"]["P_VS_NP"], "OPEN")
        self.assertFalse(out["firewall"]["TRUMP_finished"])


if __name__ == "__main__":
    unittest.main()
