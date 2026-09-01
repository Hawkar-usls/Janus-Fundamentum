#!/usr/bin/env python3
from __future__ import annotations

import inspect

import janus_trump_r12b_forbidden_pattern_quotient_compiler as r12b
import janus_trump_r12_direct_width4_interface_compiler as r12


def test_r12b_canonical_name_content_control():
    assert r12b.canonical_clause((2, 1, 1)) == r12b.canonical_clause((1, 2))
    assert r12b.canonical_clause((1, 2)) != r12b.canonical_clause((1, -2))
    assert r12b.canonical_clause((1, -1)) is None


def test_r12b_resolution_replays():
    f = ((1, 2), (-1, 3))
    q = r12b.saturate_forbidden_pattern_basis(f, wall_seconds=2, progress_label="test")
    assert q["status"] == "FIXED_POINT"
    target = r12b.canonical_clause((2, 3))
    assert target in q["active"] or any(r12b.clause_subsumes(c, target) for c in q["active"])
    assert r12b.replay_proof(q, f) is True


def test_r12b_subsumption_is_exact_semantic_dominance():
    f = ((1, 2, 3), (1, 2), (1,))
    q = r12b.saturate_forbidden_pattern_basis(f, wall_seconds=2, progress_label="test_dom")
    assert q["status"] == "FIXED_POINT"
    assert q["active"] == {r12b.canonical_clause((1,))}
    assert q["stats"]["active_weaker_states_removed"] >= 1 or q["stats"]["dominated_new_states_collapsed"] >= 1


def test_r12b_tiny_basis_matches_naive_width4_closure():
    f = ((1, 2), (-1, 3), (-2, 4), (-3, -4))
    naive = r12.saturate_width4(f)
    q = r12b.saturate_forbidden_pattern_basis(f, wall_seconds=2, progress_label="test_equiv")
    assert q["status"] == "FIXED_POINT"
    assert r12b.minimal_basis(naive["clauses"]) == tuple(sorted(q["active"], key=lambda c: (len(c), c)))


def test_r12b_candidate_firewall_and_poly_state_bound():
    fw = r12b.candidate_firewall()
    assert fw["pass"], fw
    for n in (1, 4, 10, 25):
        assert r12b.state_universe_bound(n) >= 1
    src = inspect.getsource(r12b.saturate_forbidden_pattern_basis)
    assert "shadow_exact_interface" not in src
    assert "dpll(" not in src
    assert "range(1 <<" not in src
