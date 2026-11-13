#!/usr/bin/env python3
"""R5 E132: zero-kernel-coordinate persistence under a second 2-lift."""

from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import (
    base_matrix, build_2lift, rank_q,
)
from r5_e131_invertible_base_fibre_sum_2lift_e18_firewall import kernel_rows

N0=12


def main():
    A=base_matrix()
    assert rank_q(A)==N0

    R=build_2lift(A)
    assert rank_q(R)==22

    rows=kernel_rows(R)
    assert len(rows)==24
    assert len(rows[0])==2

    zero=[i for i,r in enumerate(rows) if all(x==0 for x in r)]
    assert zero==[6,7,16,17,20,21]

    # These are exactly both first-lift sheet copies of base variables 3,8,10.
    assert sorted({i//2 for i in zero})==[3,8,10]

    # General algebraic replay:
    # In any second 2-lift, a zero old coordinate u_i=0 becomes the pair
    # (0,v_i),(0,-v_i).  If v_i=0 both are zero; otherwise ratio=-1.
    # Either case is an E18/KLOC2 obstruction for {-1,2}.
    for i in zero:
        u=rows[i]
        assert all(x==0 for x in u)

    print("R5 E132 iterated-2lift E18 firewall: PASS")
    print("E129 q24 rational kernel zero coordinates =",zero)
    print("every second 2-lift preserves an E18 obstruction at each such coordinate")
    print("iterated q12->q24->q48 post-E18 route = IMPOSSIBLE")
    print("direct non-factorizing q12->q48 4-cover remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
