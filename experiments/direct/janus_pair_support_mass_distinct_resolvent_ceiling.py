#!/usr/bin/env python3
"""Regression for the C025 pair-support-mass distinct-resolvent ceiling.

The JSON artifact contains the proof. This executable protects the combinatorial
arithmetic, exhaustively checks small unit-free canonical CNFs, and replays the
N57 abstract coarse-alarm specimen. P vs NP remains OPEN.
"""

from itertools import combinations, product
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def width_universe_count(r: int, w: int) -> int:
    return comb(r, w) * (2 ** w)


def wmax(r: int, R: int) -> int:
    rem = max(0, R)
    total = 0
    for w in range(r, -1, -1):
        take = min(rem, width_universe_count(r, w))
        total += take * w
        rem -= take
        if rem == 0:
            break
    assert rem == 0, (r, R)
    return total


def omission_product_max(p: int, q: int, o: int) -> int:
    best = 0
    for a in range(min(p, o) + 1):
        for b in range(min(q, o - a) + 1):
            best = max(best, a * b)
    return best


def distinct_resolvent_ceiling(n: int, m: int, d: int, p: int, q: int) -> int:
    if p == 0 or q == 0:
        return 0
    r = n - 1
    c = m - d
    pq = p * q
    o = min(d, c)
    M = omission_product_max(p, q, o)
    smin = r * (pq - M)
    max_R = min(pq, 3 ** r)
    feasible = 0
    for R in range(max_R + 1):
        upper = wmax(r, R) + (pq - R) * r
        if upper >= smin:
            feasible = R
        else:
            break
    return feasible


def raw_units_ceiling(n: int, m: int, d: int, p: int, q: int) -> int:
    r = n - 1
    c = m - d
    R = distinct_resolvent_ceiling(n, m, d, p, q)
    return 1 + c * (r + 1) + R + wmax(r, R)


def all_unitfree_clauses(n: int):
    out = []
    for w in range(2, n + 1):
        for support in combinations(range(1, n + 1), w):
            for signs in product((1, -1), repeat=w):
                out.append(tuple(v * s for v, s in zip(support, signs)))
    return tuple(core.canon_clause(c) for c in out)


def verify_small_exhaustive() -> None:
    clauses = all_unitfree_clauses(3)
    checked = 0
    for m in range(2, 5):
        for chosen in combinations(clauses, m):
            cnf = core.canon_cnf(chosen)
            if len(cnf) != m or not core.vars_of(cnf):
                continue
            live = core.vars_of(cnf)
            degrees = {v: v05.incidence_degree(cnf, v) for v in live}
            dmin = min(degrees.values())
            pivot = min(v for v in live if degrees[v] == dmin)
            p = sum(pivot in c for c in cnf)
            q = sum(-pivot in c for c in cnf)
            Rcap = distinct_resolvent_ceiling(len(live), m, dmin, p, q)

            out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
            assert out is not None
            # Rebuild the pre-canonical raw set exactly to count distinct resolvents.
            pos = [c for c in cnf if pivot in c]
            neg = [c for c in cnf if -pivot in c]
            resolvents = set()
            for left in pos:
                for right in neg:
                    rr = core.resolve_on_var(left, right, pivot)
                    if rr is not None:
                        resolvents.add(rr)
            assert len(resolvents) <= Rcap, (cnf, pivot, len(resolvents), Rcap)
            assert stats['raw_units'] <= raw_units_ceiling(len(live), m, dmin, p, q)
            checked += 1
    print(f'PAIR_SUPPORT_SMALL_EXHAUSTIVE=PASS:{checked}')


def verify_n57_specimen() -> None:
    n, m, d, p, q = 7, 59, 43, 18, 25
    r, c, o = 6, 16, 16
    assert omission_product_max(p, q, o) == 64
    assert r * (p * q - 64) == 2316
    R = distinct_resolvent_ceiling(n, m, d, p, q)
    assert R == 352, R
    assert wmax(6, 352) == 1728
    raw = raw_units_ceiling(n, m, d, p, q)
    assert raw == 2193, raw
    assert raw < 57 * 57
    print('PAIR_SUPPORT_N57_R_CEILING=352')
    print('PAIR_SUPPORT_N57_WMAX=1728')
    print('PAIR_SUPPORT_N57_RAW_CEILING=2193')
    print('PAIR_SUPPORT_N57_COARSE_ALARM_REPAIRED=PASS')


def verify_monotonic_support_upper() -> None:
    for r in range(1, 8):
        prev = None
        for R in range(0, min(100, 3 ** r) + 1):
            val = wmax(r, R) - R * r
            if prev is not None:
                assert val <= prev
            prev = val
    print('PAIR_SUPPORT_F_OF_R_MONOTONE=PASS')


def selftest() -> None:
    verify_monotonic_support_upper()
    verify_small_exhaustive()
    verify_n57_specimen()
    print('PAIR_SUPPORT_MASS_DISTINCT_RESOLVENT_CEILING_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
