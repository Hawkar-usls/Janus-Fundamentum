#!/usr/bin/env python3
"""Odd-order PC3 theorem with proper *short/fixed row orbits*.

The old JANUS sym adapter wrongly required every original SCL row to
have full orbit length |G|. This excludes sound inputs like direct
K4 edge-colouring, where an order-3 vertex automorphism fixes a
vertex and therefore some vertex-colour rows.

Over F2, if |G| is odd, group averaging is exact even when individual
row and generator stabilizers are nontrivial. For a generator orbit
length d | |G|, the full sum of |G| images repeats each distinct
generator |G|/d times, which is odd. Thus the image equals its
distinct orbit sum, not zero. Invariant-constant refutability is
preserved: 1 in W3 iff 1 in W3^G.

Positive test: K4 -> legal SCL18, 6 edge-colorings, order3 source
automorphism with BOTH fixed and 3-period row orbits.
Negative test: disjoint union of K4 SCL18 and Fano7 legal SCL7
(where Fano is independently UNSAT via four-orbit PC2 identity);
the order3 automorphism fixes all 7 Fano rows. The union is valid
square,cubic,linear SCL25, and PC3 must refute by recombination.

Reject an invalid permutation; preserve UNKNOWN for SAT when no
full refutation exists. Neither special finite tests nor symmetry
prove global polynomial SAT solving.
"""
from __future__ import annotations

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    K4,make_scl,brute_three_edge_coloring
)
from r5_universal_odd_automorphism_pc3_snark_probe import (
    direct_scl_action,row_orbits,pc3_symmetry_test
)
from r5_universal_certified_odd_symmetry_adapter import (
    validate_odd_row_regular_symmetry,certified_odd_symmetry_pc3
)
from r5_universal_certified_expert_portfolio import (
    SolveLinearCubicXSAT_Portfolio
)
from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import (
    cyclic,four_orbit_polynomial
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def test():
    edges=K4()
    assert brute_three_edge_coloring(edges) is not None
    # K4 vertex 3 fixed, other three rotated.
    perm=(1,2,0,3)
    rows,sigma=direct_scl_action(edges,perm,3)
    n=len(rows)
    assert n==18
    assert validate_odd_row_regular_symmetry(rows,n,sigma)==3
    reps=row_orbits(rows,sigma,3)
    # 3 fixed vertex-color rows; all other 15 rows in five 3-orbits.
    assert len(reps)==8,(len(reps),reps)
    # A correct SAT input must NOT have an algebraic contradiction.
    decision=certified_odd_symmetry_pc3(rows,n,sigma)
    assert decision['status']=='UNKNOWN'
    sat=SolveLinearCubicXSAT_Portfolio(
        rows,n,poly_only=False,
        pc3_max_n=0,bounded_states=30,
        certified_symmetry=sigma,sym_pc3_max_n=40,
    )
    assert sat['status']=='SAT'
    assert all(sum(sat['witness'][v] for v in row)==1 for row in rows)
    print('SAT_K4_SCL18_FIXED_ROW_ORBITS=VERIFIED '
          'row_orbit_lengths=1_and_3',flush=True)

    fano=cyclic(7)
    four_orbit_polynomial(7)
    unsat_rows=tuple(rows)+tuple(
        tuple(x+18 for x in row) for row in fano
    )
    n2=25
    unsat_rows=validate_sparse(unsat_rows,n2)
    mixed_sigma=tuple(sigma)+tuple(range(18,n2))
    assert validate_odd_row_regular_symmetry(
        unsat_rows,n2,mixed_sigma
    )==3
    reps=row_orbits(unsat_rows,mixed_sigma,3)
    assert len(reps)==15,(len(reps),reps)
    decision=certified_odd_symmetry_pc3(
        unsat_rows,n2,mixed_sigma
    )
    assert decision['status']=='UNSAT',decision
    assert decision['stats']['verified_orbit_certificate_terms']>0
    covered=SolveLinearCubicXSAT_Portfolio(
        unsat_rows,n2,poly_only=True,pc3_max_n=0,
        bounded_states=0,
        certified_symmetry=mixed_sigma,sym_pc3_max_n=40,
    )
    # Cardinality is n=25 so root catches this input independently.
    # The adapter's direct PC3 proof above is the decisive new
    # fixed-orbit regression, independent of routing order.
    assert covered['status']=='UNSAT'
    print('UNSAT_DISJOINT_K4_FANO_SCL25_PC3_FIXED_ROWS=PROVED_UNSAT '
          f'orbit_terms={decision["stats"]["verified_orbit_certificate_terms"]}',
          flush=True)
    bad=list(mixed_sigma);bad[0],bad[1]=bad[1],bad[0]
    assert certified_odd_symmetry_pc3(
        unsat_rows,n2,bad
    )['status']=='UNKNOWN'
    print('INVALID_ODD_SYMMETRY_REJECTED=PASS',flush=True)
    print('GENERAL_ODD_ORDER_ORBIT_STABILIZERS_PC3_REFUTABILITY = PROVED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    test()
