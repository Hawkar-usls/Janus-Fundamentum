#!/usr/bin/env python3
"""R5 constructive bounded-cell Matchgate-SUM proof decomposition.

NATIVE TWO-NODE W--GHZ cell T4 has EXACT matchgate-sum rank 2
in the ORIGINAL Boolean boundary basis:
   T4 = |0011> [even matchgate]
      + (|1000> + |0100>) [odd matchgate].
It cannot have rank 1 under ANY invertible local GL2 (independent
earlier flattening-rank no-go), hence min=2 even with gauges.

NATIVE FOUR-NODE W--GHZ--W--GHZ path cell T6 has EXACT
matchgate-sum rank 3 in the ORIGINAL Boolean boundary basis:
   E = |100100> + |010100>                [even matchgate]
   S = |001000>                           [odd matchgate]
   C = |100011> + |010011>                [odd matchgate]
   T6=E+S+C.
Every component satisfies ALL MATCHGATE IDENTITIES for its arity,
verified independently over all alpha,beta bit masks.

Why fixed-basis rank cannot be 2:
T6 has both even- and odd-parity support. A 2-summand
standard-matchgate decomposition must contain precisely ONE even
and ONE odd summand (each standard matchgate has pure parity).
Consequently they would have to equal the UNIQUE parity projections
E and O=S+C. But odd projection O violates an explicit matchgate
identity: alpha=0, beta=53 with flip positions 0,2,4,5 (zero-based,
little-endian mask convention) gives MGI residual +1.
Therefore rank_original_basis(T6)=3 exactly.

This is a CONSTRUCTIVE small-block compression, NOT a universal
polynomial contraction method. A naive distributive expansion of
p independent rank-3 cells can contain 3^p Pfaffian terms:
local bounded matchgate-sum rank does NOT establish a
polynomial-time all-SCL algorithm. An additional global
cancellation/closure/reduction theorem would be required.
"""
from __future__ import annotations
from itertools import product

from r5_universal_grouped_two_node_matchgate_flatten_rank_nogo import (
    fused_cell, verify_native_two_node_cell, BITS4,
)
from r5_universal_grouped_four_node_matchgate_rankrigidity_nogo import (
    four_node_path_tensor, verify_source_four_node_path, BITS6,
)


def bits_to_mask(bits):
    return sum(bit<<i for i,bit in enumerate(bits))


def mask_to_bits(mask,n):
    return tuple((mask>>i)&1 for i in range(n))


def to_mask_dictionary(tensor,n):
    assert len(tensor)==(1<<n)
    return {bits_to_mask(bits):value for bits,value in tensor.items()}


def parity_projection(tensor,n,parity):
    return {mask:(value if mask.bit_count()%2==parity else 0)
            for mask,value in tensor.items()}


def mgi_residual(tensor,n,alpha,beta):
    """Cai-Gorenstein matchgate identity, independently evaluated."""
    diffs=[i for i in range(n) if (alpha^beta)&(1<<i)]
    return sum((-1)**(j+1)*
               tensor[alpha^(1<<pos)]*tensor[beta^(1<<pos)]
               for j,pos in enumerate(diffs))


def verify_all_matchgate_identities(tensor,n):
    """Complete independent quadratic verifier at these tiny arities."""
    assert set(tensor)==set(range(1<<n))
    has_even=any(v for mask,v in tensor.items() if mask.bit_count()%2==0)
    has_odd=any(v for mask,v in tensor.items() if mask.bit_count()%2==1)
    assert not (has_even and has_odd),"matchgate parity violated"
    violations=[]
    for alpha in range(1<<n):
        for beta in range(1<<n):
            value=mgi_residual(tensor,n,alpha,beta)
            if value:violations.append((alpha,beta,value))
    assert not violations,("quadratic MGI violated",violations[:3])
    return True


def components_4():
    T=to_mask_dictionary(fused_cell(),4)
    even=parity_projection(T,4,0)
    odd=parity_projection(T,4,1)
    assert sum(bool(v) for v in even.values())==1
    assert sum(bool(v) for v in odd.values())==2
    assert all(even[i]+odd[i]==T[i] for i in T)
    assert verify_all_matchgate_identities(even,4)
    assert verify_all_matchgate_identities(odd,4)
    return T,(even,odd)


def components_6():
    T=to_mask_dictionary(four_node_path_tensor(),6)
    E=parity_projection(T,6,0)
    O=parity_projection(T,6,1)
    # In little-endian bit convention:
    # T6: |001000> (mask4), |100100> (mask9), |010100> (mask10),
    #     |100011> (mask49), |010011> (mask50).
    assert {m for m,v in E.items() if v}=={9,10}
    assert {m for m,v in O.items() if v}=={4,49,50}
    S={m:(v if m==4 else 0) for m,v in T.items()}
    C={m:(v if m in (49,50) else 0) for m,v in T.items()}
    assert all(E[m]+S[m]+C[m]==T[m] for m in T)
    for component in (E,S,C):
        assert verify_all_matchgate_identities(component,6)

    # Exact minimality witness: E+O are the UNIQUE two parity
    # projections; O fails a specific standard MGI by 1.
    assert mgi_residual(O,6,0,53)==1
    assert O[4]==O[49]==O[50]==1
    assert not any(O[1<<i] for i in range(6) if i!=2)
    return T,(E,S,C),O


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        K4,K33,petersen_graph,make_scl,
    )

    T4,(E4,O4)=components_4()
    T6,(E6,S6,C6),O6=components_6()
    print("GROUPED_TWO_NODE_MATCHGATE_SUM_RANK_ORIGINAL_BASIS=2_PROVED")
    print("GROUPED_FOUR_NODE_MATCHGATE_SUM_RANK_ORIGINAL_BASIS=3_PROVED")
    print("FOUR_NODE_ODD_PROJECTION_MGI_ALPHA0_BETA53=1_NONMATCHGATE")
    print("FOUR_NODE_THREE_STANDARD_MATCHGATE_COMPONENTS=FULL_MGI_VERIFIED")

    for name,rows,n in (
        ("FANO7",cyclic(7),7),
        ("K4",*make_scl(K4())[:2]),
        ("K33",*make_scl(K33())[:2]),
        ("PETERSEN",*make_scl(petersen_graph())[:2]),
    ):
        assert verify_native_two_node_cell(rows,n,0,rows[0][0])
        assert verify_source_four_node_path(rows,n)
        print(f"{name}_SOURCE_REPLAYED_2AND4_NODE_MATCHGATE_SUM=PASS",
              flush=True)

    # Counterfeit witness: omit one of the three T6 components.
    truncated={m:E6[m]+S6[m] for m in T6}
    assert truncated!=T6 and truncated[49]==0 and T6[49]==1
    print("TRUNCATED_GROUPED_MATCHGATE_SUM_REJECTED=PASS")

    # A fake statement that O6 is itself a matchgate must fail at
    # the fixed source-indexed original tensor identity.
    assert mgi_residual(O6,6,0,53)!=0
    try:
        verify_all_matchgate_identities(O6,6)
    except AssertionError:
        print("FORGED_ODD_MATCHGATE_CERTIFICATE_REJECTED=PASS")
    else:
        raise AssertionError("accepting a non-matchgate odd projection")

    print("FIXED_CELL_PFAFFIAN_SUM_COMPRESSION=EXACT_LOCAL_ONLY")
    print("GLOBAL_POLYNOMIAL_PFAFFIAN_SUM_COLLAPSE=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
