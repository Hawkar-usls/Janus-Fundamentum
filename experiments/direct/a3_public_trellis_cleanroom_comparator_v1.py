#!/usr/bin/env python3
"""
A3 vs public trellis-theory reconstruction comparator.

Scientific role:
- PUBLIC_RECONSTRUCTION: implement only standard fixed-order matroid/trellis
  formulas (greedy first/last bases and connectivity profile) plus exhaustive
  coordinate-order search on small 1D generator-column multisets.
- A3_REIMPLEMENTATION_FROM_STATEMENT: independently implement the published
  A3 endpoint-state DP from its theorem statement, without importing A3 code.
- Compare optima and state-space sizes on deterministic small cases.

This is NOT an independent external replication: the implementer knows the A3
statement. It is a clean-code/no-import comparator and a semantic sanity check.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
from math import factorial
import json

def gf2_rank(vectors):
    basis = {}
    for x in [int(v) for v in vectors if int(v) != 0]:
        y = x
        while y:
            b = y.bit_length() - 1
            if b in basis:
                y ^= basis[b]
            else:
                basis[b] = y
                break
    return len(basis)

def unique_multiset_permutations(items):
    counts = Counter(items)
    keys = sorted(counts)
    n = len(items)
    out = []
    def rec():
        if len(out) == n:
            yield tuple(out)
            return
        for key in keys:
            if counts[key] > 0:
                counts[key] -= 1
                out.append(key)
                yield from rec()
                out.pop()
                counts[key] += 1
    yield from rec()

def greedy_first_base_positions(order, column_by_class):
    chosen = []
    positions = []
    r = 0
    for pos, cls in enumerate(order, start=1):
        v = column_by_class[cls]
        nr = gf2_rank(chosen + [v])
        if nr > r:
            chosen.append(v)
            positions.append(pos)
            r = nr
    return positions

def greedy_last_base_positions(order, column_by_class):
    chosen = []
    positions = []
    r = 0
    for pos in range(len(order), 0, -1):
        cls = order[pos - 1]
        v = column_by_class[cls]
        nr = gf2_rank(chosen + [v])
        if nr > r:
            chosen.append(v)
            positions.append(pos)
            r = nr
    return sorted(positions)

def public_first_last_profile(order, column_by_class):
    first = greedy_first_base_positions(order, column_by_class)
    last = greedy_last_base_positions(order, column_by_class)
    total_rank = gf2_rank([column_by_class[c] for c in order])
    profile = []
    for cut in range(len(order) + 1):
        prefix_rank = sum(1 for p in first if p <= cut)
        suffix_rank = sum(1 for p in last if p > cut)
        profile.append(prefix_rank + suffix_rank - total_rank)
    return profile, first, last

def direct_connectivity_profile(order, column_by_class):
    total_rank = gf2_rank([column_by_class[c] for c in order])
    return [
        gf2_rank([column_by_class[c] for c in order[:cut]])
        + gf2_rank([column_by_class[c] for c in order[cut:]])
        - total_rank
        for cut in range(len(order) + 1)
    ]

def public_exhaustive_optimum(multiplicities, column_by_class):
    items = []
    for cls, mult in enumerate(multiplicities):
        items.extend([cls] * mult)
    best = None
    best_order = None
    checked = 0
    first_last_identity_checked = 0
    for order in unique_multiset_permutations(items):
        checked += 1
        profile, _, _ = public_first_last_profile(order, column_by_class)
        direct = direct_connectivity_profile(order, column_by_class)
        if profile != direct:
            raise AssertionError(("first/last profile mismatch", order, profile, direct))
        first_last_identity_checked += 1
        width = max(profile)
        if best is None or width < best:
            best = width
            best_order = order
    return {
        "optimum": best,
        "best_order": list(best_order),
        "unique_coordinate_orders_checked": checked,
        "first_last_identity_checks": first_last_identity_checked,
    }

def rank_classes_1d(column_by_class, class_set):
    return gf2_rank([column_by_class[j] for j in class_set])

def a3_endpoint_dp_from_statement(multiplicities, column_by_class):
    k = len(multiplicities)
    repeated = [m >= 2 for m in multiplicities]
    radices = [3 if rep else 2 for rep in repeated]
    all_classes = set(range(k))
    total_rank = rank_classes_1d(column_by_class, all_classes)

    def state_width(state):
        finished = set()
        started = set()
        for j, status in enumerate(state):
            if repeated[j]:
                if status == 1:
                    started.add(j)
                elif status == 2:
                    finished.add(j)
                    started.add(j)
            else:
                if status == 1:
                    finished.add(j)
                    started.add(j)
        return (
            rank_classes_1d(column_by_class, started)
            + rank_classes_1d(column_by_class, all_classes - finished)
            - total_rank
        )

    states = list(product(*[range(r) for r in radices]))
    states.sort(key=sum)
    start = tuple(0 for _ in range(k))
    sink = tuple(2 if repeated[j] else 1 for j in range(k))
    dp = {start: state_width(start)}
    transitions_seen = 0

    for state in states:
        if state not in dp:
            continue
        for j, status in enumerate(state):
            nxt = None
            if repeated[j] and status < 2:
                tmp = list(state)
                tmp[j] = status + 1
                nxt = tuple(tmp)
            elif not repeated[j] and status == 0:
                tmp = list(state)
                tmp[j] = 1
                nxt = tuple(tmp)
            if nxt is None:
                continue
            transitions_seen += 1
            value = max(dp[state], state_width(nxt))
            if nxt not in dp or value < dp[nxt]:
                dp[nxt] = value

    s = sum(m == 1 for m in multiplicities)
    r = sum(m >= 2 for m in multiplicities)
    expected_states = (2 ** s) * (3 ** r)
    expected_transitions = (
        (s * (2 ** (s - 1)) * (3 ** r) if s else 0)
        + (2 * r * (2 ** s) * (3 ** (r - 1)) if r else 0)
    )
    assert len(states) == expected_states
    assert transitions_seen == expected_transitions
    return {
        "optimum": dp[sink],
        "states": len(states),
        "transitions": transitions_seen,
        "expected_states": expected_states,
        "expected_transitions": expected_transitions,
    }

CASES = [
    {
        "id": "R1_PARALLEL_REPEATS_WIDTH2",
        "columns_gf2": [1, 2, 3, 4],
        "multiplicities": [2, 2, 2, 1],
    },
    {
        "id": "R2_EXTRA_MIDDLE_COPY_SAME_ENDPOINT_GRAPH",
        "columns_gf2": [1, 2, 3, 4],
        "multiplicities": [3, 2, 2, 1],
    },
    {
        "id": "R3_ALL_REPEATED",
        "columns_gf2": [1, 2, 3, 4],
        "multiplicities": [2, 2, 2, 2],
    },
    {
        "id": "R4_FANO_SINGLETON_CONTROL",
        "columns_gf2": [1, 2, 3, 4, 5, 6, 7],
        "multiplicities": [1, 1, 1, 1, 1, 1, 1],
    },
    {
        "id": "R5_SMALL_MIXED_DEPENDENT",
        "columns_gf2": [1, 2, 3],
        "multiplicities": [3, 2, 1],
    },
]

def main():
    rows = []
    for case in CASES:
        pub = public_exhaustive_optimum(case["multiplicities"], case["columns_gf2"])
        a3 = a3_endpoint_dp_from_statement(case["multiplicities"], case["columns_gf2"])
        if pub["optimum"] != a3["optimum"]:
            raise AssertionError(("optimum mismatch", case["id"], pub, a3))
        rows.append({
            "case": case["id"],
            "columns_gf2": case["columns_gf2"],
            "multiplicities": case["multiplicities"],
            "public_exhaustive": pub,
            "a3_endpoint_dp": a3,
            "optimum_match": True,
            "search_space_ratio_unique_orders_over_a3_states":
                pub["unique_coordinate_orders_checked"] / a3["states"],
        })

    # Explicit multiplicity>=2 invariance check for the two related cases.
    r1 = next(x for x in rows if x["case"] == "R1_PARALLEL_REPEATS_WIDTH2")
    r2 = next(x for x in rows if x["case"] == "R2_EXTRA_MIDDLE_COPY_SAME_ENDPOINT_GRAPH")
    middle_copy_invariance = {
        "same_a3_state_count": r1["a3_endpoint_dp"]["states"] == r2["a3_endpoint_dp"]["states"],
        "same_a3_transition_count": r1["a3_endpoint_dp"]["transitions"] == r2["a3_endpoint_dp"]["transitions"],
        "same_optimum": r1["public_exhaustive"]["optimum"] == r2["public_exhaustive"]["optimum"],
        "public_search_orders_increase":
            r2["public_exhaustive"]["unique_coordinate_orders_checked"]
            > r1["public_exhaustive"]["unique_coordinate_orders_checked"],
    }
    assert all(middle_copy_invariance.values())

    receipt = {
        "schema": "janus.a3.cleanroom_trellis_reconstruction.v1",
        "authority": "NON_AUTHORITATIVE_RECONSTRUCTION_SANITY_CHECK",
        "scope": "GF(2) 1D generator-column / vector-matroid cases only",
        "independence_caveat":
            "No A3 implementation is imported, but the implementer knows the A3 theorem statement; this is not independent external replication.",
        "public_reconstruction":
            "Greedy first/last matroid bases + fixed-order connectivity/trellis profile + exhaustive unique coordinate permutations.",
        "a3_reimplementation":
            "Endpoint-state DP coded only from the public A3 theorem statement.",
        "cases": rows,
        "middle_copy_invariance_check": middle_copy_invariance,
        "verdict":
            "PASS_PUBLIC_TRELLIS_SEMANTICS_MATCH_A3_OPTIMUM_ON_DECLARED_SMALL_CASES__PUBLIC_RECONSTRUCTION_DOES_NOT_BY_ITSELF_ESTABLISH_A3_PRODUCT_QUOTIENT",
        "claim_ceiling": {
            "historical_novelty": "NOT_PROVED",
            "Papadopoulos_unpublished_manuscript_reconstructed": False,
            "external_independent_replication": False,
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
