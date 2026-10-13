#!/usr/bin/env python3
"""Exact abstract 6-port Exact-One boundary parity and Kempe-closure AUDIT.

This does NOT construct a cubic multipole. It tests only TWO necessary
colour-state conditions shared by all cubic multipoles:
(1) cubic parity: each of three port colours occurs evenly (six ports);
(2) for EVERY internal 3-edge-colouring and each pair of colours,
    its two-colour Kempe subgraph pairs the semiedges of these colours
    along paths. All subsets of disjoint alternating paths can be
    switched independently while remaining proper. Thus, for each
    physical six-port boundary state and each colour pair, some
    perfect matching of its 2-colour terminals has its COMPLETE
    2^k path-toggle orbit in the multipole's physical state set.

We verify the EXACT proposed abstract onehot state set satisfies (1),
and for (2) give a matching certificate for EVERY state/colour pair.
This proves that naive parity+existential-boundary Kempe criteria
CANNOT by themselves disprove existence of an exposed onehot sixpole.
The required interior consistency across all states is UNPROVED.
"""
from itertools import product


ONEHOT={(1,0,0),(0,1,0),(0,0,1)}


def missing_colour_parity(state):
    return all(state.count(c)%2==0 for c in range(3))


def bit_tuple(p):
    return tuple(int(p[i]==p[i+3]) for i in range(3))


def matchings(vertices):
    if not vertices:
        yield ()
        return
    first,*rest=vertices
    for j,other in enumerate(rest):
        for tail in matchings(rest[:j]+rest[j+1:]):
            yield ((first,other),)+tail


def path_orbit(state,col_a,col_b,matching):
    for mask in range(1<<len(matching)):
        state_new=list(state)
        for k,edge in enumerate(matching):
            if mask & (1<<k):
                for port in edge:
                    old=state_new[port]
                    assert old in (col_a,col_b)
                    state_new[port]=col_b if old==col_a else col_a
        yield tuple(state_new)


def full_boundary_relation():
    all_states=set()
    for p in product(range(3),repeat=6):
        if bit_tuple(p) in ONEHOT and missing_colour_parity(p):
            all_states.add(p)
    assert len(all_states)==108, len(all_states)
    assert {bit_tuple(p) for p in all_states}==ONEHOT
    return frozenset(all_states)


def main():
    physical_states=full_boundary_relation()
    nproof=0
    witness=[]
    for state in sorted(physical_states):
        assert missing_colour_parity(state)
        for a,b in ((0,1),(0,2),(1,2)):
            indices=tuple(i for i,c in enumerate(state) if c in (a,b))
            assert len(indices)%2==0
            found=None
            for pairing in matchings(indices):
                if all(toggled in physical_states
                       for toggled in path_orbit(state,a,b,pairing)):
                    found=pairing
                    break
            assert found is not None,("KEMPE_NECESSARY_OBSTRUCTION",state,a,b)
            assert all(bit_tuple(t) in ONEHOT
                       for t in path_orbit(state,a,b,found))
            nproof+=1
            if len(witness)<5:
                witness.append((state,(a,b),found))
    assert nproof==108*3
    print("EXACTONE_6PORT_ABSTRACT: 108 full physical boundary colour states")
    print("CUBIC_PARITY: every state has even count per colour PASS")
    print("KEMPE_PATH_MATCHING_CLOSURE: all 324 state*colour-pair cases PASS")
    print("KEMPE_CERTIFICATE_EXAMPLES",witness)
    print("IMPLICATION: parity plus existential Kempe-boundary closure is")
    print("  TOO WEAK to prove universal nonexistence of Exact-One sixpole.")
    print("  Does NOT witness one single fixed graph, nor a PC reduction.")
    print("OPEN_SIXPOLE_REALIZABILITY=OPEN")
    print("UNBOUNDED_NATIVE_PC_DEGREE=OPEN; UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
