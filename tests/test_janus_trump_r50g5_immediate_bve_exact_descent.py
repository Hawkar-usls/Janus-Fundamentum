import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
if str(EXP) not in sys.path:
    sys.path.insert(0, str(EXP))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5


def _find_frozen_escape():
    # Deterministic frozen R50G4 lineage only; test evidence, never theorem authority.
    for worker in range(5):
        n = 6 + worker
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            state, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(state)) != n:
                continue
            seen = set()
            for _ in range(8 * n + 4 * max(1, len(state)) + 32):
                h = r50g4.fhash(state)
                if h in seen:
                    break
                seen.add(h)
                if r50g4.micro_r33_status(state)["status"] == "IMMEDIATE_BVE_W4_ESCAPE":
                    return state
                step = r50g4.refined_exact_step(state)
                if step["kind"] in ("TERMINAL", "OPEN_OBSTRUCTION"):
                    break
                state = r33.canonical_formula(step["successor"])
    raise AssertionError("frozen R50G4 escape witness disappeared")


def test_immediate_bve_same_pivot_theorem_mechanics():
    state = _find_frozen_escape()
    out = r50g5.prove_immediate_bve_same_pivot(state)
    assert out["applicable"] is True
    assert out["same_pivot_R47J_legacy_accepted"] is True
    assert out["strict_CLV_descent_proved"] is True
    assert out["no_fresh_variables_proved"] is True
    assert out["strict_variable_descent_proved"] is True
    assert out["independent_replay_pass"] is True
    assert out["polynomial_per_transition_envelope_pass"] is True
    assert out["same_pivot_R47J_machine_safe"] == (
        out["same_pivot_terminal"] or out["final_width"] <= 4
    )


def test_firewall_has_no_heuristic_authority():
    fw = r50g5.firewall()
    assert fw["HEURISTIC_AUTHORITY"] is False
    assert fw["LEARNED_SELECTOR"] is False
    assert fw["PROBABILISTIC_AUTHORITY"] is False
    assert fw["FINITE_REPLAY_IMPLIES_UNIVERSAL_THEOREM"] is False
    assert fw["U_MU"] == "OPEN"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
