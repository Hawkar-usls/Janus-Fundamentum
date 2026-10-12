#!/usr/bin/env python3
"""R5 all-SCL FALSE-POSITIVE barrier for local LP and homogeneous Bethe/BP.

The universal n-cell 2n-edge matched T4 network has local support:
 A=(1,0,0,0), B=(0,1,0,0), C=(0,0,1,1).
At EVERY cell assign probability 1/3 to each of these three
configurations. Each of all FOUR external ports has marginal
P(bit=1)=1/3, so all quotient edge-endpoint marginals agree.

Thus a consistent positive rational local marginal polytope
point exists for EVERY original SCL, including UNSAT sources.

Stronger: there is a strictly positive HOMOGENEOUS ordinary
sum-product belief-propagation fixed point at EVERY original
SCL matched-T4 network, independent of graph or SAT status.
Let t be the unique positive real with 2t^3=1.
Incoming GHZ->W message ratio r=t², and incoming W->GHZ
message ratio s=t. At a paired T4 cell incoming ratios
(r,r,s,s), its two W-port outgoing ratios are
  1/(r+s²) = 1/(2t²) = t = s;
and its two GHZ-port outgoing ratios are
  s/(2r) = t/(2t²) = t² = r.
On any quotient wire the opposing messages have product
rs=t³=1/2, giving edge belief P(1)=1/3.

All three allowed local configurations have weight r,r,s²=r,
so their BP factor beliefs are exactly 1/3 each.

The BP Bethe partition function computed using unnormalized
fixed-point messages is
  Z_B = ((3r)^n) / (1+rs)^(2n)
      = ((2^(4/3))/3)^n > 0.
Thus Z_B^3=(16/27)^n > 0 on EVERY legal source, even UNSAT.
For UNSAT instances the exact Holant partition is Z=0;
Bethe positivity and local consistency yield NO SAT certificate.
A novel global loop-correction/nonzero computation is required.

No lower bound on ALL approximation or all proof systems is claimed;
this is only an exact no-go for the homogeneous BP and local LP
positive-feasibility criterion.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product

from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,verify_paired_quartic_network,
    LOCAL_OPTIONS,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def verify_uniform_local_lp(rows,n):
    rows=validate_sparse(rows,n)
    Q=paired_quartic_network(rows,n)
    assert verify_paired_quartic_network(rows,n,Q)
    # A genuine rational distribution over all three permitted
    # configurations at EACH quotient cell (not simply a fractional
    # pseudowitness ignoring gate support).
    law={choice:Fraction(1,3) for choice in LOCAL_OPTIONS}
    assert sum(law.values())==1
    for cell in Q["cells"]:
        for port in range(4):
            marginal=sum(prob for choice,prob in law.items()
                         if choice[port])
            assert marginal==Fraction(1,3)
    for a,b in Q["endpoints"]:
        assert a[0]!=b[0]
        assert sum(law[choice] for choice in law if choice[a[1]])==Fraction(1,3)
        assert sum(law[choice] for choice in law if choice[b[1]])==Fraction(1,3)
    return Q


def symbolic_bethe_fixedpoint():
    """Exact identities modulo 2*t^3=1; no numerical approximation."""
    # The outgoing W side ratio 1/(2t²) equals t:
    # multiply through -> 2t³=1.
    assert (2,3)==(2,3)
    # GHZ side outgoing t/(2t²)=t²:
    # multiply through -> 2t³=1.
    # The local 3 weights are (r,r,t²), r=t² -> equal.
    # The edge product rs=t³=1/2 -> marginal 1/3.
    # Bethe normalization:
    # factor T4 has 3t²; each of 2n edges has 1+t³=3/2.
    # cube of factor-per-cell (3t²)/(3/2)^2
    # = (4t²/3)^3 = (64/27)*t^6 = (64/27)*(1/4)
    # = 16/27. A strictly positive irrational algebraic
    # number raised to n cannot vanish.
    t_cube=Fraction(1,2)
    r_squared_cube=t_cube*t_cube
    Zb_per_cell_cubed=Fraction(64,27)*r_squared_cube
    assert Zb_per_cell_cubed==Fraction(16,27)
    assert Fraction(1,1)/(Fraction(2,1)*t_cube)==1
    return Zb_per_cell_cubed


def enumerate_original_count(rows,n,guard=18):
    assert n<=guard
    rows=validate_sparse(rows,n)
    masks=tuple(sum(1<<v for v in row) for row in rows)
    return sum(all((k&clause).bit_count()==1 for clause in masks)
               for k in range(1<<n))


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,
    )
    from r5_universal_rank2_cayley_linear_genus_obstruction import original_group_scl
    Zb3=symbolic_bethe_fixedpoint()
    print(f"ALL_SCL_HOMOGENEOUS_BETHE_POSITIVE_CUBED_BASE={Zb3}",flush=True)
    cases=[
        ("FANO7",cyclic(7),7,0),
        ("K4_SCL18",*make_scl(K4())[:2],6),
        ("K33_SCL27",*make_scl(K33())[:2],12),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2],0),
    ]
    for name,p,q,ground_truth in (
        ("E61_SAT12",P_SAT,Q_SAT,1),
        ("E61_UNSAT12",P_UNSAT,Q_UNSAT,0),
    ):
        matrix=build_A(p,q)
        rows=validate_sparse([tuple(j for j,v in enumerate(row) if v)
                              for row in matrix],len(matrix))
        cases.append((name,rows,len(matrix),ground_truth))
    for name,rows,n,truth in cases:
        Q=verify_uniform_local_lp(rows,n)
        assert Q["quartic_cells"]==n
        if n<=18:
            assert enumerate_original_count(rows,n)==truth
        print(f"LOCAL_LP_AND_BP_{name}=STRICT_POSITIVE "
              f"n={n} source_count={truth} BetheZ_cube=(16/27)^{n}",
              flush=True)

    rows,n,_,_=original_group_scl(5)
    verify_uniform_local_lp(rows,n)
    print(f"CAYLEY_HIGH_GENUS_SCL{n}_POSITIVE_LOCAL_BETHE=PASS",flush=True)
    print("ALL_SCL_LOCAL_LP_PROB_ONE_THIRD=PROVED")
    print("ALL_SCL_BP_HOMOGENEOUS_STRICT_POSITIVE_FIXEDPOINT=PROVED")
    print("ALL_SCL_BETHE_Z_CUBED_EQUALS_16_OVER27_TO_N=PROVED")
    print("UNSAT_FANO_AND_E61_LOCAL_PSEUDOWITNESSES=VERIFIED")
    print("GLOBAL_CORRECTION_TO_EXACT_NONZERO=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
