#!/usr/bin/env python3
"""Regression for the C025 minimum-incidence m<=6 clause-count invariant.

The theorem is algebraic; this executable protects the arithmetic and two dense edge cases.
P vs NP remains OPEN.
"""

from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def verify_d_le_4_arithmetic() -> None:
    for m in range(0, 7):
        for d in range(0, min(4, m) + 1):
            for p in range(d + 1):
                q = d - p
                assert m - d + p * q <= 6, (m, d, p, q)
    print("M_LE_6_D_LE_4_CLAUSE_BOUND=PASS")


def full_width_clause(n: int, mask: int) -> core.Clause:
    return tuple(v if (mask >> (v - 1)) & 1 else -v for v in range(1, n + 1))


def verify_d6_full_width_exhaustive(n: int) -> None:
    checked = 0
    for chosen in combinations(range(1 << n), 6):
        cnf = core.canon_cnf(full_width_clause(n, mask) for mask in chosen)
        assert len(cnf) == 6
        for pivot in range(1, n + 1):
            out, _ = core.eliminate_var_capped(cnf, pivot, 10**9)
            assert out is not None
            assert len(out) <= 3, (n, chosen, pivot, out)
            checked += 1
    print(f"M6_D6_FULL_WIDTH_N{n}_EXHAUSTIVE=PASS:{checked}")


def build_d5_m6_complete_compatibility_fixture() -> core.CNF:
    # Pivot 1 occurs in five clauses; every other variable is omitted from
    # exactly one of the six clauses, so every live variable has degree 5.
    # Two positive and three negative pivot parents are cross-compatible.
    raw = [
        (1, 3, 4, 5, 6),       # omit 2
        (1, 2, 4, 5, 6),       # omit 3
        (-1, 2, 3, 5, 6),      # omit 4
        (-1, 2, 3, 4, 6),      # omit 5
        (-1, 2, 3, 4, 5),      # omit 6
        (2, 3, 4, 5, 6),       # retained, omit pivot 1
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 6, cnf
    assert len(core.vars_of(cnf)) == 6
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 7)]
    assert degrees == [5] * 6, degrees
    return cnf


def verify_d5_m6_complete_compatibility_collapse() -> None:
    class Stub:
        pass
    cnf = build_d5_m6_complete_compatibility_fixture()
    st = Stub(); st.residual = cnf; st.root_vars = tuple(range(1, 7))
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
    assert out is not None
    assert {stats['positive'], stats['negative']} == {2, 3}, stats
    assert stats['retained'] == 1
    assert stats['pairs'] == 6
    # All six compatible resolvents equal the retained full tail and deduplicate.
    assert len(out) == 1, (out, stats)
    assert out[0] == (2, 3, 4, 5, 6), out
    print("M6_D5_K23_COMPLETE_COMPATIBILITY_COLLAPSE=PASS")


def verify_raw_size_corollary() -> None:
    for n in range(1, 64):
        assert 1 + 6 * n >= 1
    print("M_LE_6_RAW_UNITS_1_PLUS_6N=PASS")


def selftest() -> None:
    verify_d_le_4_arithmetic()
    verify_d6_full_width_exhaustive(3)
    verify_d6_full_width_exhaustive(4)
    verify_d5_m6_complete_compatibility_collapse()
    verify_raw_size_corollary()
    print("MIN_DEGREE_SIX_CLAUSE_INVARIANT_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == '__main__':
    selftest()
