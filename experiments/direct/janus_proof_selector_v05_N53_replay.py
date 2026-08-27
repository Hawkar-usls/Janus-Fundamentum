#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=53.

Protects N53 partition, degree-4 r=9 cell, r=10/r=11 bounded bridges,
and the general near-full/full-width clause-count arithmetic. P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"
CAP = 53 * 53


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


def near_full_bound(m: int, p: int, q: int) -> int:
    assert p + q == m - 1
    if p == 0 or q == 0:
        return 1
    a = min(p, q)
    return 1 + max(1, p * q - a + 1)


def general_clause_bound(m: int, d: int) -> int:
    if d == m:
        return m // 2
    if d == m - 1:
        return max(near_full_bound(m, p, d-p) for p in range(d + 1))
    return m - d + (d*d)//4


def max_next_clause_bound(mmax: int) -> int:
    return max(general_clause_bound(m, d) for m in range(1, mmax + 1) for d in range(1, m + 1))


def verify_partition() -> None:
    N = 53
    r9=[]; r10=[]; r11=[]
    for r, out in ((9,r9),(10,r10),(11,r11)):
        for m in range(7,N):
            L=N-1-r-m
            if L >= 3*r and L >= 2*m:
                out.append((m,L))
    assert r9 == [(7,36),(8,35),(9,34),(10,33),(11,32),(12,31),(13,30),(14,29)]
    assert r10 == [(7,35),(8,34),(9,33),(10,32),(11,31),(12,30)]
    assert r11 == [(7,34),(8,33)]
    print('V05_N53_PARTITION=PASS')


def verify_r_le_8_recurrence() -> None:
    maximum=Fraction(0)
    for r in range(1,9):
        for _,_,raw,_ in recurrence_raw_bounds_from(Fraction(53-r),r):
            maximum=max(maximum,raw)
            assert raw <= CAP
    assert maximum == Fraction(58591,27)
    print('V05_N53_R_LE_8_RECURRENCE=PASS')


def verify_bridge_arithmetic() -> None:
    assert T(48) == Fraction(2221,12)
    assert T(64) == Fraction(1327,4)
    assert T(65) == Fraction(1027,3)
    assert T(81) == Fraction(1603,3)
    assert T(100) == Fraction(3271,4)
    assert T(105) == Fraction(2707,3)
    assert T(177) == Fraction(7747,3)
    for x in [T(48),T(64),T(65),T(81),T(100),T(105),T(177),Fraction(Uraw(6))]:
        assert x < CAP, x
    assert max_next_clause_bound(7) == 8
    assert max_next_clause_bound(8) == 11
    assert max_next_clause_bound(11) == 22

    # r9 degree-3 hard continuation: if n1=8,s1<=48,m1<=13,
    # the incidence average restricts the selected degree enough for m2<=13.
    for m in range(1,14):
        L = 48 - 1 - m
        dmax = min(m, L // 8)
        for d in range(1,dmax+1):
            assert general_clause_bound(m,d) <= 13, (m,d,general_clause_bound(m,d))
    print('V05_N53_BRIDGE_ARITHMETIC=PASS')


def build_r9_m7_L36_degree4_fixture() -> core.CNF:
    raw = [
        (1,3,5,6,7,9),
        (2,6,7,8,9),
        (2,3,4,7,8),
        (3,4,5,7,9),
        (1,3,5,6,8),
        (-1,2,4,5,6),
        (-1,2,4,8,9),
    ]
    cnf=core.canon_cnf(raw)
    assert len(cnf)==7
    assert sum(map(len,cnf))==36
    assert len(core.vars_of(cnf))==9
    assert core.input_size_units(cnf)==53
    assert [v05.incidence_degree(cnf,v) for v in range(1,10)] == [4]*9
    return cnf


def verify_r9_degree4_fixture() -> None:
    class Stub: pass
    st=Stub(); st.root_vars=tuple(range(1,10)); st.residual=build_r9_m7_L36_degree4_fixture()
    pivot=v05.proof_pivot_order(st)[0]
    assert pivot==1 and v05.incidence_degree(st.residual,pivot)==4
    out,stats=core.eliminate_var_capped(st.residual,pivot,CAP)
    assert out is not None
    assert {stats['positive'],stats['negative']} == {2}
    assert len(out)<=7
    assert stats['raw_units']<=72
    print(f'V05_N53_R9_D4_ACTUAL_POST_CLAUSES={len(out)}')
    print('V05_N53_R9_D4_FIXTURE=PASS')


def build_r11_m8_L33_fixture() -> core.CNF:
    raw = [
        (1,2,6,9),
        (3,5,7,8,11),
        (-1,2,6,7,10),
        (4,5,6,7),
        (-1,4,9,11),
        (3,5,8,9),
        (2,8,10),
        (3,4,10,11),
    ]
    cnf=core.canon_cnf(raw)
    assert len(cnf)==8
    assert sum(map(len,cnf))==33
    assert len(core.vars_of(cnf))==11
    assert core.input_size_units(cnf)==53
    assert [v05.incidence_degree(cnf,v) for v in range(1,12)] == [3]*11
    return cnf


def verify_r11_fixture_replay() -> None:
    class Stub: pass
    st=Stub(); st.root_vars=tuple(range(1,12)); current=build_r11_m8_L33_fixture(); st.residual=current
    pivot=v05.proof_pivot_order(st)[0]
    assert pivot==1 and v05.incidence_degree(current,pivot)==3
    current,stats=core.eliminate_var_capped(current,pivot,CAP)
    assert current is not None and len(current)<=7 and stats['raw_units']<=CAP
    max_raw=stats['raw_units']; steps=1
    while core.vars_of(current):
        st.residual=current
        p=v05.proof_pivot_order(st)[0]
        nxt,ss=core.eliminate_var_capped(current,p,CAP)
        assert nxt is not None and ss['raw_units']<=CAP, (p,ss)
        max_raw=max(max_raw,ss['raw_units']); current=nxt; steps+=1
    print(f'V05_N53_R11_FIXTURE_MAX_ACTUAL_RAW={max_raw}')
    print(f'V05_N53_R11_FIXTURE_STEPS={steps}')
    print('V05_N53_R11_M8_FIXTURE_REPLAY=PASS')


def selftest() -> None:
    v05.selftest()
    verify_partition()
    verify_r_le_8_recurrence()
    verify_bridge_arithmetic()
    verify_r9_degree4_fixture()
    verify_r11_fixture_replay()
    print('V05_SELECTOR_BRIDGE_N_LE_53_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('V3_UNIVERSAL_AVAILABILITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__': selftest()
