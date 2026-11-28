#!/usr/bin/env python3
"""All-input incidence-divisibility NO-GO for isolated XOR3 gadgets.

An isolated 3-uniform positive Exact-One gadget is a hypergraph H,
with three distinct externally visible Boolean ports p,q,r and
internal variables that each occur EXACTLY THREE times in H.
The port occurrence multiplicities inside H are d=(d1,d2,d3).

For any satisfying assignment x,
    #rows = d1*p+d2*q+d3*r+3*sum_internal_variables,
hence
    d1*p+d2*q+d3*r = #rows (mod 3).

The projections of H's solutions cannot be ALL four vectors satisfying
p XOR q XOR r = charge unless ALL port degrees d_i vanish mod 3:
 * EVEN charge: permitted assignments 000,011,101,110; subtract
   congruences to get d1=d2=d3=0 (mod 3).
 * ODD charge: permitted 100,010,001,111; singleton congruences
   give all d_i=#rows (mod 3); triple gives #rows=0 (mod 3).

Therefore NO such local XOR3 gadget can have port degree 1 or 2,
even if the degrees are different and even if the constraints are
NONLINEAR or many. The theorem excludes only SEPARATED gadgets
with all internal degrees 3 and three original ports; it does NOT
exclude coupled multi-gadget representations, different interfaces,
or the desired P=NP algorithm.

As a positive exact sanity control, the MINIMAL 3-port equality
gadget consists of rows (a,b,p),(a,b,q),(a,b,r), where its
ports each have degree 1 and the two internal variables have degree 3.
Its projection is exactly {000,111}. It is non-linear (rows
pairwise share a,b). This illustrates the MOD3 filter's correct
difference between EQ3 and XOR3, NOT a universal solver.

The checker exhausts every degree vector mod 3 and every port
assignment; it independently enumerates 2^5 assignments to
the explicit minimal equality gadget.
"""
from __future__ import annotations

from itertools import product
from collections import Counter

def parity3(word):
    return sum(word)&1

def degree_mod3_image(degrees,rows_mod3):
    return {
        word for word in product((0,1),repeat=3)
        if sum(d*x for d,x in zip(degrees,word))%3==rows_mod3
    }

def xor_projection_no_go():
    cases=0
    valid=[]
    for d in product(range(3),repeat=3):
        for m_mod3 in range(3):
            possible=degree_mod3_image(d,m_mod3)
            for charge in (0,1):
                target={word for word in product((0,1),repeat=3)
                        if parity3(word)==charge}
                if target<=possible:
                    valid.append((d,m_mod3,charge))
                    assert d==(0,0,0)
                    assert m_mod3==0
                else:
                    assert d!=(0,0,0) or m_mod3!=0
                cases+=1
    assert valid==[
        ((0,0,0),0,0),
        ((0,0,0),0,1),
    ],valid
    print(f"XOR3_FULL_RELATION_MOD3_ENUM={cases} PASS")
    print("XOR3_SEPARATED_PORT_DEGREES_MUST_BE_0_MOD3 = PROVED")

def equal3_minimal_gadget():
    rows=(("a","b","p"),("a","b","q"),("a","b","r"))
    degrees=Counter(v for clause in rows for v in clause)
    assert degrees=={"a":3,"b":3,"p":1,"q":1,"r":1}
    models=[]
    for bits in product((0,1),repeat=5):
        assignment=dict(zip(("a","b","p","q","r"),bits))
        if all(sum(assignment[j] for j in c)==1 for c in rows):
            models.append(assignment)
    projections=Counter((m["p"],m["q"],m["r"]) for m in models)
    assert projections==Counter({(0,0,0):2,(1,1,1):1})
    assert len(rows)==3
    assert all(len(set(a)&set(b))==2
               for i,a in enumerate(rows) for b in rows[i+1:])
    print("MINIMAL_EQ3_NONLINEAR_DEGREE1_PORTS_2_INTERNALS = EXACT")
    print("MINIMAL_EQ3_PROJECTIONS_000x2_111x1 = EXACT")
    return rows

def main():
    xor_projection_no_go()
    equal3_minimal_gadget()
    print("ISOLATED_POSITIVE_EO3_XOR3_PORT_DEG1_DEG2 = IMPOSSIBLE")
    print("COUPLED_PORT_NETWORK_OR_DIFFERENT_INTERFACE = NOT_RULED_OUT")
    print("CUBIC_TSEITIN_TO_LEGAL_SCL_BDFREGE_TRANSFER = OPEN")
    print("UNIVERSAL_POLYNOMIAL_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
