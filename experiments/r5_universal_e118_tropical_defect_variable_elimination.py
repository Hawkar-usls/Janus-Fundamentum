#!/usr/bin/env python3
"""Exact max-plus elimination for cubic Exact-One: NO polynomial claim.

The all-E118 matched-port primitive-phase polynomial is nonnegative
in the formal alpha variable. For source assignment x_v=1-p_v,
the MAX achievable target-kernel weight after optimizing each local
E118 flip is
    M(x)=20s/3 - (2/3)*(t0+2*t2+t3)
for s divisible by 3; t_j=#source checks with j Boolean ones.

Hence the top coefficient is nonzero iff the MIN-COST score
    B(x)=sum_{clause c} phi(sum_{v in c} x_v)
    phi(0)=1, phi(1)=0, phi(2)=2, phi(3)=1
is zero. The minimum B is a multiple of 3 in regular cubic inputs.

This file IMPLEMENTS exact deterministic min-sum factor elimination
for ALL square+cubic+linear instances, with witness reconstruction.
A matching/cycle layout may improve the elimination ORDER, but there
is NO uniform width bound. Worst-case cost remains 2^w*poly(s),
not s^O(1) when induced width w can grow.

The checker is not a claimed P=NP algorithm and finite tests do not
prove polynomial runtime. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product

from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,build_A
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions
)
from r5_universal_e118_matching_port_phase_normal_form import (
    incidence_perfect_matching,local_weight_poly
)

PHI=(1,0,2,1)

@dataclass
class Factor:
    scope: tuple[int,...]
    table: tuple[int,...]

    def __post_init__(self):
        assert tuple(sorted(set(self.scope))) == self.scope
        assert len(self.table)==1<<len(self.scope)
        assert all(isinstance(v,int) and v>=0 for v in self.table)


def score_source(rows, x):
    return sum(PHI[sum(x[j] for j in row)] for row in rows)


def constraints_from_matrix(A):
    n=len(A)
    assert n>0 and all(len(row)==n for row in A)
    assert all(sum(row)==3 and all(v in (0,1) for v in row) for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    rows=[tuple(j for j,v in enumerate(row) if v) for row in A]
    pair_seen=set()
    for row in rows:
        for a,b in ((row[0],row[1]),(row[0],row[2]),(row[1],row[2])):
            p=(a,b)
            assert p not in pair_seen,"not a linear/C4-free input"
            pair_seen.add(p)
    return rows


def minfill_order(n,rows):
    # Deterministic polynomial-time greedy heuristic, not a width theorem.
    adj=[set() for _ in range(n)]
    for row in rows:
        for v in row:
            adj[v].update(u for u in row if u!=v)
    left=set(range(n))
    order=[]
    width=0
    while left:
        def weight(v):
            N=sorted(adj[v]&left)
            missed=sum(u not in adj[w] for i,u in enumerate(N) for w in N[i+1:])
            return missed,len(N),v
        v=min(left,key=weight)
        nbrs=sorted(adj[v]&left)
        width=max(width,len(nbrs))
        for a in nbrs:
            adj[a].update(b for b in nbrs if b!=a)
            adj[a].discard(v)
        left.remove(v)
        order.append(v)
    return order,width


def extract_bits(index, positions):
    return sum(((index>>pos)&1)<<j for j,pos in enumerate(positions))


def exact_min_plus_elimination(rows,n,max_width=None):
    """Return (minimum B, Boolean minimizer, observed induced width).

    If max_width is supplied, a failure to fit raises rather than
    returning a speculative UNSAT. max_width=None is complete.
    """
    assert n>0 and all(len(row)==3 and len(set(row))==3 for row in rows)
    assert set(v for row in rows for v in row)==set(range(n))
    factors=[]
    for row in rows:
        scope=tuple(sorted(row))
        factors.append(Factor(scope,tuple(
            PHI[mask.bit_count()] for mask in range(8)
        )))
    order,predicted=minfill_order(n,rows)
    backtrack=[]
    max_seen=0
    for var in order:
        participating=[f for f in factors if var in f.scope]
        factors=[f for f in factors if var not in f.scope]
        if not participating:
            backtrack.append((var,(),(0,)))
            continue
        union=tuple(sorted(set().union(*(f.scope for f in participating))))
        remainder=tuple(x for x in union if x!=var)
        width=len(remainder)
        max_seen=max(max_seen,width)
        if max_width is not None and width>max_width:
            raise RuntimeError(
                f"exact variable elimination requires width={width} "
                f"exceeding configured resource guard {max_width}; "
                "NO SAT/UNSAT verdict issued"
            )
        slots={j:i for i,j in enumerate(union)}
        fpositions=[
            tuple(slots[j] for j in f.scope)
            for f in participating
        ]
        rempositions=tuple(slots[j] for j in remainder)
        varbit=1<<slots[var]
        table=[]
        decisions=[]
        for remmask in range(1<<width):
            entire=sum(((remmask>>i)&1)<<slot
                       for i,slot in enumerate(rempositions))
            scores=[]
            for bit in (0,1):
                bits=entire|(varbit if bit else 0)
                scores.append(sum(
                    f.table[extract_bits(bits,pos)]
                    for f,pos in zip(participating,fpositions)
                ))
            winner=0 if scores[0]<=scores[1] else 1
            table.append(scores[winner])
            decisions.append(winner)
        factors.append(Factor(remainder,tuple(table)))
        backtrack.append((var,remainder,tuple(decisions)))
    assert all(not f.scope for f in factors)
    optimum=sum(f.table[0] for f in factors)

    witness=[0]*n
    assigned=set()
    for var,remaining,choices in reversed(backtrack):
        assert all(j in assigned for j in remaining)
        mask=sum(witness[j]<<i for i,j in enumerate(remaining))
        witness[var]=choices[mask]
        assigned.add(var)
    assert len(assigned)==n
    assert score_source(rows,witness)==optimum
    assert max_seen==predicted,(max_seen,predicted)
    return optimum,witness,max_seen


def SolveLinearCubicXSAT(A,max_width=None):
    """COMPLETE exact solver (not polynomial worst case) on valid SCL A."""
    rows=constraints_from_matrix(A)
    n=len(rows)
    if n%3:
        # 3|x|=n must hold in a square 3-regular Exact-One model.
        return {"status":"UNSAT","witness":None,"min_defect":None,
                "induced_width":0,"runtime_bound":"O(n^2) arithmetic"}
    optimum,x,width=exact_min_plus_elimination(rows,n,max_width)
    if optimum==0:
        assert all(sum(x[j] for j in row)==1 for row in rows)
        assert sum(x)==n//3
        return {"status":"SAT","witness":x,"min_defect":0,
                "induced_width":width,
                "runtime_bound":"2^w * poly(n), w measured induced width"}
    return {"status":"UNSAT","witness":None,"min_defect":optimum,
            "induced_width":width,
            "runtime_bound":"2^w * poly(n), w measured induced width"}


def rows_to_matrix(rows,n):
    return [[int(j in row) for j in range(n)] for row in rows]


def exact_e118_maxplus_bridge(source,matching):
    n=len(source)
    names=sorted({v for row in source for v in row})
    where={v:i for i,v in enumerate(names)}
    assert n%3==0 and n==len(names)
    defects=Counter()
    for mask in range(1<<n):
        xv={v:(mask>>i)&1 for v,i in where.items()}
        pv={v:1-xv[v] for v in names}
        kinds=Counter(sum(xv[v] for v in row) for row in source)
        B=kinds[0]+2*kinds[2]+kinds[3]
        assert B==sum(PHI[sum(xv[v] for v in row)] for row in source)
        q={}
        for clause,owner in matching.items():
            a,b=[v for v in source[clause] if v!=owner]
            q[owner]=pv[a]^pv[b]
        assert len(q)==n
        maximum=sum(
            max(local_weight_poly(pv[v],q[v])) for v in names
        )
        assert maximum==7*n-(kinds[0]+kinds[2])-sum(xv.values())
        assert 3*(20*n//3-maximum)==2*B
        assert B%3==0
        deficits=(20*n//3-maximum)//2
        assert deficits==B//3
        defects[deficits]+=1
    return defects


def finite_controls():
    for name,A,expected in (
        ("E61_SAT12",build_A(P_SAT,Q_SAT),"SAT"),
        ("E61_UNSAT12",build_A(P_UNSAT,Q_UNSAT),"UNSAT"),
    ):
        r=SolveLinearCubicXSAT(A)
        assert r["status"]==expected,(name,r)
        print(name, r["status"],"width",r["induced_width"],
              "min_defect",r["min_defect"])

    for name,a,b,expected in (
        ("E118_SOURCE_SAT9",1,2,"SAT"),
        ("E118_SOURCE_UNSAT9",1,6,"UNSAT"),
    ):
        source=cyclic_source(9,a,b)
        match=incidence_perfect_matching(source)
        names=sorted({v for row in source for v in row})
        index={v:i for i,v in enumerate(names)}
        rows=[tuple(sorted(index[v] for v in row)) for row in source]
        source_matrix=rows_to_matrix(rows,9)
        # The SOURCE is 3-uniform and cubic but may be non-linear;
        # it is a valid reduction PREIMAGE, not itself an SCL input.
        optimum,x,width=exact_min_plus_elimination(rows,9)
        actual=source_solutions(source)
        assert (optimum==0)==bool(actual)==(expected=="SAT")
        assert optimum==(0 if expected=="SAT" else 3)
        defects=exact_e118_maxplus_bridge(source,match)
        assert min(defects)==optimum//3
        assert sum(defects.values())==1<<9
        print(name,expected,"width",width,"min B",optimum,
              "max target-kernel weight",60-2*min(defects))

    print("MIN_PLUS_DP_EXACT_WITH_WITNESS_FOR_ALL_SCL = PROVED")
    print("E118_MAX_PLUS_LOCAL_GADGET_DEFECT_IDENTITY = REPLAYED")
    print("UNIFORM_POLYNOMIAL_WIDTH_BOUND = NOT_PROVED")
    print("SolveLinearCubicXSAT worst-case polynomial = NOT_CONSTRUCTED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    finite_controls()
