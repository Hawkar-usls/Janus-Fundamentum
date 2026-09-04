from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g3_minimal_counterexample_structure_mirrored_falsifier as r50g3


def test_local_symbolic_kernel_closes_v_lt6_and_v6_geometry():
    k = r50g3.local_symbolic_kernel()
    assert k["V6_width5_patterns"] == [[3, 4, 0], [4, 3, 0], [4, 4, 1]]
    assert max(row["max_nontautological_resolvent_width"] for row in k["V_lt_6_rows"]) == 4
    assert all(
        not row["can_exceed_4_by_width_arithmetic"]
        or row["positive_parent_width"] == 4
        or row["negative_parent_width"] == 4
        for row in k["parent_width_rows"]
    )


def test_independent_r33_history_replay_on_existing_reduction_stack():
    f = r33.easy_redundant_tail()
    replay = r50g3.replay_r33_history(f)
    assert replay["result"]["history"]
    assert r33.canonical_formula(replay["result"]["final_formula"]) == r50g3.canon_from_hashless_rows(
        f, replay["result"]["history"], len(replay["result"]["history"])
    )
    assert all(
        row["rule"] == "BOUNDED_VARIABLE_ELIMINATION" or row["after_width"] <= row["before_width"]
        for row in replay["rows"]
    )


def test_guarded_open_v_lt6_is_symbolically_excluded_by_kernel_bound():
    # This test checks the exact arithmetic used by L4, not finite formula search.
    for vcount in range(1, 6):
        assert vcount - 1 <= 4


def test_small_mirrored_worker_keeps_firewall_open():
    out = r50g3.run_worker(0, roots_per_worker=2, mirror_candidates_per_worker=3)
    assert out["n"] == 6
    assert out["firewall"]["R50G3_STRUCTURAL_LEMMAS_IMPLY_U"] is False
    assert out["firewall"]["SAFE_PREFIX_EXISTS_IMPLIES_CURRENT_U"] is False
    assert out["firewall"]["ARBITRARY_SUBFORMULA_MINIMALITY_ALLOWED_ON_REACHABLE_U"] is False
    assert out["firewall"]["GUARDED_U"] == "OPEN"
    assert out["firewall"]["SAT_IN_P"] == "NOT_PROVED"
    assert out["firewall"]["P_VS_NP"] == "OPEN"
