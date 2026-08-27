#!/usr/bin/env python3
"""Exact regression for the C025 counterexample to m<=7 invariance.

This is a negative control. It must continue to produce eight canonical clauses
under the v0.5 minimum-incidence selector. P vs NP remains OPEN.
"""

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def build_counterexample() -> core.CNF:
    raw = [
        (1, 5, 6, 7),
        (1, 2, 3, 4),
        (-1, 3, 4, 6, 7),
        (-1, 2, 4, 5, 7),
        (-1, 2, 3, 5, 6),
        (-2, -3, -4, -5, -6, -7),
        (2, -3, -4, -5, -6, -7),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 7, cnf
    assert len(core.vars_of(cnf)) == 7
    assert [v05.incidence_degree(cnf, v) for v in range(1, 8)] == [5] * 7
    return cnf


def selftest() -> None:
    class Stub:
        pass

    cnf = build_counterexample()
    st = Stub(); st.residual = cnf; st.root_vars = tuple(range(1, 8))
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
    assert out is not None, stats
    assert stats['positive'] == 2
    assert stats['negative'] == 3
    assert stats['retained'] == 2
    assert stats['pairs'] == 6
    assert len(out) == 8, (out, stats)
    print('M_LE_7_INVARIANT_COUNTEREXAMPLE=PASS')
    print('CLAUSES_BEFORE=7')
    print('CLAUSES_AFTER=8')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
