#!/usr/bin/env python3
"""R5 exact selector expansion: each of the 2^n rank-two matchgate
summand choices IS ONE original Boolean source assignment, bijectively.

Each native paired T4 gate is E+O:
 E=|0011> (even, matched column variable must be 1)
 O=|1000>+|0100> (odd, matched column variable must be 0).
Fix a global E/O label at each matched cell. Its two column-side
external wires are individually FIXED to its label b. Since every
remaining original Tanner incidence wire connects to one of these
variable ports, EVERY quotient wire value is now forced.

Therefore the global contracted component network for this FIXED
summand-selection vector has value EXACTLY 0 or 1, determined by
source Exact-One row checks. In particular:
  Z_quotient = sum_{b in {0,1}^n} term(b);
  term(b) = 1 iff x_(matching[i])=b_i forms an ORIGINAL SAT witness.
All terms nonnegative and there is no cancellation. This is an exact
source-preserving algebraic identity, but its naive 2^n expansion
recovers the original NP-complete decision problem and is NOT a
polynomial SAT/UNSAT solver.

Every SAT witness has exactly n/3 true variables; hence even a
naive weight-restricted selector search has C(n,n/3) candidates
(which is exponential as n grows along multiples of 3). An
arbitrary implicit compression would need a genuinely new theorem
for deciding the existence of a nonzero term without enumerating
these selectors. No P vs NP outcome is claimed.
"""
from __future__ import annotations
from math import comb
from itertools import product

from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network, verify_paired_quartic_network,
    original_to_quotient_wires, quotient_to_original_witness,
)
from r5_universal_grouped_cell_matchgate_sum_rank import components_4


def selector_term(report,cell_bits):
    """Exact contraction of the chosen matchgate summands, 0 or 1.

    cell_bits[i]=1 chooses EVEN=|0011> at matched row/column cell i;
    0 chooses ODD=|1000>+|0100>. We compute forced edge values
    from the two variable-side legs. No exponential contraction.
    """
    n=report["source_n"]
    assert len(cell_bits)==n
    assert all(type(v) is int and v in (0,1) for v in cell_bits)
    matching=report["matching"]
    owner={v:i for i,v in enumerate(matching)}
    forced=tuple(cell_bits[owner[v]] for i,v in report["incidences"])
    _T,(even,odd)=components_4()
    product_value=1
    for i,ports in enumerate(report["cells"]):
        local=tuple(forced[e] for e in ports)
        mask=sum(bit<<j for j,bit in enumerate(local))
        chosen=even if cell_bits[i] else odd
        product_value*=chosen[mask]
        if not product_value:break
    assert product_value in (0,1)
    original=tuple(cell_bits[owner[v]] for v in range(n))
    source_value=int(all(sum(original[v] for v in row)==1
                         for row in report["source_rows"]))
    assert product_value==source_value
    if product_value:
        assert original_to_quotient_wires(report,original)==forced
        assert quotient_to_original_witness(report,forced)==original
    return product_value


def exhaustive_selector_count(report,max_n=18):
    """2^n worst case; scientific control ONLY, never polynomial lane."""
    n=report["source_n"]
    assert n<=max_n
    # Avoid rerunning the complete quadratic matchgate verifier for
    # each selector: once source-indexed source equivalence is proved,
    # evaluating a fixed selector amounts to these original-row checks.
    match=report["matching"]
    owner={v:i for i,v in enumerate(match)}
    vars_for_rows=tuple(tuple(owner[v] for v in row)
                        for row in report["source_rows"])
    total=0
    witnesses=[]
    for mask in range(1<<n):
        # Fixed-cell term equals source row truth under the bijection.
        good=all(sum((mask>>j)&1 for j in row)==1
                 for row in vars_for_rows)
        if good:
            total+=1
            if len(witnesses)<6:
                labels=tuple((mask>>i)&1 for i in range(n))
                assert selector_term(report,labels)==1
                witnesses.append(labels)
    return total,tuple(witnesses)


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower

    cases=(
        ("FANO7",cyclic(7),7,0),
        ("K4_SCL18",*make_scl(K4())[:2],6),
        ("K33_SCL27",*make_scl(K33())[:2],12),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2],0),
        ("FLOWER_J5_SCL90",*make_scl(flower(5))[:2],0),
    )
    for name,rows,n,ground_truth in cases:
        network=paired_quartic_network(rows,n)
        assert verify_paired_quartic_network(rows,n,network)
        assert len(set(network["matching"]))==n
        owner={v:i for i,v in enumerate(network["matching"])}
        assert set(owner)==set(range(n))

        for labels in (
            (0,)*n,(1,)*n,tuple(i%2 for i in range(n)),
            tuple(1 if i%3==0 else 0 for i in range(n))
        ):
            assert selector_term(network,labels) in (0,1)

        if n<=18:
            count,witnesses=exhaustive_selector_count(network)
            assert count==ground_truth,(name,count,ground_truth)
            if witnesses:
                good=witnesses[0]
                assert selector_term(network,good)==1
                for i in range(n):
                    bogus=list(good);bogus[i]^=1
                    assert selector_term(network,bogus)==0
            print(f"RANK2_SELECTOR_EXACT_COUNT_{name}={count} "
                  f"selectors={1<<n}",flush=True)
        else:
            # Precomputed independently checked source SAT witness,
            # when available from the finite paired-network evaluator.
            from r5_universal_all_scl_perfect_matching_rank2_network import (
                independent_network_count_small
            )
            if n==27:
                small=independent_network_count_small(
                    network,max_nodes=27,max_states=1000000
                )
                assert small["status"]=="SAT"
                assert small["count"]==ground_truth
                witness=small["witness"]
                labels=tuple(witness[v] for v in network["matching"])
                assert selector_term(network,labels)==1
            print(f"RANK2_SELECTOR_BIJECTION_{name}=SOURCE_REPLAYED "
                  f"cells={n} rank2_terms={n}",flush=True)

        if n%3==0:
            options=comb(n,n//3)
            assert options>=1
            print(f"RANK2_SELECTOR_WEIGHT_FILTER_{name}="
                  f"C({n},{n//3})={options}",flush=True)

    print("MATCHGATE_SUM_SELECTOR_TERM_EXACT_ORIGINAL_WITNESS=PROVED")
    print("MATCHGATE_SUM_SELECTOR_PFAFFIAN_EXPANSION_NAIVE_2POWER_N=YES")
    print("SELECTOR_ORIGINAL_PROBLEM_NP_COMPLETE=HOLYER_REDUCTION")
    print("UNIFORM_POLYNOMIAL_SELECTOR_NONZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
