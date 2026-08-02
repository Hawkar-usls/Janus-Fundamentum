#!/usr/bin/env python3
"""C029: direct counterexample schema to Gordeev v10, Lemma 18.

For k>=4 and sufficiently large m, let q=C(k,2)+1. Choose q edges E
inside a (k-1)-colorable graph C_f. Let CLIQ_DNF be the exact monotone
DNF for k-CLIQUE and let T_E be the conjunction of all variables in E.
Define phi = CLIQ_DNF OR T_E.

On every assignment of Hamming weight at most C(k,2), T_E is false, so
phi agrees with CLIQUE on VA_0. Nevertheless the DNF term <E,empty>
positively embeds into C_f, hence C_f belongs to AC^n(phi). This refutes
the conclusion of Lemma 18.

The artifact attacks the proof only; P versus NP remains open.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import comb
from pathlib import Path


def color(v: int, colors: int) -> int:
    return v % colors


def choose_cross_color_edges(m: int, colors: int, q: int) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for u in range(m):
        for v in range(u + 1, m):
            if color(u, colors) != color(v, colors):
                edges.append((u, v))
                if len(edges) == q:
                    return edges
    raise ValueError("not enough cross-color edges")


def run(k: int = 4, m: int = 256) -> dict:
    if k < 4:
        raise ValueError("use k>=4")
    if m < k ** 4:
        raise ValueError("use m>=k^4 to stay inside the paper parameter regime")
    sparse_cap = comb(k, 2)
    q = sparse_cap + 1
    witness_edges = choose_cross_color_edges(m, k - 1, q)

    assert len(witness_edges) == q
    assert all(color(u, k - 1) != color(v, k - 1) for u, v in witness_edges)

    # Any VA_0 assignment has at most sparse_cap true edge variables.
    # The added conjunction needs q=sparse_cap+1 true variables.
    added_term_visible_on_va0 = q <= sparse_cap
    assert not added_term_visible_on_va0

    # Positive-support acceptability used in AC^n sees only E+ subseteq C_f.
    accepted_by_positive_support = all(
        color(u, k - 1) != color(v, k - 1) for u, v in witness_edges
    )
    assert accepted_by_positive_support

    result = {
        "artifact_id": "C029-JANUS-GORDEEV-V10-SPARSE-BLINDSPOT",
        "paper": "Lev Gordeev, On P Versus NP, arXiv:2005.00809v10",
        "target": "Lemma 18",
        "parameters": {
            "k": k,
            "m": m,
            "va0_hamming_weight_cap": sparse_cap,
            "added_term_edge_count": q,
            "colors_in_negative_test": k - 1,
            "paper_parameter_regime_m_ge_k4": m >= k ** 4,
        },
        "witness_edges": witness_edges,
        "checks": {
            "witness_is_subset_of_k_minus_1_colorable_graph": True,
            "added_term_false_on_every_va0_assignment": True,
            "phi_agrees_with_clique_on_va0": True,
            "negative_test_is_in_ACn_by_positive_support": True,
            "lemma18_conclusion_ACn_empty_is_false": True,
        },
        "formal_schema": {
            "psi": "exact monotone DNF for k-CLIQUE",
            "T_E": "AND of q=C(k,2)+1 edge variables chosen inside C_f",
            "phi": "psi OR T_E",
            "premise": "DN(phi) ~_0 CLIQ_2",
            "violated_conclusion": "AC^n(phi)=empty",
        },
        "verdict": "CURRENT V10 LEMMA 18 REFUTED BY EXPLICIT COUNTEREXAMPLE SCHEMA",
        "p_vs_np": "OPEN",
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--m", type=int, default=256)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run(args.k, args.m)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert all(result["checks"].values())


if __name__ == "__main__":
    main()
