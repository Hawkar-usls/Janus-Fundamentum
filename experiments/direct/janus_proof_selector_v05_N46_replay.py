#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=46.

Regression checks the finite N46 partition, the corrected r<=8 ledger,
the r=9 degree-3 tail, and the r=10,m=5,L=30 degree-3 -> m<=4 collapse.
P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def T(s: Fraction) -> Fraction:
    s = Fraction(s)
    return max(s, Fraction(1) + (s - 1) ** 2 / 12)


def Uraw(n: int) -> int:
    return 3 ** (n - 2) * (2 * n + 1)


def Smax(n: int) -> int:
    if n <= 0:
        return 1
    return 1 + max((k + 1) * comb(n, k) * (2 ** k) for k in range(1, n + 1))


def recurrence_raw_bounds_from(s0: Fraction, n0: int):
    s = Fraction(s0)
    n = n0
    rows = []
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        rows.append((n, s, raw, next_s))
        s = next_s
        n -= 1
    return rows


def recurrence_raw_bounds_root(N: int, r0: int):
    return recurrence_raw_bounds_from(Fraction(N - r0), r0)


def verify_N46_partition() -> None:
    N = 46
    hard_r_max = (N - 6) // 4
    assert hard_r_max == 10

    r9 = []
    for m in range(5, N):
        L = N - 1 - 9 - m
        if L >= 27 and L >= 2 * m:
            r9.append((m, L))
    assert r9 == [(5,31),(6,30),(7,29),(8,28),(9,27)], r9

    r10 = []
    for m in range(5, N):
        L = N - 1 - 10 - m
        if L >= 30 and L >= 2 * m:
            r10.append((m, L))
    assert r10 == [(5,30)], r10

    print("V05_N46_HARD_R_MAX=10")
    print("V05_N46_R9_CELLS=M5L31..M9L27")
    print("V05_N46_R10_CELL=M5L30")


def verify_N46_r_le_8_recurrence() -> None:
    cap = 46 * 46
    maximum = Fraction(0)
    where = None
    for r in range(1, 9):
        for n, s, raw, _ in recurrence_raw_bounds_root(46, r):
            if raw > maximum:
                maximum = raw
                where = (r, n, s)
            assert raw <= cap, (r, n, raw, cap)
    assert maximum == Fraction(1875889, 1728), maximum
    assert where == (8, 7, Fraction(1381, 12)), where
    print("V05_N46_R_LE_8_RECURRENCE=PASS")
    print(f"V05_N46_R_LE_8_MAX_RAW={maximum}")
    print(f"V05_N46_R_LE_8_MAX_AT={where}")


def build_N46_r9_m9_L27_fixture() -> core.CNF:
    raw = [
        (-1, 2),
        (3, 4),
        (1, 2, 3, 5),
        (1, 2, 3, 6),
        (4, 5, 6),
        (4, 7, 8),
        (5, 7, 9),
        (6, 8, 9),
        (7, 8, 9),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 9, cnf
    assert sum(len(c) for c in cnf) == 27
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 37
    assert core.input_size_units(cnf) == 46
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert degrees == [3] * 9, degrees
    return cnf


def verify_N46_r9_fixture() -> None:
    class Stub:
        pass

    cnf = build_N46_r9_m9_L27_fixture()
    st = Stub()
    st.residual = cnf
    st.root_vars = tuple(range(1, 10))
    pivot = v05.proof_pivot_order(st)[0]
    assert v05.incidence_degree(cnf, pivot) == 3
    out, stats = core.eliminate_var_capped(cnf, pivot, 46 * 46)
    assert out is not None
    assert stats["raw_units"] <= 41, stats
    assert len(core.vars_of(out)) <= 8
    print(f"V05_N46_R9_SELECTED_PIVOT={pivot}")
    print(f"V05_N46_R9_ACTUAL_RAW_UNITS={stats['raw_units']}")
    print("V05_N46_R9_FIXTURE=PASS")


def verify_N46_r9_tail() -> None:
    cap = 46 * 46
    got = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(41), 8)]
    expected = [
        Fraction(403, 3),
        Fraction(40027, 27),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert max(got) == Fraction(40027, 27)
    assert all(x <= cap for x in got)
    print("V05_N46_R9_TAIL=PASS")
    print(f"V05_N46_R9_TAIL_MAX_RAW={max(got)}")


def build_N46_r10_m5_L30_fixture() -> core.CNF:
    raw = [
        (5, 6, 7, 8, 9, 10),
        (2, 3, 4, 8, 9, 10),
        (-1, 3, 4, 6, 7, 10),
        (1, 2, 4, 5, 7, 9),
        (1, 2, 3, 5, 6, 8),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 5, cnf
    assert sum(len(c) for c in cnf) == 30
    assert len(core.vars_of(cnf)) == 10
    assert core.state_units(cnf) == 36
    assert core.input_size_units(cnf) == 46
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 11)]
    assert degrees == [3] * 10, degrees
    return cnf


def verify_N46_r10_clause_collapse() -> None:
    class Stub:
        pass

    cnf = build_N46_r10_m5_L30_fixture()
    st = Stub()
    st.residual = cnf
    st.root_vars = tuple(range(1, 11))
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(cnf, pivot) == 3

    out, stats = core.eliminate_var_capped(cnf, pivot, 46 * 46)
    assert out is not None, stats
    assert stats["positive"] + stats["negative"] == 3, stats
    assert {stats["positive"], stats["negative"]} == {1, 2}, stats
    assert stats["retained"] == 2, stats
    assert stats["pairs"] == 2, stats
    assert len(out) <= 4, (out, stats)
    assert len(core.vars_of(out)) <= 9
    assert 1 + 4 * len(core.vars_of(out)) <= 37
    print(f"V05_N46_R10_SELECTED_PIVOT={pivot}")
    print(f"V05_N46_R10_POST_CLAUSES={len(out)}")
    print(f"V05_N46_R10_ACTUAL_RAW_UNITS={stats['raw_units']}")
    print("V05_N46_R10_DEGREE3_TO_M_LE_4=PASS")


def verify_coarse_false_alarm_is_not_used_as_failure() -> None:
    cap = 46 * 46
    coarse = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(41), 9)]
    assert Fraction(3645) in coarse
    assert max(coarse) > cap
    print("V05_N46_COARSE_R10_BOUND_EXCEEDS_CAP=RECORDED_NOT_FAILURE")


def selftest() -> None:
    v05.selftest()
    verify_N46_partition()
    verify_N46_r_le_8_recurrence()
    verify_N46_r9_fixture()
    verify_N46_r9_tail()
    verify_N46_r10_clause_collapse()
    verify_coarse_false_alarm_is_not_used_as_failure()
    print("V05_SELECTOR_BRIDGE_N_LE_46_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("UNIVERSAL_GPEI=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
