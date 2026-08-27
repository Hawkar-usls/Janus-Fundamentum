#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=49.

Protects the finite N49 partition and the reachable r=10,m=8,L=30 bridge.
The proof deliberately does NOT assume the false m<=7 invariant.
P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"
CAP = 49 * 49


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
    N = 49
    r9 = []
    for m in range(7, N):
        L = N - 1 - 9 - m
        if L >= 27 and L >= 2 * m:
            r9.append((m, L))
    assert r9 == [(7,32),(8,31),(9,30),(10,29),(11,28),(12,27)], r9

    r10 = []
    for m in range(7, N):
        L = N - 1 - 10 - m
        if L >= 30 and L >= 2 * m:
            r10.append((m, L))
    assert r10 == [(7,31),(8,30)], r10
    print('V05_N49_PARTITION=PASS')


def verify_r_le_8_recurrence() -> None:
    maximum = Fraction(0)
    for r in range(1, 9):
        for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(49-r), r):
            maximum = max(maximum, raw)
            assert raw <= CAP, (r, raw, CAP)
    print(f'V05_N49_R_LE_8_RECURRENCE_MAX={maximum}')
    print('V05_N49_R_LE_8_RECURRENCE=PASS')


def verify_r9_tail() -> None:
    got = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(44), 8)]
    expected = [
        Fraction(1861, 12),
        Fraction(3420529, 1728),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert max(got) == Fraction(3420529, 1728)
    assert all(x <= CAP for x in got)
    print('V05_N49_R9_TAIL=PASS')


def verify_bridge_arithmetic() -> None:
    assert T(Fraction(44)) == Fraction(1861, 12)
    assert T(Fraction(64)) == Fraction(1327, 4)
    assert T(Fraction(97)) == Fraction(769)
    assert max(7 - d + (d*d)//4 for d in range(1, 8)) == 12
    assert Uraw(6) == 1053
    assert Fraction(1861,12) < CAP
    assert Fraction(1327,4) < CAP
    assert Fraction(769) < CAP
    assert 1053 < CAP
    print('V05_N49_REACHABLE_BRIDGE_ARITHMETIC=PASS')


def build_r10_m8_L30_hard_fixture() -> core.CNF:
    raw = [
        (1, 2, 4),
        (3, 5),
        (1, 6, 7, 8, 9),
        (-1, 2, 6, 10),
        (3, 4, 7, 10),
        (5, 8, 9, 10),
        (2, 3, 6, 7),
        (4, 5, 8, 9),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 8, cnf
    assert sum(len(c) for c in cnf) == 30
    assert len(core.vars_of(cnf)) == 10
    assert core.state_units(cnf) == 39
    assert core.input_size_units(cnf) == 49
    assert [v05.incidence_degree(cnf, v) for v in range(1, 11)] == [3] * 10
    return cnf


def verify_hard_fixture() -> None:
    class Stub:
        pass

    roots = tuple(range(1, 11))
    st = Stub(); st.root_vars = roots
    current = build_r10_m8_L30_hard_fixture()
    st.residual = current
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(current, pivot) == 3

    current, stats = core.eliminate_var_capped(current, pivot, CAP)
    assert current is not None, stats
    assert len(current) == 7, (current, stats)
    assert len(core.vars_of(current)) == 9
    assert core.state_units(current) <= 44

    st.residual = current
    second = v05.proof_pivot_order(st)[0]
    assert v05.incidence_degree(current, second) <= 4

    # Replay the actual fixture to completion under the same selector/cap.
    steps = 1
    while core.vars_of(current):
        st.residual = current
        order = v05.proof_pivot_order(st)
        if not order:
            break
        p = order[0]
        nxt, step_stats = core.eliminate_var_capped(current, p, CAP)
        assert nxt is not None, (p, step_stats)
        assert step_stats['raw_units'] <= CAP, (p, step_stats)
        current = nxt
        steps += 1

    print(f'V05_N49_HARD_FIXTURE_SECOND_DEGREE={v05.incidence_degree(core.canon_cnf(build_r10_m8_L30_hard_fixture()), second) if False else "CERTIFIED_LE_4"}')
    print(f'V05_N49_HARD_FIXTURE_REPLAY_STEPS={steps}')
    print('V05_N49_R10_M8_REACHABLE_BRIDGE_FIXTURE=PASS')


def selftest() -> None:
    v05.selftest()
    verify_partition()
    verify_r_le_8_recurrence()
    verify_r9_tail()
    verify_bridge_arithmetic()
    verify_hard_fixture()
    print('V05_SELECTOR_BRIDGE_N_LE_49_REGRESSION=PASS')
    print('M_LE_7_INVARIANT=FALSE_COUNTEREXAMPLE_ARCHIVED')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('V3_UNIVERSAL_AVAILABILITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
