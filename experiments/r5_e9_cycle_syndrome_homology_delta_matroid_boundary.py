#!/usr/bin/env python3
"""Finite regression for the cycle-syndrome homology identity.

OFFLINE_FALSIFIER_ONLY: the arbitrary-size theorem is in the companion markdown.
"""

from __future__ import annotations

import random


def compose_component_graph(p: list[int], q: list[int]) -> list[list[int]]:
    n = len(p)
    adj = [[] for _ in range(n)]
    for i in range(n):
        u, v = p[i], q[i]
        adj[u].append(v)
        adj[v].append(u)
    return adj


def components(adj: list[list[int]]) -> list[list[int]]:
    seen = [False] * len(adj)
    out: list[list[int]] = []
    for s in range(len(adj)):
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        out.append(comp)
    return out


def mat_vec_A(p: list[int], q: list[int], x: list[int]) -> list[int]:
    n = len(p)
    return [(x[i] ^ x[p[i]] ^ x[q[i]]) for i in range(n)]


def random_disjoint_perms(n: int, rng: random.Random) -> tuple[list[int], list[int]]:
    # Find P,Q such that I,P,Q have pairwise disjoint row support.
    while True:
        p = list(range(n))
        q = list(range(n))
        rng.shuffle(p)
        rng.shuffle(q)
        if all(p[i] != i and q[i] != i and p[i] != q[i] for i in range(n)):
            return p, q


def check_homology_identity() -> None:
    rng = random.Random(20260928)
    for n in range(6, 31):
        for _ in range(40):
            p, q = random_disjoint_perms(n, rng)
            adj = compose_component_graph(p, q)
            comps = components(adj)

            # P and Q are permutations, so every vertex has degree 2 (counting
            # multiplicity).  The exact component identity does not require
            # simplicity of this finite random control.
            assert all(len(a) == 2 for a in adj)

            indicators = []
            for comp in comps:
                x = [0] * n
                for v in comp:
                    x[v] = 1
                indicators.append(x)
                assert mat_vec_A(p, q, x) == x

                # XOR of the A-columns indexed by C equals A chi_C.
                col_xor = [0] * n
                for j in comp:
                    # Column j has ones in row j, row p^{-1}(j), row q^{-1}(j).
                    for i in range(n):
                        if i == j or p[i] == j or q[i] == j:
                            col_xor[i] ^= 1
                assert col_xor == x

            # Disjoint nonempty component indicators are linearly independent.
            # A direct support witness suffices: each component owns a private
            # coordinate absent from every other component indicator.
            for idx, comp in enumerate(comps):
                witness = comp[0]
                assert indicators[idx][witness] == 1
                assert all(
                    indicators[j][witness] == 0
                    for j in range(len(comps))
                    if j != idx
                )


def is_delta_matroid_03() -> bool:
    feasible = {frozenset(), frozenset({0, 1, 2})}
    for X in feasible:
        for Y in feasible:
            diff = X ^ Y
            for e in diff:
                ok = False
                for f in diff:
                    Z = set(X)
                    Z.symmetric_difference_update({e, f} if e != f else {e})
                    if frozenset(Z) in feasible:
                        ok = True
                        break
                if not ok:
                    return False
    return True


def main() -> None:
    check_homology_identity()
    assert not is_delta_matroid_03()
    print("PASS: cycle homology A*chi_C=chi_C and {0,3} delta-matroid barrier")


if __name__ == "__main__":
    main()
