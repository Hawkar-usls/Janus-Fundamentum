#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
from math import gcd
import json


def idx(r: int, a: int, m: int) -> int:
    return r * m + a


def coord(i: int, m: int) -> tuple[int, int]:
    return divmod(i, m)


def family(m: int) -> tuple[list[int], list[int]]:
    n = 3 * m
    p = [0] * n
    q = [0] * n
    for r in range(3):
        for a in range(m):
            p[idx(r, a, m)] = idx((r + 1) % 3, a, m)
    for a in range(m):
        q[idx(0, a, m)] = idx(2, (a + 1) % m, m)
        q[idx(1, a, m)] = idx(0, a, m)
        q[idx(2, a, m)] = idx(1, a, m)
    u = idx(0, 0, m)
    v = idx(2, 2, m)
    q[u], q[v] = q[v], q[u]
    return p, q


def inv(p: list[int]) -> list[int]:
    z = [0] * len(p)
    for i, j in enumerate(p):
        z[j] = i
    return z


def compose(a: list[int], b: list[int]) -> list[int]:
    # a after b
    return [a[b[i]] for i in range(len(a))]


def commutator(p: list[int], q: list[int]) -> list[int]:
    return compose(p, compose(q, compose(inv(p), inv(q))))


def orbit_transitive(p: list[int], q: list[int]) -> bool:
    ip, iq = inv(p), inv(q)
    seen = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for perm in (p, q, ip, iq):
            v = perm[u]
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == len(p)


def long_cycle_from_zero(c: list[int]) -> list[int]:
    out = []
    u = 0
    while True:
        out.append(u)
        u = c[u]
        if u == 0:
            return out
        assert u not in out


def expected_cycle(m: int) -> list[tuple[int, int]]:
    return (
        [(0, 0), (2, 2), (2, 1), (1, 2), (2, 0)]
        + [(2, a) for a in range(m - 1, 2, -1)]
        + [(0, a) for a in range(1, m)]
    )


def check_m(m: int) -> dict:
    p, q = family(m)
    n = 3 * m
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    assert orbit_transitive(p, q)

    c = commutator(p, q)
    cyc = long_cycle_from_zero(c)
    got = [coord(x, m) for x in cyc]
    exp = expected_cycle(m)
    assert got == exp
    assert len(cyc) == 2 * m + 1

    C = set(cyc)
    F = set(range(n)) - C
    assert F == {idx(1, a, m) for a in range(m) if a != 2}
    assert all(c[x] == x for x in F)
    assert len(F) == m - 1
    assert len(C) > n // 2

    common = gcd(3 * m, 2 * m + 1)
    assert common in (1, 3)
    assert common == (3 if m % 3 == 1 else 1)

    arithmetic_exception_killed = None
    if m % 3 == 1:
        L = 2 * m + 1
        d = L // 3
        B = {cyc[0], cyc[d], cyc[2 * d]}
        PB = {p[x] for x in B}
        # P(0,0) is fixed by c, while P(c^d(0,0)) is on C.
        assert p[cyc[0]] in F
        assert p[cyc[d]] in C
        assert PB & C and PB & F
        arithmetic_exception_killed = True

    return {
        "m": m,
        "n": n,
        "commutator_long_cycle": len(C),
        "commutator_fixed": len(F),
        "gcd_block_bound": common,
        "arithmetic_exception_killed": arithmetic_exception_killed,
    }


controls = [check_m(m) for m in range(3, 61)]

result = {
    "status": "PASS_LOCAL_SWAP_PRIMITIVE_LINEAR_NULLITY_FAMILY",
    "checked_m_range": [3, 60],
    "symbolic_theorem": {
        "commutator_cycle_type": "(2m+1)(1)^(m-1)",
        "proper_block_size": "divides gcd(3m,2m+1), hence only possible size 3",
        "size3_case": "contradicted by P-image mixing long orbit and fixed set",
        "conclusion": "<P,Q'> primitive for every m>=3",
    },
    "parent_properties": {
        "SAT": True,
        "rational_nullity_lower_bound": "m=n/3",
        "linear_cubic": True,
        "connected": True,
        "noncommuting": True,
        "Z3_phase": "FAIL",
    },
    "boundary": {
        "primitive_implies_log_nullity": "FALSIFIED_ASYMPTOTICALLY",
        "universal_solver": "NOT_PROVED",
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    },
    "controls": controls,
}
print(json.dumps(result, sort_keys=True))
