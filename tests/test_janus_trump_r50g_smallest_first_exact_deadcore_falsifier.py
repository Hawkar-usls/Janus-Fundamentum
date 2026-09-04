from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g


def test_planted_generators_directly_verify_false_witness():
    for profile in ("3CNF", "W34", "W234", "W4_CONTROL"):
        f, a = r50g.make_planted(50700001, 7, 20, profile)
        assert r33.eval_formula(f, a)
        assert r50g.max_width(f) <= (3 if profile == "3CNF" else 4)
        assert all(any(l < 0 for l in c) for c in f)


def test_width5_requires_at_least_one_width4_parent():
    f = r50g.canon([
        (1, 2, 3, 4),
        (-1, 5, 6),
    ])
    rows = r50g.bad_pair_shape_lemma(f, 1)
    assert rows == [{"positive_width": 4, "negative_width": 3, "resolvent_width": 5}]


def test_width6_requires_width4_times_width4():
    f = r50g.canon([
        (1, 2, 3, 4),
        (-1, 5, 6, 7),
    ])
    rows = r50g.bad_pair_shape_lemma(f, 1)
    assert rows == [{"positive_width": 4, "negative_width": 4, "resolvent_width": 6}]


def test_two_width3_parents_cannot_make_wide_resolvent():
    f = r50g.canon([
        (1, 2, 3),
        (-1, 4, 5),
    ])
    assert r50g.bad_pair_shape_lemma(f, 1) == []
    p = r49i.variable_profile(f, 1)
    assert p["chi_star"] == 4


def test_at_most_five_variables_force_chi_star_at_most_four():
    # Exhaust every possible non-tautological residual literal selection for a
    # pivot over four remaining variables: a clause cannot contain two signs of
    # the same variable without becoming tautological, hence width <=4.
    f = r50g.canon([
        (1, 2, 3, 4),
        (-1, 2, -3, 5),
        (1, -2, 4, -5),
        (-1, -2, -4, 5),
    ])
    assert len(r33.variables(f)) == 5
    assert r49i.variable_profile(f, 1)["chi_star"] <= 4


def test_candidate_key_is_smallest_first_v_c_l_hash():
    a = {"CLV": [20, 60, 6], "hash": "b"}
    b = {"CLV": [18, 55, 7], "hash": "a"}
    c = {"CLV": [21, 59, 6], "hash": "a"}
    assert sorted((a, b, c), key=r50g.candidate_key) == [a, c, b]


def test_firewall_never_promotes_no_find_to_u():
    fw = r50g.firewall(False, False)
    assert fw["U_FOR_FROZEN_REACHABLE_MACHINE"] == "OPEN"
    assert fw["NO_DEADCORE_FOUND_IMPLIES_U"] is False
    assert fw["GENERATED_POOL_SMALLEST_IS_GLOBAL_MINIMUM"] is False
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False
