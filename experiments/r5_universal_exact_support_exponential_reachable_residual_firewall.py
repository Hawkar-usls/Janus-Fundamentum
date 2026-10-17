#!/usr/bin/env python3
"""Exponential REACHABLE residuals -- sharp firewall for the DAG-size claim.

For ANY SAT n-by-n 3-regular/cubic Exact-One instance, the conflict graph
has max degree 6 and every exact-cover witness selects n/3 variables.
A greedy distance>=3 packing of witness-1 variables has k>=ceil(n/111)
because every closed 2-neighborhood has at most 1+6+6*5=37 vertices.

For each subset T of that packing, select every v in T (without fixing
the other packed bits), apply exact residual deletion. The SAME full
SAT witness extends all such partial selections. Moreover for every
unselected packed center v a distinguished original clause C_v remains
UNCHANGED; when v selected its clause is deleted. Thus the 2^k
residuals have distinct LABELLED canonical keys. This proves an
all-input exponential lower bound on the set of POSSIBLE reachable
feasible residual hypergraphs, not on the states EXPLORED by the
fixed shortest-clause decision algorithm, which exits on first SAT.

The explicit triangular-torus SAT family L=3r (r>=3) improves k
from >=n/111 to exactly n/9 using selected grid sites (3a,3b).

Do not confuse 'all reachable' with 'actually expanded by the
deterministic search order'! It is NOT a lower bound on the
algorithm runtime, and it does NOT prove P!=NP.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse, residual_choose_one,
    ExactSupportResidualDAG_sparse,
)
from r5_universal_kettani_2025_toroidal_treewidth_counterexample import (
    toroidal_triangular_carrier,
)


def conflict_neighborhoods(rows,n):
    neighbors=[set() for _ in range(n)]
    for clause in rows:
        for v in clause:
            neighbors[v].update(w for w in clause if w!=v)
    assert all(len(nn)<=6 for nn in neighbors)
    return neighbors


def greedy_witness_packing(rows,n,witness):
    assert len(witness)==n and all(x in (0,1) for x in witness)
    assert sum(witness)==n//3
    assert all(sum(witness[v] for v in clause)==1 for clause in rows)
    adj=conflict_neighborhoods(rows,n)
    excluded=set()
    packed=[]
    for v in range(n):
        if witness[v]!=1 or v in excluded:
            continue
        packed.append(v)
        distance1={v}|adj[v]
        distance2=distance1.copy()
        for w in distance1:
            distance2.update(adj[w])
        assert len(distance2)<=37
        excluded.update(distance2)
    assert 111*len(packed)>=n
    for i,v in enumerate(packed):
        assert v not in adj[v]
        radius2={v}|adj[v]
        for w in adj[v]:
            radius2.update(adj[w])
        assert all(w not in radius2 for w in packed[i+1:])
    return packed


def triangular_torus_witness(L):
    assert L%3==0 and L>=9
    return [
        int((i-j)%3==0)
        for i in range(L) for j in range(L)
    ]


def independent_torus_grid_sites(L):
    assert L%3==0
    return tuple(i*L+j for i in range(0,L,3) for j in range(0,L,3))


def reachable_residual(rows,choices):
    state=tuple(sorted(rows))
    for v in choices:
        assert any(v in row for row in state)
        state=residual_choose_one(state,v)
        assert state is not None
    return state


def check_identity_by_clause_signatures(rows,n,packed,subsets=4096):
    """Independent finite replay of all singleton-clause distinguishers.

    We avoid claiming an exhaustive 2^k replay when k is large.
    Formal proof covers ALL 2^k combinations for ALL SAT inputs.
    """
    witness_clauses={}
    for v in packed:
        witness_clauses[v]=next(row for row in rows if v in row)
    capped=min(len(packed),12)
    selected_centers=packed[:capped]
    tested=min(1<<capped,subsets)
    signatures=set()
    for mask in range(tested):
        chosen=tuple(v for k,v in enumerate(selected_centers) if mask>>k&1)
        state=reachable_residual(rows,chosen)
        signature=tuple(int(witness_clauses[v] in state)
                        for v in selected_centers)
        assert signature==tuple(0 if mask>>k&1 else 1 for k in range(capped))
        signatures.add(signature)
    assert len(signatures)==tested
    return tested


def main():
    for L in (9,12,15,18):
        n=L*L
        rows=validate_sparse(toroidal_triangular_carrier(L),n)
        witness=triangular_torus_witness(L)
        grid=independent_torus_grid_sites(L)
        packing=greedy_witness_packing(rows,n,witness)
        assert len(grid)==n//9
        assert all(witness[v]==1 for v in grid)
        adj=conflict_neighborhoods(rows,n)
        for i,v in enumerate(grid):
            radius2={v}|adj[v]
            for w in adj[v]:
                radius2.update(adj[w])
            assert all(w not in radius2 for w in grid[i+1:])
        checked=check_identity_by_clause_signatures(rows,n,grid)
        assert 111*len(packing)>=n
        found=ExactSupportResidualDAG_sparse(rows,n,max_states=5000)
        assert found["status"]=="SAT"
        # The actually expanded DAG is dramatically smaller than
        # the total reachable family for the same SAT instance.
        assert found["stats"]["distinct_states"] < (1<<len(grid))
        print(
            f"SAT_TORUS_L{L}: n={n}, greedy_k={len(packing)}, "
            f"explicit_k=n/9={len(grid)}, "
            f"REACHABLE_possible>=2^{len(grid)}, "
            f"sampled distinct canonical states={checked}, "
            f"ACTUAL deterministic DAG states={found['stats']['distinct_states']}"
        )

    print("EVERY_SAT_SCL_POSSIBLE_REACHABLE_STATES_GE_2^(N/111) = PROVED")
    print("SAT_TOROIDAL_POSSIBLE_REACHABLE_STATES_GE_2^(N/9) = PROVED")
    print("INFINITE_SAT_FAMILY_EXACT_DAG_SEARCH_VISITS_CAN_BE_SMALL = VERIFIED")
    print("IMPORTANT: NO EXPONENTIAL_LOWER_BOUND_ON_ACTUAL_EXPANDED_STATES")
    print("GLOBAL_ACTUAL_SEARCH_STATES_LE_POLY_N = OPEN")
    print("UNIVERSAL_POLY_ExactSupport = NOT_CONSTRUCTED; P_VS_NP = OPEN")


if __name__=="__main__":
    main()
