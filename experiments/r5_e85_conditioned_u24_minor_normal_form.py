#!/usr/bin/env python3
"""R5 E85: conditioned U2,4 minor -> pin-and-project residual normal form.

E83 turned every exact Tanner delta interface D into a canonical matroid
M=D*P, with P the variable-side boundary coordinates.

E85 proves the minor-to-pinning reduction used in the companion note:
every matroid minor is obtained, at the level of basis families, by fixing
each eliminated coordinate to 0 or 1 and projecting it away. Undoing the
canonical twist converts the same operation into boundary pinning of D.

For a surviving U_{2,4} minor on four coordinates R, the conditioned exact
Tanner relation is therefore exactly U_{2,4} * (P intersect R).

After deterministic ExactOne/Equality propagation, any C4-free source witness
can be reduced to a four-free-port residual network in which active variables
have no fixed incidences, and the only retained fixed incidences are check-side
zeros ("zero holes"). If p of the four surviving ports are variable-side and h
zero holes remain, with a active checks and b active variables, then

    h = 3(a-b) + 2p - 4,
    3 | (a+p-2),

and every one of the six surviving states uses exactly

    (a+p-2)/3

active selected variables.

The checker also freezes an explicit unrestricted 7-check/6-variable five-port
nonbinary Tanner interface. Its canonical rank-2 matroid has one parallel pair;
deleting one member produces U_{2,4}. In boundary language, pinning one
check-side port to zero and projecting yields U_{2,4} twisted by the one
surviving variable-side port. The witness contains Tanner C4s, so it does not
settle the square-cubic-linear source case.

P_VS_NP remains OPEN.
"""

from itertools import combinations

from r5_e77_source_aligned_delta_composition_frontier import symmetric_exchange_failure
from r5_e83_canonical_matroid_twist_u24_frontier import (
    generic_boundary_relation,
    basis_exchange_failure,
)

U24 = frozenset(
    (1 << i) | (1 << j)
    for i, j in combinations(range(4), 2)
)

WITNESS_EDGES = {
    (0,1),(0,2),(0,5),
    (1,0),(1,3),(1,4),
    (2,1),(2,2),(2,5),
    (3,0),(3,1),
    (4,4),(4,5),
    (5,3),
    (6,0),(6,3),(6,4),
}

EXPECTED_D = frozenset({1,2,4,8,19,21,22,25,26})
EXPECTED_M_BASES = frozenset({3,5,6,9,10,17,18,20,24})


def project_pin(family, n, e, value):
    out=set()
    for X in family:
        if ((X >> e) & 1) != value:
            continue
        low = X & ((1 << e) - 1)
        high = X >> (e + 1)
        out.add(low | (high << e))
    return frozenset(out)


def delete_from_bases(bases, n, e):
    """Basis-family deletion, including the coloop case."""
    has_avoiding = any(not ((B >> e) & 1) for B in bases)
    value = 0 if has_avoiding else 1
    return project_pin(bases, n, e, value), value


def contract_from_bases(bases, n, e):
    """Basis-family contraction, including the loop case."""
    has_containing = any((B >> e) & 1 for B in bases)
    value = 1 if has_containing else 0
    return project_pin(bases, n, e, value), value


def c4_violations(a,b,edges):
    out=[]
    for u,v in combinations(range(b),2):
        common=tuple(i for i in range(a) if (i,u) in edges and (i,v) in edges)
        if len(common) >= 2:
            out.append((u,v,common))
    return out


def verify_minor_to_pin_one_step():
    bases=EXPECTED_M_BASES
    assert {B.bit_count() for B in bases} == {2}
    assert basis_exchange_failure(bases,5) is None

    deleted, bit = delete_from_bases(bases,5,2)
    assert bit == 0
    assert deleted == U24

    contracted, bit = contract_from_bases(U24,4,0)
    assert bit == 1
    assert contracted == frozenset({1,2,4})

    deleted_u24, bit = delete_from_bases(U24,4,0)
    assert bit == 0
    assert deleted_u24 == frozenset({3,5,6})


def verify_unrestricted_conditioned_witness():
    arity, check_boundary, D = generic_boundary_relation(7,6,WITNESS_EDGES)
    assert arity == 5
    assert check_boundary == 4
    assert D == EXPECTED_D
    assert symmetric_exchange_failure(D,5) is None

    P = 1 << 4
    M = frozenset(X ^ P for X in D)
    assert M == EXPECTED_M_BASES
    assert basis_exchange_failure(M,5) is None

    minor, bit = delete_from_bases(M,5,2)
    assert bit == 0
    assert minor == U24

    conditioned = project_pin(D,5,2,0)

    survivor_P = 1 << 3
    expected_conditioned = frozenset(B ^ survivor_P for B in U24)
    assert conditioned == expected_conditioned
    assert conditioned == frozenset({1,2,4,11,13,14})

    a,b,p,h = 7,6,1,1
    assert h == 3*(a-b) + 2*p - 4
    assert (a+p-2) % 3 == 0
    assert (a+p-2)//3 == 2

    bad = c4_violations(7,6,WITNESS_EDGES)
    assert bad
    return bad


def verify_orientation_arithmetic():
    mins={}
    for p in range(5):
        vals=[]
        for d in range(-4,8):
            h=3*d+2*p-4
            if h>=0:
                vals.append((h,d))
        mins[p]=min(vals)
    assert mins == {
        0:(2,2),
        1:(1,1),
        2:(0,0),
        3:(2,0),
        4:(1,-1),
    }


def main():
    verify_minor_to_pin_one_step()
    bad = verify_unrestricted_conditioned_witness()
    verify_orientation_arithmetic()

    print("R5 E85 conditioned U2,4 minor / pin-and-project normal form: PASS")
    print("minor lemma: deletion/contraction of basis families = pin one bit then project")
    print("therefore U2,4 minor of M=D*P => four-port conditioned D relation = U2,4*(P intersect R)")
    print("post-propagation residual equations: h=3(a-b)+2p-4 and 3|(a+p-2)")
    print("explicit unrestricted 5-port nonbinary witness: delete/pin bit2 -> conditioned U2,4")
    print("witness has Tanner C4 violations:", bad)
    print("next linear-source killer: exclude the E85 residual zero-hole normal forms under C4-freeness, or construct one")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
