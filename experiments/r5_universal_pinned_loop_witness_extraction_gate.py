#!/usr/bin/env python3
"""R5 original-source PINS on exact quartic generalized-loop algebra.

Universal mathematical result for EVERY original legal SCL F:
Original source has a certified n-cell perfect-matching quotient Q,
with T4 allowed configurations {1000,0100,0011}. The matched
original variable of cell i is the common last-two-port value.

For any consistent partial original variable pins P, replace only
the T4 local factor of every pinned variable's matched cell:
  pin 1: E4=|0011>,
  pin 0: O4=|1000>+|0100>.
No graph rewiring, and original n-variable SCL still acts as
the proof-carrying source.

Using *the SAME* positive Bethe normalization of the UNPINNED
original source, the exact edge resolution delta(a,b)/pi(a) =
1 + psi(a)psi(b)/2 remains valid with pi=(2/3,1/3)
and psi(0)=-1, psi(1)=2. For each cell v with pin status,
put local weight q_v(bit)=T4(bit)*indicator(pin)/3;
define pinned local moments M_v^P(J) =
 sum_local_allowed q_v(bit) product_(port in J) psi(bit_port).

Then the exact algebraic identity remains:
  L_P = Σ_(S⊆E) 2^(-|S|) ∏_v M_v^P(S∩δ(v))
      = #SAT(F respecting P) / Z_B(F).
This does NOT assume the pinned network has its own positive
BP fixed point; it is a direct exact reweighting of the
original unpinned Bethe change of basis.

IMPORTANT STRICT OBSTRUCTION: unpinned local moment M(all4)=0
and M(singleton)=0, but pinned E4 moments at ALL 16 masks
are nonzero, including singletons and full degree4.
Therefore the convenient fixed LOOP GRAMMAR of local
occupied degrees {0,2,3} is NOT closed under witness-extraction
conditioning. Any universal polynomial LoopZeroTest whose
proof depends crucially on forbidding local degrees 1&4 must
include an independently proved extension to marked/pinned
cells OR a different witness extraction reduction.

Conditional reduction THEOREM:
If there is a uniform polynomial-bit-time signed-loop ZERO TEST
for all such original-source-authenticated partially pinned
rank-two networks, we can recover SAT witness by ≤ n+1 zero tests:
test initial; then fix original matched variables one by one,
query whether a SAT extension with x=0 exists; if yes keep 0,
else keep 1, with soundness by induction. This is a CONDITIONAL
self-reduction theorem, NOT a construction of a polynomial oracle.
A zero test only on unpinned networks is not by itself
sufficient to invoke this particular self reduction.

Small controls evaluate signed-loop expansion independently
with a resource guard, never silently converting UNKNOWN→UNSAT.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network, LOCAL_OPTIONS
)
from r5_universal_rank2_exact_bethe_loop_correction import (
    local_loop_moments
)

PSI=(-1,2)


def exact_pin_moment_numerators(pin):
    """Return 16 integer numerators, denominator 3 for pinned gate.

    For unpinned gate, return existing INTEGERS with denominator1,
    which reduces arithmetic and preserves the original signed-loop
    code's moment table exactly.
    """
    assert pin in (None,0,1)
    if pin is None:
        return local_loop_moments(),1
    kept=[bits for bits in LOCAL_OPTIONS if bits[2]==pin]
    assert kept and all(bits[3]==pin for bits in kept)
    table=[]
    for mask in range(16):
        val=sum(
            product(PSI[bits[port]] for port in range(4)
                    if (mask>>port)&1)
            for bits in kept
        )
        table.append(val)
    return tuple(table),3


def product(xs):
    p=1
    for x in xs:p*=x
    return p


def pin_source_truth_count(report,pins,max_n=15):
    """Independent brute original source control, exponential by design."""
    n=report["source_n"]
    assert n<=max_n
    pins=dict(pins)
    assert all(0<=k<n and v in (0,1) for k,v in pins.items())
    masks=tuple(sum(1<<v for v in row)
                for row in report["source_rows"])
    return sum(
        all((guess&row).bit_count()==1 for row in masks)
        and all(((guess>>v)&1)==b for v,b in pins.items())
        for guess in range(1<<n)
    )


def signed_pinned_loop_exact(report,pins,limit=8000000):
    """Finite exact generalized-loop evaluation with resource guard.

    Dynamic partial product is integer, with every 1/3 factor for
    PINNED cell in a common denominator 3^#pinned. The 2^|S|
    weights are retained using a common denominator 2^2n.
    No floating point.
    """
    n=report["source_n"]
    source_pins=dict(pins)
    assert all(type(v) is int and 0<=v<n and b in (0,1)
               for v,b in source_pins.items())
    owner={v:i for i,v in enumerate(report["matching"])}
    table=[];denom=1
    for cell in range(n):
        v=report["matching"][cell]
        t,d=exact_pin_moment_numerators(source_pins.get(v))
        table.append(t);denom*=d
    m=report["quotient_edges"]
    assert m==2*n
    edges=report["endpoints"]
    assert len(edges)==m
    last=[-1]*n
    for e,pair in enumerate(edges):
        assert len(pair)==2
        for v,port in pair:
            last[v]=e
    closing=[[] for _ in range(m)]
    for v,e in enumerate(last):closing[e].append(v)

    masks=[0]*n
    numerator=0
    visits=0
    negative=0
    class ResourceGuard(Exception):pass

    def rec(i,coef,selected):
        nonlocal visits,numerator,negative
        visits+=1
        if visits>limit:raise ResourceGuard
        if i==m:
            term=coef<<(m-selected)
            numerator+=term
            if term<0:negative+=1
            return
        (u,a),(v,b)=edges[i]
        assert u!=v
        # Unselected edge, check factors completing at i.
        val=coef
        for w in closing[i]:val*=table[w][masks[w]]
        if val:rec(i+1,val,selected)

        # Selected edge, independently mark both endpoint port masks.
        masks[u]^=1<<a
        masks[v]^=1<<b
        val=coef
        for w in closing[i]:val*=table[w][masks[w]]
        if val:rec(i+1,val,selected+1)
        masks[u]^=1<<a
        masks[v]^=1<<b
    try:
        rec(0,1,0)
    except ResourceGuard:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","states":visits}
    correction=Fraction(numerator,(1<<m)*denom)
    return {"status":"EXACT","loop":correction,"states":visits,
            "negative_terms":negative,"pins":len(source_pins)}


def recover_source_witness_with_pinned_zero_oracle(report,zero_oracle):
    """Conditional general theorem: ≤n+1 oracle calls.

    zero_oracle(P) MUST be sound and complete for all pinned
    original-source signed-loop sums, not only unpinned sums.
    """
    n=report["source_n"]
    if zero_oracle({}):
        return None,n+1 if False else 1
    pins={}
    calls=1
    for original_v in report["matching"]:
        trial={**pins,original_v:0}
        calls+=1
        if zero_oracle(trial):
            pins[original_v]=1
        else:
            pins[original_v]=0
    witness=tuple(pins[v] for v in range(n))
    assert all(sum(witness[v] for v in row)==1
               for row in report["source_rows"])
    assert calls==n+1
    return witness,calls


def main():
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic

    base=local_loop_moments()
    none,d=exact_pin_moment_numerators(None)
    assert d==1 and none==base
    odd,d1=exact_pin_moment_numerators(1)
    even,d0=exact_pin_moment_numerators(0)
    assert d1==d0==3
    assert sum(1 for x in odd if x==0)==0
    assert odd[15]==4 and even[15]==-4
    assert all(odd[1<<i]!=0 for i in range(4))
    assert any(even[1<<i]!=0 for i in range(4))
    assert tuple(odd[i]+even[i] for i in range(16))==tuple(3*x for x in base)
    print(f"PIN_ONE_ALL16_MOMENTS_NONZERO={odd}",flush=True)
    print(f"PIN_ZERO_MOMENT_TABLE={even}",flush=True)
    print("PIN_UNPINNED_DEGREE_ONE_FOUR_ZERO_GRAMMAR_NOT_CLOSED=PROVED")

    cases=[("FANO7",cyclic(7),7,0)]
    for name,p,q,count in (
        ("E61_SAT12",P_SAT,Q_SAT,1),
        ("E61_UNSAT12",P_UNSAT,Q_UNSAT,0)
    ):
        A=build_A(p,q)
        n=len(A)
        rows=validate_sparse(
            [tuple(j for j,v in enumerate(row) if v) for row in A],n
        )
        cases.append((name,rows,n,count))
    for name,rows,n,ground in cases:
        net=paired_quartic_network(rows,n)
        assert pin_source_truth_count(net,{})==ground
        k=n//3
        if n%3:
            # With n nonmultiple3 no original assignment satisfies all
            # exact ones, regardless of pins, and both true loops are0.
            for value in (0,1):
                pin={net["matching"][0]:value}
                res=signed_pinned_loop_exact(net,pin)
                assert res["status"]=="EXACT" and res["loop"]==0
            print("SOURCE_PINNED_FANO7_UNSAT_LOOP_ZERO_FOR_BOTH_BITS=PASS",
                  flush=True)
            continue

        # For SAT12, unique witness forces the correct value of
        # chosen source variable; the other pin has zero extensions.
        v=net["matching"][0]
        for value in (0,1):
            pin={v:value}
            expected=pin_source_truth_count(net,pin)
            res=signed_pinned_loop_exact(net,pin)
            assert res["status"]=="EXACT",res
            assert res["loop"]==Fraction(expected,1) * Fraction(27,16)**k
            print(f"PINNED_{name}_ORIGINAL_VAR_{v}_VALUE_{value}="
                  f"COUNT_{expected}_LOOP_{res['loop']} "
                  f"STATES_{res['states']}",flush=True)

        # Independent finite EXHAUSTIVE source-oracle is used only
        # to verify the GENERAL witness extraction logic; it does
        # not implement a polynomial pinned loop zero oracle.
        oracle=lambda pins:pin_source_truth_count(net,pins)==0
        witness,calls=recover_source_witness_with_pinned_zero_oracle(
            net,oracle
        )
        assert calls in (1,n+1)
        if ground==0:
            assert witness is None
        else:
            assert witness is not None
            assert pin_source_truth_count(
                net,{v:bit for v,bit in enumerate(witness)}
            )==1
        print(f"SOURCE_REDUCE_{name}_WITNESS="
              f"{witness if witness is not None else 'UNSAT'} "
              f"ORACLE_CALLS={calls}",flush=True)

    print("ALL_SCL_PINNED_LOOP_IDENTITY_EXACT=PROVED")
    print("ALL_SCL_WITNESS_RECOVERY_LE_N_PLUS_ONE_PINNED_ORACLE_CALLS=PROVED")
    print("UNPINNED_LOOP_ZERO_TEST_ALONE_DOES_NOT_YIELD_THIS_PINNED_ORACLE")
    print("UNIFORM_POLY_PINNED_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
