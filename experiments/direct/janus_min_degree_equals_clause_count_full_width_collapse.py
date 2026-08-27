#!/usr/bin/env python3
"""Regression for the general d_min == m full-width collapse lemma.

The theorem is algebraic. This executable protects representative full-width
sign-vector cases including m=10. P vs NP remains OPEN.
"""

from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def full_clause(n: int, mask: int) -> core.Clause:
    return tuple(v if (mask >> (v - 1)) & 1 else -v for v in range(1, n + 1))


def verify_family(n: int, m: int, limit: int | None = None) -> None:
    checked = 0
    for chosen in combinations(range(1 << n), m):
        cnf = core.canon_cnf(full_clause(n, mask) for mask in chosen)
        if len(cnf) != m:
            continue
        for pivot in range(1, n + 1):
            degrees = [v05.incidence_degree(cnf, v) for v in range(1, n + 1)]
            assert degrees == [m] * n
            out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
            assert out is not None
            assert stats['retained'] == 0
            assert len(out) <= min(stats['positive'], stats['negative']), (n, m, chosen, pivot, out, stats)
            assert len(out) <= m // 2
            checked += 1
            if limit is not None and checked >= limit:
                print(f'FULL_WIDTH_COLLAPSE_N{n}_M{m}=PASS:{checked}')
                return
    print(f'FULL_WIDTH_COLLAPSE_N{n}_M{m}=PASS:{checked}')


def verify_m10_fixture() -> None:
    n = 5
    masks = [0, 1, 2, 4, 8, 16, 3, 5, 9, 17]
    cnf = core.canon_cnf(full_clause(n, mask) for mask in masks)
    assert len(cnf) == 10
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, n + 1)]
    assert degrees == [10] * n
    class Stub: pass
    st = Stub(); st.residual = cnf; st.root_vars = tuple(range(1, n + 1))
    pivot = v05.proof_pivot_order(st)[0]
    out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
    assert out is not None
    assert stats['positive'] + stats['negative'] == 10
    assert stats['retained'] == 0
    assert len(out) <= min(stats['positive'], stats['negative']) <= 5
    print('FULL_WIDTH_COLLAPSE_M10_TARGET=PASS')


def selftest() -> None:
    verify_family(3, 4)
    verify_family(4, 6, limit=2000)
    verify_m10_fixture()
    print('MIN_DEGREE_EQUALS_M_FULL_WIDTH_COLLAPSE_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
