#!/usr/bin/env python3
"""Regression checker for the row-basis rank-3 matching router.

The theorem uses a standard polynomial general-graph matching algorithm after
branching only on basis columns of multiplicity three.  This small checker uses
an exact recursive matching routine on tiny fixtures so that CI needs no third-
party dependency; it validates semantics, reconstruction, counting identities,
and the 2n/5 exponent algebra.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json
import random


def rank_q(rows):
    if not rows:
        return 0
    a = [[Fraction(x) for x in row] for row in rows]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        z = a[r][c]
        a[r] = [v / z for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def actual_row_basis(A):
    chosen = []
    current = []
    old_rank = 0
    for i, row in enumerate(A):
        test = current + [row]
        new_rank = rank_q(test)
        if new_rank > old_rank:
            chosen.append(i)
            current = test
            old_rank = new_rank
    return chosen, current


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def brute_sat(A):
    n = len(A[0])
    target = [1] * len(A)
    for bits in product((0, 1), repeat=n):
        if matvec(A, bits) == target:
            return list(bits)
    return None


def matching_cover_mandatory(vertices, edges, mandatory):
    """Tiny exact checker for matching that saturates every mandatory vertex.

    `vertices` is the allowed vertex set.  Optional-optional edges never need to
    be selected, because optional unmatched vertices are completed by private
    variables.  Hence recursion only has to cover the first uncovered mandatory
    vertex.
    """

    vertices = set(vertices)
    mandatory = frozenset(mandatory)
    incident = {v: [] for v in vertices}
    for edge_id, u, v in edges:
        if u in vertices and v in vertices and u != v:
            incident[u].append((edge_id, v))
            incident[v].append((edge_id, u))

    memo = {}

    def rec(used, covered):
        key = (frozenset(used), frozenset(covered))
        if key in memo:
            return None
        if mandatory <= covered:
            return []
        u = min(mandatory - covered)
        if u in used:
            memo[key] = False
            return None
        for edge_id, v in incident.get(u, []):
            if v in used:
                continue
            got = rec(used | {u, v}, covered | ({u, v} & mandatory))
            if got is not None:
                return [edge_id] + got
        memo[key] = False
        return None

    return rec(set(), set())


def solve_rank3_router(A):
    n = len(A[0])
    basis_indices, B = actual_row_basis(A)
    r = len(B)
    k = n - r
    multiplicity = [sum(B[i][j] for i in range(r)) for j in range(n)]
    assert all(1 <= m <= 3 for m in multiplicity)

    N1 = [j for j, m in enumerate(multiplicity) if m == 1]
    N2 = [j for j, m in enumerate(multiplicity) if m == 2]
    N3 = [j for j, m in enumerate(multiplicity) if m == 3]
    n1, n2, h = len(N1), len(N2), len(N3)
    delta = 2 * n - 3 * k

    assert n1 + n2 + h == n
    assert n1 + 2 * n2 + 3 * h == 3 * r
    assert n2 + 2 * h == delta
    assert 2 * h <= delta

    privates = [[] for _ in range(r)]
    for j in N1:
        rows = [i for i in range(r) if B[i][j]]
        assert len(rows) == 1
        privates[rows[0]].append(j)

    pair_edges = []
    for j in N2:
        rows = [i for i in range(r) if B[i][j]]
        assert len(rows) == 2
        pair_edges.append((j, rows[0], rows[1]))

    for bits in product((0, 1), repeat=h):
        alpha = dict(zip(N3, bits))
        demand = []
        bad = False
        for i in range(r):
            fixed = sum(alpha[j] for j in N3 if B[i][j])
            b = 1 - fixed
            if b not in (0, 1):
                bad = True
                break
            demand.append(b)
        if bad:
            continue

        allowed = {i for i in range(r) if demand[i] == 1}
        mandatory = {i for i in allowed if not privates[i]}
        chosen_pair_vars = matching_cover_mandatory(allowed, pair_edges, mandatory)
        if chosen_pair_vars is None:
            continue

        x = [0] * n
        for j, value in alpha.items():
            x[j] = value
        selected_pair = set(chosen_pair_vars)
        matched_rows = set()
        for j, u, v in pair_edges:
            if j in selected_pair:
                x[j] = 1
                matched_rows.add(u)
                matched_rows.add(v)

        for i in allowed:
            if i not in matched_rows:
                assert privates[i], (i, demand, privates)
                x[privates[i][0]] = 1

        assert matvec(B, x) == [1] * r
        # RBO-2: satisfying the actual-row rational basis must satisfy all rows.
        assert matvec(A, x) == [1] * len(A)
        return {
            "witness": x,
            "basis_indices": basis_indices,
            "rank": r,
            "nullity": k,
            "delta": delta,
            "n1": n1,
            "n2": n2,
            "h": h,
        }

    return {
        "witness": None,
        "basis_indices": basis_indices,
        "rank": r,
        "nullity": k,
        "delta": delta,
        "n1": n1,
        "n2": n2,
        "h": h,
    }


def incidence_from_triples(n, triples):
    A = [[0] * n for _ in triples]
    for i, tri in enumerate(triples):
        assert len(set(tri)) == 3
        for j in tri:
            A[i][j] = 1
    return A


def is_cubic_linear_square(A):
    n = len(A)
    if any(len(row) != n or sum(row) != 3 for row in A):
        return False
    if any(sum(A[i][j] for i in range(n)) != 3 for j in range(n)):
        return False
    supports = [{j for j, x in enumerate(row) if x} for row in A]
    return all(len(supports[i] & supports[j]) <= 1 for i, j in combinations(range(n), 2))


def fano7():
    n = 7
    return incidence_from_triples(n, [[i, (i + 1) % n, (i + 3) % n] for i in range(n)])


def td33():
    n = 9
    def idx(x, y):
        return 3 * x + y
    triples = []
    for x in range(3):
        for y in range(3):
            triples.append([idx(x, y), idx((x + 1) % 3, y), idx(x, (y + 1) % 3)])
    return incidence_from_triples(n, triples)


def permutation_instance(n, p, q):
    triples = [[i, p[i], q[i]] for i in range(n)]
    A = incidence_from_triples(n, triples)
    return A


def random_linear_cubic_instances(seed=20260928, limit=24):
    rng = random.Random(seed)
    out = []
    for n in range(6, 10):
        attempts = 0
        while attempts < 3000 and len(out) < limit:
            attempts += 1
            p = list(range(n))
            q = list(range(n))
            rng.shuffle(p)
            rng.shuffle(q)
            if any(len({i, p[i], q[i]}) < 3 for i in range(n)):
                continue
            A = permutation_instance(n, p, q)
            if is_cubic_linear_square(A):
                out.append(A)
        if len(out) >= limit:
            break
    return out


def verify_fixture(name, A):
    assert is_cubic_linear_square(A), name
    brute = brute_sat(A)
    routed = solve_rank3_router(A)
    assert (brute is None) == (routed["witness"] is None), (name, brute, routed)
    if routed["witness"] is not None:
        assert matvec(A, routed["witness"]) == [1] * len(A)
    return {
        "name": name,
        "n": len(A),
        "rank": routed["rank"],
        "nullity": routed["nullity"],
        "delta": routed["delta"],
        "h": routed["h"],
        "sat": routed["witness"] is not None,
    }


def verify_exponent_bound(max_n=120):
    worst = (0.0, None)
    for n in range(1, max_n + 1):
        for k in range(0, (2 * n) // 3 + 1):
            delta = 2 * n - 3 * k
            # h is integral and h <= floor(delta/2).
            exponent = min(k, delta // 2)
            assert 5 * exponent <= 2 * n
            ratio = exponent / n
            if ratio > worst[0]:
                worst = (ratio, (n, k, delta, exponent))
    return worst


def main():
    fixtures = [
        verify_fixture("FANO7", fano7()),
        verify_fixture("TD33", td33()),
    ]
    for idx, A in enumerate(random_linear_cubic_instances()):
        fixtures.append(verify_fixture(f"RANDOM_{idx:02d}", A))

    worst_ratio, worst_tuple = verify_exponent_bound()
    assert worst_ratio <= 0.4

    out = {
        "status": "PASS_ROW_BASIS_RANK3_MATCHING_ROUTER",
        "fixtures_checked": len(fixtures),
        "fixtures": fixtures,
        "theorem": {
            "basis_router": "2^h poly(n)",
            "h_definition": "number of basis columns with multiplicity 3",
            "count_identity": "delta = n2 + 2h",
            "bound": "h <= delta/2",
            "combined_router": "2^min(k,h) poly(n)",
            "universal_exponent": "<= 2n/5",
            "residual": "k=omega(log n) AND h=omega(log n)",
        },
        "worst_small_integer_ratio": worst_ratio,
        "worst_small_integer_witness": worst_tuple,
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
