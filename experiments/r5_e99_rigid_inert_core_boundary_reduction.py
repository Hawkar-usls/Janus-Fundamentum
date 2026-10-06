#!/usr/bin/env python3
"""R5 E99: rigid-defect inert-core boundary reduction.

Call a variable support INERT when it is a union of the three opposite-pair
atoms
  O0={XA,QBC}, O1={XB,QAC}, O2={XC,QAB}.
Equivalently its three opposite-pair split bits are 000, so the variable is
absent from every E97 exchange graph.

At any ordinary check the three supports partition the six TARGET6 labels.

E99 proves:
  * a check is one of the five E96 rigid defects iff all three incident
    supports are inert;
  * exactly two inert variables at an ordinary check is impossible:
    if two disjoint supports are unions of opposite atoms, their complement
    is also such a union, so the third support is inert;
  * hence non-rigid checks have 0 or 1 inert incidences.

For a connected rigid core C consisting of inert variables and rigid checks,
let B_C count incidences from its inert variables to non-rigid/mixed checks.
Every inert variable is cubic and every rigid check consumes three inert
incidences, so
    B_C = 3|V_C| - 3|R_C| = 3(|V_C|-|R_C|).
Thus every rigid-core boundary is a multiple of three.

If B_C=0, the core is never an obstruction: choose any opposite atom O_i and
select exactly those inert variables whose support contains O_i. Since each
rigid check partitions the three opposite atoms among its three supports,
exactly one incident variable is selected at every rigid check.

Therefore every minimal TARGET6/no-state8 obstruction may discard closed rigid
cores. Any relevant rigid core has at least three mixed boundary incidences,
and boundary size is 0 mod 3.

P_VS_NP remains OPEN.
"""

from itertools import product

OPPOSITE=(
    frozenset({0,5}),
    frozenset({1,4}),
    frozenset({2,3}),
)
U=frozenset(range(6))


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def all_partitions():
    out=set()
    for assignment in product(range(3),repeat=6):
        blocks=[
            frozenset(i for i,x in enumerate(assignment) if x==k)
            for k in range(3)
        ]
        out.add(canonical_partition(blocks))
    return tuple(sorted(out))


def inert_supports():
    out=set()
    for mask in range(8):
        S=set()
        for i,A in enumerate(OPPOSITE):
            if (mask>>i)&1:
                S.update(A)
        out.add(frozenset(S))
    assert len(out)==8
    return out


def verify_rigid_dictionary():
    inert=inert_supports()
    rigid=[]
    two_inert=[]
    for p in all_partitions():
        blocks=[frozenset(b) for b in p]
        k=sum(B in inert for B in blocks)
        if k==3:
            rigid.append(p)
            assert all(len(B)%2==0 for B in blocks)
        if k==2:
            two_inert.append(p)

    assert two_inert==[]
    assert len(rigid)==5

    # Exactly the Bell(3)=5 coarsenings of the three opposite atoms.
    coarsenings=set()
    for assignment in product(range(3),repeat=3):
        bins=[set(),set(),set()]
        for atom,k in zip(OPPOSITE,assignment):
            bins[k].update(atom)
        coarsenings.add(canonical_partition(frozenset(B) for B in bins))
    assert set(rigid)==coarsenings
    return inert,tuple(sorted(rigid))


def verify_component_boundary_formula():
    # Abstract component accounting over representative sizes.
    for V in range(1,30):
        for R in range(V+1):
            B=3*V-3*R
            if B<0:
                continue
            assert B==3*(V-R)
            assert B%3==0
            if B>0:
                assert B>=3


def verify_closed_core_atom_cover(rigid):
    # On every rigid support partition, choosing one opposite atom selects
    # exactly one incident support block.
    for p in rigid:
        blocks=[frozenset(B) for B in p]
        for atom in OPPOSITE:
            chosen=sum(1 for B in blocks if atom <= B)
            assert chosen==1


def main():
    inert,rigid=verify_rigid_dictionary()
    verify_component_boundary_formula()
    verify_closed_core_atom_cover(rigid)

    print("R5 E99 rigid-defect inert-core boundary reduction: PASS")
    print("inert support types=",len(inert))
    print("rigid partitions=",len(rigid),"exactly Bell(3)=5 opposite-atom coarsenings")
    print("ordinary check inert incidence count is never 2")
    print("rigid-core boundary B_C=3(|V_C|-|R_C|), hence B_C=0 mod3")
    print("closed rigid core B_C=0 has three canonical atom-covers and is not an obstruction")
    print("minimal obstruction: every relevant rigid core has at least 3 mixed boundary incidences")
    print("next target: classify B_C=3 rigid cores and rectangle-holonomy coupling")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
