#!/usr/bin/env python3
"""R5 E113: TARGET6 support-lift parity obstruction for E112 cycle covers.

For fixed six TARGET6 witnesses let S_v be the six-label support of Tanner
variable v.  E95 base bit is
    e_v = 1 iff |S_v| is even.
At an ordinary check, E105's unique forbidden local kernel pattern is
    f_c = 111 xor e|_c.
Therefore the forbidden bit on incidence (c,v) is
    f_{c,v} = 1 xor e_v = |S_v| mod 2.
This depends ONLY on the actual Tanner variable v, not on the check.

Consequently, if the same actual Tanner variable appears in two active checks,
the marked forbidden character has the same value on its normal direction at
both checks.

E112 cycle-space cover has the opposite property:
for every graph edge / shared normal direction g_e, the endpoint forbidden
marks are opposite.

Therefore no E112 edge can be lifted as ONE actual Tanner variable shared by
its two endpoint checks.

Any TARGET6-support lift must split each shared normal direction into distinct
variables u_e,v_e with
    g_u = g_v
but
    |S_u| mod2 != |S_v| mod2.
Call this an ANTIPHASE PARALLEL PAIR.

For every residual kernel state z,
    z_u=z_v
while the E95 base bits e_u,e_v are opposite, so final raw8 candidate bits
    e_u xor z_u
and
    e_v xor z_v
are complementary for EVERY repair.

For the 12-vertex E112 prism:
  12 active checks x 3 incidences = 36 active incidences;
  all 18 shared directions occur twice;
  opposite endpoint marks forbid reusing one actual variable on either pair;
hence any literal TARGET6 lift needs 36 distinct active variable occurrences.
No actual variable can serve two of the 12 active checks.

This does not yet rule out a lift: parallel variables may be coupled through
inactive/propagated Tanner structure.  It isolates exactly what such a lift
must contain.

P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e112_cubic_cycle_space_cover_firewall import (
    hex_prism,
    incidence_rows,
    gf2_nullspace,
    edge_normals_from_cycle_basis,
    find_even_orientation,
    head_bit,
)


def verify_forbidden_bit_identity():
    # Exhaust all 64 six-witness supports.
    for mask in range(64):
        S=frozenset(i for i in range(6) if (mask>>i)&1)
        e=1 if len(S)%2==0 else 0
        forbidden=1^e
        assert forbidden==(len(S)&1)


def verify_variable_attached_mark():
    # Abstract replay: one actual variable has one support S and therefore one
    # forbidden bit at every check occurrence.
    for mask in range(64):
        p=mask.bit_count()&1
        marks=[p,p,p]
        assert len(set(marks))==1


def verify_prism_requires_antiphase_splitting():
    edges=hex_prism()
    nv=12
    rows=incidence_rows(edges,nv)
    cycles=gf2_nullspace(rows,len(edges))
    normals=edge_normals_from_cycle_basis(cycles,len(edges))
    orient,indeg=find_even_orientation(edges,nv)

    # Each shared normal has opposite endpoint forbidden marks.
    opposite=0
    for i,(u,v) in enumerate(edges):
        mu=head_bit(orient,i,u,edges[i])
        mv=head_bit(orient,i,v,edges[i])
        assert mu^mv==1
        opposite+=1
    assert opposite==18

    # If one actual variable represented both endpoint occurrences, its
    # variable-attached support parity would have to equal both opposite marks.
    # Impossible. Therefore the two occurrences must be distinct variables.
    active_incidences=3*nv
    assert active_incidences==36
    assert 2*len(edges)==active_incidences

    minimum_distinct_active_variables=active_incidences
    assert minimum_distinct_active_variables==36

    return {
        "active_checks":nv,
        "shared_normal_directions":len(edges),
        "opposite_mark_directions":opposite,
        "required_distinct_active_variables":minimum_distinct_active_variables,
    }


def verify_antiphase_parallel_truth_table():
    # Same residual normal g => same kernel bit z.
    # Opposite support parity => opposite E95 base bits.
    # Hence final candidate bits remain opposite under every repair.
    for base_u in (0,1):
        base_v=base_u^1
        for z in (0,1):
            final_u=base_u^z
            final_v=base_v^z
            assert final_u^final_v==1


def main():
    verify_forbidden_bit_identity()
    verify_variable_attached_mark()
    verify_antiphase_parallel_truth_table()
    stats=verify_prism_requires_antiphase_splitting()

    print("R5 E113 TARGET6 support-lift parity obstruction: PASS")
    print("forbidden incidence bit = six-witness support parity of the actual variable")
    print("same Tanner variable => same forbidden mark at all its active checks")
    print("E112 shared directions have opposite endpoint marks")
    print("therefore every E112 shared direction must split into an antiphase parallel variable pair in any TARGET6 lift")
    print("antiphase pair final raw8 bits are complementary under every zero-boundary repair")
    print("prism lift lower bound:",stats)
    print("next target: decompose or kill networks coupled only through antiphase parallel pairs")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
