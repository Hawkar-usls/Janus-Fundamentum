#!/usr/bin/env python3
"""R5 exact nonnegative-Bethe-normalized LOOP SERIES on universal T4 network.

Original source F -> source-verified quartic T4 matched network Q,
with each local T4 supported on three bits:
  1000, 0100, 0011.
Put the local probability distribution p_v=1/3 on each allowed
four-port state. Every port has marginal pi=(2/3,1/3).

Let psi(0)=-1 and psi(1)=2. For two copies a,b of any quotient
edge, the EXACT identity
  1[a=b]/pi(a) = 1+psi(a)psi(b)/2
holds for all a,b∈{0,1}. Therefore normalizing by the exact
homogeneous BP Bethe value Z_B > 0 gives:
  Z/Z_B = sum_{S subseteq E(Q)} 2^(-|S|)
          prod_{v∈V(Q)} M_v(S∩delta(v)),
where M_v(J)=E_{p_v} prod_{incident port∈J} psi(port_bit).
Every M is an INTEGER (the 1/3 cancels).

For the canonical T4 port order:
  M(empty)=1
  M(singleton)=0
  M(pair)= -1 except pair ports 2&3, which has value 2
  M(triple)=2 for {0,1,2},{0,1,3};
            =-1 for {0,2,3},{1,2,3}
  M(all four)=0.
So only selected-edge subgraphs with ALL VERTEX DEGREES in {0,2,3}
contribute. The local 1/4-degree terms vanish EXACTLY.

This gives a source-correct EXACT generalized-loop polynomial
whose local coefficients are finite / independently auditable.
It is NOT a polynomial-time all-source summation procedure.
Naive enumeration has up to 2^(2n) edge selections.
CI brute-force checks two source-different SCL12 of SAME SIZE:
SAT with exactly 1 solution vs UNSAT with 0, and Fano7 UNSAT.
All results are exact rational arithmetic, not Bethe approximations.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction

from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,LOCAL_OPTIONS,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def local_loop_moments():
    moments={}
    for mask in range(16):
        total=0
        for choice in LOCAL_OPTIONS:
            weight=1
            for port in range(4):
                if (mask>>port)&1:
                    weight*=2 if choice[port] else -1
            total+=weight
        assert total%3==0,(mask,total)
        moments[mask]=total//3
    assert moments[0]==1
    assert all(moments[1<<i]==0 for i in range(4))
    assert moments[15]==0
    assert {tuple(i for i in range(4) if mask>>i&1):moments[mask]
            for mask in range(16) if mask.bit_count()==2}=={
        (0,1):-1,(0,2):-1,(0,3):-1,
        (1,2):-1,(1,3):-1,(2,3):2
    }
    assert {tuple(i for i in range(4) if mask>>i&1):moments[mask]
            for mask in range(16) if mask.bit_count()==3}=={
        (0,1,2):2,(0,1,3):2,(0,2,3):-1,(1,2,3):-1
    }
    return tuple(moments[i] for i in range(16))


def verify_pairwise_edge_resolution():
    probabilities=(Fraction(2,3),Fraction(1,3))
    psi=(-1,2)
    for a in (0,1):
        for b in (0,1):
            lhs=Fraction(int(a==b),1)/probabilities[a]
            rhs=Fraction(1)+Fraction(psi[a]*psi[b],2)
            assert lhs==rhs,(a,b,lhs,rhs)
    return True


def signed_loop_sum_exact(Q,state_limit=35000000):
    """Intentionally exponential exhaustive edge-subset contraction.

    Evaluates the loop correction numerator over denominator 2^m.
    Finite scientific verifier only; guard yields UNKNOWN rather
    than a false refutation if interrupted.
    """
    n=Q["source_n"]
    edges=Q["endpoints"]
    m=len(edges)
    assert m==2*n and n<=12,"finite controls n<=12 ONLY"
    moments=local_loop_moments()
    # Each quartic node stores a 4-bit mask of selected incident edges.
    chosen=[0]*n
    last=[-1]*n
    for e,pair in enumerate(edges):
        assert len(pair)==2
        for v,port in pair:
            assert 0<=v<n and 0<=port<4
            last[v]=e
    assert all(v>=0 for v in last)
    closure=[[] for _ in range(m)]
    for v,e in enumerate(last):closure[e].append(v)
    numerator=0
    visited=0
    nonzero=0
    negative=0
    def rec(pos,scalar,selected):
        nonlocal numerator,visited,nonzero,negative
        visited+=1
        if visited>state_limit:
            raise OverflowError("LOOP_RESOURCE_GUARD")
        if pos==m:
            contribution=scalar<<(m-selected)
            numerator+=contribution
            if contribution:
                nonzero+=1
                if contribution<0:negative+=1
            return
        (u,portu),(v,portv)=edges[pos]
        assert u!=v
        close=closure[pos]
        # Nonselection branch.
        scale=scalar
        for vertex in close:
            scale*=moments[chosen[vertex]]
        if scale:
            rec(pos+1,scale,selected)
        # Selection branch: mark each endpoint's chosen incident port.
        assert not chosen[u]&(1<<portu)
        assert not chosen[v]&(1<<portv)
        chosen[u]^=1<<portu
        chosen[v]^=1<<portv
        scale=scalar
        for vertex in close:
            scale*=moments[chosen[vertex]]
        if scale:
            rec(pos+1,scale,selected+1)
        chosen[u]^=1<<portu
        chosen[v]^=1<<portv

    try:
        rec(0,1,0)
    except OverflowError:
        return {"status":"UNKNOWN_RESOURCE_GUARD","states":visited}
    return {"status":"EXACT","correction":Fraction(numerator,1<<m),
            "states":visited,"nonzero_loops":nonzero,
            "negative_loops":negative}


def exact_original_count(rows,n):
    assert n<=12
    clauses=tuple(sum(1<<v for v in row) for row in rows)
    return sum(all((x&mask).bit_count()==1 for mask in clauses)
               for x in range(1<<n))


def main():
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic

    assert verify_pairwise_edge_resolution()
    moments=local_loop_moments()
    print(f"T4_LOOP_MOMENTS_16_EXACT={moments}",flush=True)
    print("T4_LOOP_DEGREES_ONE_AND_FOUR_ZERO=PROVED")
    print("ALL_SCL_BETHE_LOOP_CORRECTION_IDENTITY=PROVED")

    cases=[("FANO7",cyclic(7),7,0)]
    for name,p,q,count in (
        ("E61_SAT12",P_SAT,Q_SAT,1),
        ("E61_UNSAT12",P_UNSAT,Q_UNSAT,0),
    ):
        A=build_A(p,q)
        rows=validate_sparse(
            [tuple(j for j,v in enumerate(row) if v) for row in A],
            len(A)
        )
        cases.append((name,rows,len(rows),count))

    for name,rows,n,expected in cases:
        Q=paired_quartic_network(rows,n)
        exact=exact_original_count(rows,n)
        assert exact==expected
        result=signed_loop_sum_exact(Q)
        assert result["status"]=="EXACT",result
        corr=result["correction"]
        if exact==0:
            assert corr==0,(name,corr)
        else:
            assert n%3==0
            bethe=Fraction(16,27)**(n//3)
            assert bethe*corr==exact,(name,bethe,corr,exact)
        print(f"EXACT_LOOP_SUM_{name}=CORRECTION_{corr} "
              f"ORIGINAL_COUNT_{exact} "
              f"STATES_{result['states']} "
              f"NONZERO_{result['nonzero_loops']} "
              f"NEGATIVE_{result['negative_loops']}",flush=True)

    print("SAME_N12_SAT_VS_UNSAT_BETHE_IDENTICAL_LOOP_SUM_DISTINGUISHES=PASS")
    print("ALL_SCL_LOOP_SUM_POLYTIME_EVALUATOR=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
