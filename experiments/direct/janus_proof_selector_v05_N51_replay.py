#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=51.

Protects the finite N51 partition, exact resource arithmetic, and a real
r=10,m=10,L=30 hard fixture that lands in m1=9,n1=9.
P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"
CAP = 51 * 51


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
    rows = []
    for n in range(n0, 2, -1):
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        rows.append((n, s, raw, next_s))
        s = next_s
    return rows


def verify_partition() -> None:
    N = 51
    r9 = []
    for m in range(7, N):
        L = N - 1 - 9 - m
        if L >= 27 and L >= 2 * m:
            r9.append((m, L))
    assert r9 == [(7,34),(8,33),(9,32),(10,31),(11,30),(12,29),(13,28)], r9

    r10 = []
    for m in range(7, N):
        L = N - 1 - 10 - m
        if L >= 30 and L >= 2 * m:
            r10.append((m, L))
    assert r10 == [(7,33),(8,32),(9,31),(10,30)], r10
    print('V05_N51_PARTITION=PASS')


def verify_r_le_8_recurrence() -> None:
    maximum = Fraction(0)
    for r in range(1, 9):
        for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(51-r), r):
            maximum = max(maximum, raw)
            assert raw <= CAP, (r, raw, CAP)
    assert maximum == Fraction(7207, 4), maximum
    print(f'V05_N51_R_LE_8_RECURRENCE_MAX={maximum}')
    print('V05_N51_R_LE_8_RECURRENCE=PASS')


def verify_r9_tail() -> None:
    got = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(46), 8)]
    expected = [
        Fraction(679, 4),
        Fraction(151939, 64),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert max(got) == Fraction(151939, 64)
    assert all(x <= CAP for x in got)
    print('V05_N51_R9_TAIL=PASS')


def verify_r10_bridge_arithmetic() -> None:
    assert T(Fraction(46)) == Fraction(679, 4)
    assert T(Fraction(82)) == Fraction(2191, 4)
    assert T(Fraction(161)) == Fraction(6403, 3)
    assert Uraw(6) == 1053
    assert Fraction(679, 4) < CAP
    assert Fraction(2191, 4) < CAP
    assert Fraction(6403, 3) < CAP
    assert 1053 < CAP

    for m1 in (7, 8, 9):
        L1 = 46 - 1 - m1
        assert L1 // 9 <= 4
        for d in range(1, 5):
            assert m1 - d + (d*d)//4 <= 9

    assert 1 + 9 * (1 + 8) == 82
    assert max(9 - d + (d*d)//4 for d in range(1, 10)) == 20
    assert 1 + 20 * (1 + 7) == 161
    print('V05_N51_R10_BRIDGE_ARITHMETIC=PASS')


def build_r10_m10_L30_hard_fixture() -> core.CNF:
    # 3-regular cyclic incidence on 10 clauses/10 variables.
    # Pivot 1 occurs once positively and twice negatively, so the selected
    # degree-3 pivot exercises the mixed 1+2 branch. Every clause has width 3.
    raw = [
        (1, 2, 4),
        (2, 3, 5),
        (3, 4, 6),
        (4, 5, 7),
        (5, 6, 8),
        (6, 7, 9),
        (7, 8, 10),
        (-1, 8, 9),
        (2, 9, 10),
        (-1, 3, 10),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 10, cnf
    assert sum(len(c) for c in cnf) == 30
    assert len(core.vars_of(cnf)) == 10
    assert core.state_units(cnf) == 41
    assert core.input_size_units(cnf) == 51
    assert [v05.incidence_degree(cnf, v) for v in range(1, 11)] == [3] * 10
    return cnf


def verify_hard_fixture() -> None:
    class Stub:
        pass

    roots = tuple(range(1, 11))
    st = Stub(); st.root_vars = roots
    current = build_r10_m10_L30_hard_fixture()
    st.residual = current
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(current, pivot) == 3

    current, stats = core.eliminate_var_capped(current, pivot, CAP)
    assert current is not None, stats
    assert {stats['positive'], stats['negative']} == {1, 2}, stats
    assert len(current) == 9, (current, stats)
    assert len(core.vars_of(current)) == 9
    assert core.state_units(current) <= 46

    st.residual = current
    second = v05.proof_pivot_order(st)[0]
    assert v05.incidence_degree(current, second) <= 4

    steps = 1
    max_raw = stats['raw_units']
    while core.vars_of(current):
        st.residual = current
        order = v05.proof_pivot_order(st)
        if not order:
            break
        p = order[0]
        nxt, step_stats = core.eliminate_var_capped(current, p, CAP)
        assert nxt is not None, (p, step_stats)
        assert step_stats['raw_units'] <= CAP, (p, step_stats)
        max_raw = max(max_raw, step_stats['raw_units'])
        current = nxt
        steps += 1

    print('V05_N51_HARD_FIXTURE_M1_EQ_9_N1_EQ_9=PASS')
    print('V05_N51_HARD_FIXTURE_SECOND_DEGREE_LE_4=PASS')
    print(f'V05_N51_HARD_FIXTURE_MAX_ACTUAL_RAW={max_raw}')
    print(f'V05_N51_HARD_FIXTURE_REPLAY_STEPS={steps}')
    print('V05_N51_R10_M10_REACHABLE_BRIDGE_FIXTURE=PASS')


def selftest() -> None:
    v05.selftest()
    verify_partition()
    verify_r_le_8_recurrence()
    verify_r9_tail()
    verify_r10_bridge_arithmetic()
    verify_hard_fixture()
    print('V05_SELECTOR_BRIDGE_N_LE_51_REGRESSION=PASS')
    print('M_LE_7_INVARIANT=FALSE_COUNTEREXAMPLE_ARCHIVED')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('V3_UNIVERSAL_AVAILABILITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
