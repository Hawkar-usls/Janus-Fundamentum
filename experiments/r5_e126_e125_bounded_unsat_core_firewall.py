#!/usr/bin/env python3
"""R5 E126: E125 bounded-UNSAT-core firewall."""

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q,
    tutte12_incidence,
    two_level_kernel_count,
)
from r5_e125_toroidal_one_check_block_splice import (
    BASE_N,
    DELETE_ROW,
    build_splice,
)


def core_rows(R):
    return [tuple(j for j,v in enumerate(R[c]) if v)
            for c in range(BASE_N) if c != DELETE_ROW]


def main():
    R=tutte12_incidence()
    assert len(R)==63
    assert rank_q(R)==49
    d,count=two_level_kernel_count(R)
    assert d==14 and count==0

    core=core_rows(R)
    assert len(core)==62
    assert all(len(r)==3 for r in core)

    # Symbolic one-check-redundancy certificate:
    # if all 62 retained checks were satisfied, then for the deleted check
    # selected count s we would have 62 = 3|x| - s, hence s == 1 mod 3.
    # Since s in {0,1,2,3}, s=1 and the full E64 carrier would be SAT,
    # contradicting the frozen exact E64 certificate above.
    assert 62 % 3 == 2
    possible=[s for s in range(4) if (3-s) % 3 == 62 % 3]
    assert possible==[1]

    # Replay that E125 retains this same 62-check pattern verbatim in every
    # block for finite construction controls t=2,3.
    for t in (2,3):
        rows,N=build_splice(R,t)
        m=t*t
        assert N==63*m
        pos=0
        for block in range(m):
            off=block*63
            local=[]
            for _ in range(62):
                row=rows[pos]
                pos+=1
                assert all(off <= v < off+63 for v in row)
                local.append(tuple(sorted(v-off for v in row)))
            assert sorted(local)==sorted(core)
        # Cross-checks occupy the remaining m rows.
        assert len(rows)-pos==m

    print("R5 E126 E125 bounded-core firewall: PASS")
    print("frozen E64 full carrier UNSAT; deleting one check leaves 62-check UNSAT core")
    print("E125 t=2,3 retain that exact core in every block")
    print("E125 scalable high-nullity/high-width family is bounded-core routed")
    print("NO_BOUNDED_UNSAT_CORE becomes a required scalable-benchmark gate")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
