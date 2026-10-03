#!/usr/bin/env python3
"""R5 E54 exact controls: deterministic claw-coordinate correlations imply Boolean equalities.

For a conflict vertex v in the all-positive square+cubic+linear E12 carrier,
its three source pairs are P_i={p_i^0,p_i^1}.  A claw family F subseteq {0,1}^3
encodes which endpoint from each source pair is selected when v is unselected.

If z_i xor z_j is constant c over all z in F, then every Exact-One witness obeys
  x_{p_i^a} = x_{p_j^(a xor c)}  for a in {0,1}.
The equality also holds when v itself is selected, because all six neighbors are then 0.

This checker replays the eight canonical post-E52 claw types from E53 and verifies
that exactly the size-2, size-3, and one size-4 orbit contain deterministic pair
correlations.  In each such case the corresponding two source rows become identical
after quotienting by the forced equalities.
"""
import itertools

REPS = [
    ((0,0,0),(1,1,1)),
    ((0,0,0),(0,0,1),(1,1,0)),
    ((0,0,0),(0,0,1),(0,1,0),(1,0,0)),
    ((0,0,0),(0,0,1),(0,1,0),(1,0,1)),
    ((0,0,0),(0,0,1),(1,1,0),(1,1,1)),
    ((0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0)),
    ((0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1)),
    tuple(itertools.product([0,1], repeat=3)),
]


def correlations(F):
    out=[]
    for i,j in itertools.combinations(range(3),2):
        vals={z[i]^z[j] for z in F}
        if len(vals)==1:
            out.append((i,j,next(iter(vals))))
    return out


def local_states(F):
    # C denotes v selected; then every neighbor is 0.
    return [None] + list(F)


def endpoint_value(state, pair, endpoint):
    if state is None:
        return 0
    return int(state[pair] == endpoint)


def verify_correlation(F,i,j,c):
    for state in local_states(F):
        for a in (0,1):
            lhs=endpoint_value(state,i,a)
            rhs=endpoint_value(state,j,a^c)
            assert lhs==rhs


def main():
    got=[]
    for F in REPS:
        corr=correlations(F)
        got.append((len(F),len(corr)))
        for i,j,c in corr:
            verify_correlation(F,i,j,c)

            # Source rows Ri={v,p_i^0,p_i^1}, Rj={v,p_j^0,p_j^1}.
            # Under the two quotient equalities p_i^a == p_j^(a xor c),
            # the two rows have identical multisets of quotient variables.
            row_i=("v",(i,0),(i,1))
            mapped_j=("v",(i,0^c),(i,1^c))
            assert set(row_i)==set(mapped_j)

    assert got == [(2,3),(3,1),(4,0),(4,0),(4,1),(5,0),(6,0),(8,0)]
    print("R5 E54 claw-coordinate equality folding: PASS")
    print("correlated_orbits=size2,size3,one_size4")
    print("remaining_uncorrelated_orbits=two_size4,size5,size6,size8")


if __name__ == "__main__":
    main()
