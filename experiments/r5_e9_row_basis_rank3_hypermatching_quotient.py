#!/usr/bin/env python3
"""Finite replay for the row-basis rank-3 hypermatching quotient.

The arbitrary-size theorem uses standard polynomial maximum-weight matching after
enumerating size-3 basis hyperedges.  This checker validates the exact quotient,
multiplicity identities, and witness equivalence on tiny frozen controls only.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        q = A[r][c]
        A[r] = [x / q for x in A[r]]
        for i in range(r + 1, m):
            if A[i][c] != 0:
                q = A[i][c]
                A[i] = [A[i][j] - q * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def matrix(rows, n):
    A = [[0] * n for _ in rows]
    for i, row in enumerate(rows):
        for v in row:
            A[i][v] = 1
    return A


def actual_row_basis(A):
    chosen = []
    cur = 0
    for i in range(len(A)):
        trial = [A[j][:] for j in chosen + [i]]
        rr = rank_q(trial)
        if rr > cur:
            chosen.append(i)
            cur = rr
    assert cur == rank_q(A)
    return chosen


def verify_exact_one(rows, x):
    return all(sum(x[v] for v in row) == 1 for row in rows)


def basis_hypergraph(rows, n):
    A = matrix(rows, n)
    basis = actual_row_basis(A)
    r = len(basis)
    k = n - r

    supports = []
    for j in range(n):
        e = tuple(ii for ii, bi in enumerate(basis) if A[bi][j])
        assert 1 <= len(e) <= 3
        supports.append(e)

    # Every basis-row vertex has degree exactly three in the quotient hypergraph.
    vdeg = [0] * r
    for e in supports:
        for u in e:
            vdeg[u] += 1
    assert vdeg == [3] * r

    p = sum(len(e) == 1 for e in supports)
    s = sum(len(e) == 2 for e in supports)
    t = sum(len(e) == 3 for e in supports)
    delta = 3 * r - n

    assert p + s + t == n
    assert 3 * k == 2 * p + s
    assert delta == s + 2 * t
    assert t - p == n - 3 * k
    assert t >= n - 3 * k
    assert 2 * t <= delta

    return {
        "A": A,
        "basis": basis,
        "supports": supports,
        "r": r,
        "k": k,
        "p": p,
        "s": s,
        "t": t,
        "delta": delta,
    }


def exact_cover_from_x(H, x):
    covered = [0] * H["r"]
    for j, bit in enumerate(x):
        if bit:
            for u in H["supports"][j]:
                covered[u] += 1
    return covered == [1] * H["r"]


def brute_hyper_exact_cover(H):
    n = len(H["supports"])
    for bits in product((0, 1), repeat=n):
        if exact_cover_from_x(H, bits):
            return bits
    return None


def brute_source(rows, n):
    for bits in product((0, 1), repeat=n):
        if verify_exact_one(rows, bits):
            return bits
    return None


def matching_residual_bruteforce(H, triple_bits):
    """Tiny-control replay of the theorem's post-triple graph-matching residual."""
    supports = H["supports"]
    triples = [j for j, e in enumerate(supports) if len(e) == 3]
    assert len(triple_bits) == len(triples)

    selected_triples = [triples[i] for i, b in enumerate(triple_bits) if b]
    covered = set()
    for j in selected_triples:
        e = set(supports[j])
        if covered & e:
            return None
        covered |= e

    U = [u for u in range(H["r"]) if u not in covered]
    Uset = set(U)
    singletons = [j for j, e in enumerate(supports) if len(e) == 1 and set(e) <= Uset]
    pairs = [j for j, e in enumerate(supports) if len(e) == 2 and set(e) <= Uset]
    has_singleton = {supports[j][0] for j in singletons}
    mandatory = set(U) - has_singleton

    # Exhaustive matching only for tiny controls.  The theorem uses polynomial
    # maximum-weight matching in the arbitrary-size algorithm.
    for mask in range(1 << len(pairs)):
        used = set()
        picked = []
        ok = True
        for i, j in enumerate(pairs):
            if (mask >> i) & 1:
                e = set(supports[j])
                if used & e:
                    ok = False
                    break
                used |= e
                picked.append(j)
        if not ok or not mandatory <= used:
            continue
        # Every unmatched optional vertex has an available singleton.
        selected = set(selected_triples) | set(picked)
        for u in U:
            if u in used:
                continue
            cand = next((j for j in singletons if supports[j] == (u,)), None)
            if cand is None:
                ok = False
                break
            selected.add(cand)
        if ok:
            x = tuple(1 if j in selected else 0 for j in range(len(supports)))
            assert exact_cover_from_x(H, x)
            return x
    return None


def routed_witness(H):
    triples = [j for j, e in enumerate(H["supports"]) if len(e) == 3]
    for bits in product((0, 1), repeat=len(triples)):
        got = matching_residual_bruteforce(H, bits)
        if got is not None:
            return got
    return None


FANO7 = [
    (0, 1, 2), (0, 3, 4), (0, 5, 6),
    (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5),
]

AFFINE3X3 = []
for rr in range(3):
    AFFINE3X3.append(tuple(3 * rr + c for c in range(3)))
for c in range(3):
    AFFINE3X3.append(tuple(3 * rr + c for rr in range(3)))
for d in range(3):
    AFFINE3X3.append(tuple(3 * rr + ((rr + d) % 3) for rr in range(3)))

UNSAT9 = [
    (3, 6, 7), (2, 3, 4), (0, 3, 8), (2, 5, 8), (0, 4, 7),
    (1, 4, 8), (1, 5, 7), (1, 2, 6), (0, 5, 6),
]

controls = []
for name, rows, n in [
    ("FANO7", FANO7, 7),
    ("AFFINE_3X3", AFFINE3X3, 9),
    ("CONNECTED_LINEAR_CUBIC_UNSAT9", UNSAT9, 9),
]:
    H = basis_hypergraph(rows, n)
    source = brute_source(rows, n)
    hyper = brute_hyper_exact_cover(H)
    routed = routed_witness(H)
    assert (source is not None) == (hyper is not None) == (routed is not None)
    if routed is not None:
        assert verify_exact_one(rows, routed)
    controls.append({
        "name": name,
        "n": n,
        "rank_Q": H["r"],
        "nullity_Q": H["k"],
        "p_size1": H["p"],
        "s_size2": H["s"],
        "t_size3": H["t"],
        "delta": H["delta"],
        "sat": source is not None,
    })

print(json.dumps({
    "status": "PASS_ROW_BASIS_RANK3_HYPERMATCHING_QUOTIENT_FINITE_REPLAY",
    "role": "OFFLINE_FALSIFIER_ONLY",
    "semantic_quotient": "Bx=1_IFF_SELECTED_COLUMN_SUPPORT_HYPEREDGES_EXACTLY_COVER_BASIS_ROWS",
    "identities": ["3k=2p+s", "delta=s+2t", "t-p=n-3k"],
    "router": "2^t_B*poly(n,L)",
    "post_triple_residual": "GENERAL_GRAPH_MATCHING_WITH_MANDATORY_VERTICES",
    "hard_slab_basis_lower_bound": "k<=n/6_IMPLIES_t_B>=n/2_FOR_EVERY_ACTUAL_ROW_BASIS",
    "controls": controls,
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
