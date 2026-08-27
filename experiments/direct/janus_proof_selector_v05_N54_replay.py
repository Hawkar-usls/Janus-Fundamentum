#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=54.

Protects the N54 partition, exact bridge arithmetic, and the degree-4 balanced
survival literal-transport witness. P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"
CAP = 54 * 54


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
    s = Fraction(s0); rows=[]
    for n in range(n0,2,-1):
        raw=min(T(s),Fraction(Uraw(n)))
        nxt=min(T(s),Fraction(Smax(n-1)))
        rows.append((n,s,raw,nxt)); s=nxt
    return rows


def near_full_bound(m: int, p: int, q: int) -> int:
    assert p+q == m-1
    if p==0 or q==0: return 1
    a=min(p,q)
    return 1+max(1,p*q-a+1)


def general_clause_bound(m: int, d: int) -> int:
    if d==m: return m//2
    if d==m-1: return max(near_full_bound(m,p,d-p) for p in range(d+1))
    return m-d+(d*d)//4


def verify_partition() -> None:
    N=54
    expected={
      9:[(7,37),(8,36),(9,35),(10,34),(11,33),(12,32),(13,31),(14,30)],
      10:[(7,36),(8,35),(9,34),(10,33),(11,32),(12,31),(13,30)],
      11:[(7,35),(8,34),(9,33)],
    }
    for r,want in expected.items():
        got=[]
        for m in range(7,N):
            L=N-1-r-m
            if L>=3*r and L>=2*m: got.append((m,L))
        assert got==want,(r,got)
    print('V05_N54_PARTITION=PASS')


def verify_r_le_8_recurrence() -> None:
    maximum=Fraction(0)
    for r in range(1,9):
        for _,_,raw,_ in recurrence_raw_bounds_from(Fraction(54-r),r):
            maximum=max(maximum,raw); assert raw<=CAP
    assert maximum==Fraction(151939,64)
    print('V05_N54_R_LE_8_RECURRENCE=PASS')


def verify_arithmetic() -> None:
    expected={49:Fraction(193),73:Fraction(433),89:Fraction(1939,3),97:Fraction(769),105:Fraction(2707,3),121:Fraction(1201),81:Fraction(1603,3),100:Fraction(3271,4),177:Fraction(7747,3)}
    for s,w in expected.items():
        assert T(s)==w,(s,T(s),w)
        assert w<CAP
    assert Uraw(6)==1053 and Uraw(6)<CAP
    # m<=8 ->11, m<=11 ->22 under general full/near-full bounds.
    def max_next(mmax):
        return max(general_clause_bound(m,d) for m in range(1,mmax+1) for d in range(1,m+1))
    assert max_next(8)==11
    assert max_next(11)==22
    # r9 degree-3 n=8,s<=49,m<=13 keeps m'<=13.
    for m in range(1,14):
        dmax=min(m,(49-1-m)//8)
        for d in range(1,dmax+1):
            assert general_clause_bound(m,d)<=13
    # r10 n=8,s<=49,m<=12 keeps m'<=12.
    for m in range(1,13):
        dmax=min(m,(49-1-m)//8)
        for d in range(1,dmax+1):
            assert general_clause_bound(m,d)<=12
    print('V05_N54_BRIDGE_ARITHMETIC=PASS')


def build_degree4_transport_fixture() -> core.CNF:
    raw=[
      (6,7,8),
      (3,5,6),
      (2,7,8),
      (2,6,7),
      (3,5,8),
      (1,4,5),
      (3,4,5),
      (1,6,9),
      (-1,2,4),
      (-1,7,9),
      (3,8,9),
      (2,4,9),
    ]
    cnf=core.canon_cnf(raw)
    assert len(cnf)==12
    assert sum(map(len,cnf))==36
    assert len(core.vars_of(cnf))==9
    assert [v05.incidence_degree(cnf,v) for v in range(1,10)]==[4]*9
    return cnf


def verify_degree4_transport_fixture() -> None:
    class Stub: pass
    cnf=build_degree4_transport_fixture(); st=Stub(); st.residual=cnf; st.root_vars=tuple(range(1,10))
    pivot=v05.proof_pivot_order(st)[0]
    assert pivot==1 and v05.incidence_degree(cnf,pivot)==4
    out,stats=core.eliminate_var_capped(cnf,pivot,CAP)
    assert out is not None
    assert {stats['positive'],stats['negative']}=={2}
    post_L=sum(map(len,out)); post_n=len(core.vars_of(out))
    assert post_L<=48,(post_L,out,stats)
    if post_n==8:
        next_min=min(v05.incidence_degree(out,v) for v in core.vars_of(out))
        assert next_min<=6,(next_min,out)
    print(f'V05_N54_TRANSPORT_POST_L={post_L}')
    print(f'V05_N54_TRANSPORT_POST_N={post_n}')
    print('V05_N54_DEGREE4_LITERAL_TRANSPORT_FIXTURE=PASS')


def selftest() -> None:
    v05.selftest()
    verify_partition()
    verify_r_le_8_recurrence()
    verify_arithmetic()
    verify_degree4_transport_fixture()
    print('V05_SELECTOR_BRIDGE_N_LE_54_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('V3_UNIVERSAL_AVAILABILITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__': selftest()
