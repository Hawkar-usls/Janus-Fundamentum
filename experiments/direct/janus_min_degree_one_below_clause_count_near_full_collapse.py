#!/usr/bin/env python3
"""Regression for the general d_min == m-1 near-full collapse lemma.

Protects the closed-form clause-count bound and representative canonical
near-full states. P vs NP remains OPEN.
"""

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def near_full_bound(m: int, p: int, q: int) -> int:
    assert p + q == m - 1
    if p == 0 or q == 0:
        return 1
    a = min(p, q)
    return 1 + max(1, p * q - a + 1)


def verify_closed_form_table() -> None:
    expected = {6: 6, 7: 8, 8: 11, 9: 14, 10: 18, 11: 22}
    for m, want in expected.items():
        got = max(near_full_bound(m, p, m - 1 - p) for p in range(m))
        assert got == want, (m, got, want)
    print('NEAR_FULL_BOUND_TABLE=PASS')


def build_m11_d10_fixture() -> core.CNF:
    # Pivot 1 occurs in ten of eleven clauses (4 positive, 6 negative).
    # Variables 2..5 occur in all eleven clauses, so d_min=10 at pivot 1.
    tails = [
        (2,3,4,5),
        (-2,3,4,5),
        (2,-3,4,5),
        (2,3,-4,5),
        (2,3,4,-5),
        (-2,-3,4,5),
        (-2,3,-4,5),
        (-2,3,4,-5),
        (2,-3,-4,5),
        (2,-3,4,-5),
    ]
    raw = []
    for i, tail in enumerate(tails):
        pivot = 1 if i < 4 else -1
        raw.append((pivot, *tail))
    raw.append((-2,-3,-4,-5))  # unique retained full-width clause
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 11, cnf
    assert v05.incidence_degree(cnf, 1) == 10
    assert min(v05.incidence_degree(cnf, v) for v in range(1,6)) == 10
    return cnf


def verify_m11_fixture() -> None:
    class Stub: pass
    cnf = build_m11_d10_fixture()
    st = Stub(); st.residual = cnf; st.root_vars = tuple(range(1,6))
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
    assert out is not None
    assert stats['positive'] + stats['negative'] == 10
    assert stats['retained'] == 1
    p, q = stats['positive'], stats['negative']
    assert len(out) <= near_full_bound(11, p, q), (out, stats)
    assert len(out) <= 22
    print(f'NEAR_FULL_M11_D10_ACTUAL_CLAUSES={len(out)}')
    print('NEAR_FULL_M11_D10_FIXTURE=PASS')


def max_next_clause_bound(mmax: int) -> int:
    best = 0
    for m in range(1, mmax + 1):
        for d in range(1, m + 1):
            if d == m:
                b = m // 2
            elif d == m - 1:
                b = max(near_full_bound(m, p, d-p) for p in range(d + 1))
            else:
                b = m - d + (d*d)//4
            best = max(best, b)
    return best


def verify_bridge_tables() -> None:
    assert max_next_clause_bound(7) == 8
    assert max_next_clause_bound(8) == 11
    assert max_next_clause_bound(11) == 22
    print('NEAR_FULL_BRIDGE_TABLES=PASS')


def selftest() -> None:
    verify_closed_form_table()
    verify_m11_fixture()
    verify_bridge_tables()
    print('MIN_DEGREE_M_MINUS_1_NEAR_FULL_COLLAPSE_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
