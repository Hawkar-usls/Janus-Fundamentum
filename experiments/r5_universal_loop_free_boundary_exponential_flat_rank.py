#!/usr/bin/env python3
"""R5 ALL-LEGAL-SCL exponential exact boundary rank of isolated T4 cells.

Universal theorem, for EVERY original legal square-cubic-linear
Positive Exact-One source on n variables:
  1. Source-authenticated 3-regular Tanner Hall matching converts
     original F into an n-cell 4-regular quartic T4 network Q.
  2. Q has max 4 DISTINCT neighbours per vertex (possibly parallel
     edges). A greedy independent set I has cardinality >=ceil(n/5).
  3. Select the induced disconnected collection of T4 cells indexed
     by I, leave ALL 4|I| incident quotient wires OPEN. There are
     NO internal wires among these cells, so its exact boundary
     signature is a tensor product of |I| copies of T4.
  4. Split each cell's four ports as left (0,2), right (1,3).
     Single T4 flattening has rank 3 and a unit 3x3 minor.
     Flattened whole signature is a Kronecker product of the
     local 4x4 flattenings, hence has EXACT rank 3**|I|.

This proves a worst-case EXPONENTIAL lower bound on the rank of
a FLAT, EXPLICIT LINEAR INTERFACE FACTORIZATION preserving ALL
boundary assignments of these source-grounded partial networks.
Any decomposition M=U V through a d-dimensional vector space
needs d>=3**ceil(n/5). Over Q, R or C, and also for a
nonnegative rank factorization, same lower bound applies.

The original entire tensor network itself has size O(n) as an
IMPLICIT expression. This theorem is NOT a complexity lower
bound on arbitrary succinct implicit representations, Boolean
SAT decision, Pfaffian sums or arbitrary polynomial global
contractions; arbitrary context can restrict exposed boundary
assignments. It excludes ONLY explicit polynomial-dimensional
flat linear boundary channels with free boundary values.

Because the exact generalized-loop M4 tensor is a local
invertible H^tensor4 transform of T4 and rescaled by 1/3,
its identical source-grounded isolated-cell boundary matrix
has the SAME rank 3**|I|. Thus the rank obstruction applies
to both original and signed-loop FLAT boundary signatures.
"""
from __future__ import annotations
from itertools import product
from fractions import Fraction

from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,verify_paired_quartic_network
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_grouped_two_node_matchgate_flatten_rank_nogo import (
    fused_cell,rank_exact
)
from r5_universal_rank2_exact_bethe_loop_correction import local_loop_moments


def source_quotient_adjacency(Q):
    n=Q["source_n"]
    nbr=[set() for _ in range(n)]
    for endpoints in Q["endpoints"]:
        assert len(endpoints)==2
        (u,pu),(v,pv)=endpoints
        assert 0<=u<n and 0<=v<n and u!=v
        nbr[u].add(v)
        nbr[v].add(u)
    assert all(len(s)<=4 for s in nbr)
    assert sum(len(s) for s in nbr)<=4*n
    return tuple(frozenset(s) for s in nbr)


def source_greedy_independent_cells(Q):
    nbr=source_quotient_adjacency(Q)
    allowed=set(range(len(nbr)))
    chosen=[]
    while allowed:
        v=min(allowed)
        chosen.append(v)
        allowed.difference_update({v})
        allowed.difference_update(nbr[v])
    assert len(chosen)*5>=len(nbr)
    assert all(b not in nbr[a] for i,a in enumerate(chosen)
               for b in chosen[i+1:])
    assert len(set(chosen))==len(chosen)
    return tuple(chosen)


def local_flatten(tensor):
    """Rows=port bits 0,2; columns=port bits 1,3."""
    return tuple(tuple(
        Fraction(tensor[(a,c,b,d)])
        for c,d in product((0,1),repeat=2)
    ) for a,b in product((0,1),repeat=2))


def determinant_3(A):
    assert len(A)==3 and all(len(row)==3 for row in A)
    return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])
           -A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])
           +A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))


def exact_single_cell_rank_and_minor():
    T=local_flatten(fused_cell())
    assert rank_exact(T)==3
    # Single-cell sources in binary order (port0,port2) vs
    # (port1,port3) restrict to indices 0,1,2 in each axis.
    minor=tuple(tuple(T[i][j] for j in range(3))
                for i in range(3))
    assert minor==((0,0,1),(0,1,0),(1,0,0))
    assert determinant_3(minor)==-1

    # Generalized-loop M4 is an invertible local basis image
    # of the same original T4, see prior exact backtransform.
    M=tuple(local_loop_moments())
    loop_t={tuple((mask>>i)&1 for i in range(4)):Fraction(M[mask])
            for mask in range(16)}
    loop_mat=local_flatten(loop_t)
    assert rank_exact(loop_mat)==3
    return T,loop_mat


def kron(A,B):
    return tuple(tuple(A[i][j]*B[p][q]
                       for j in range(len(A[0]))
                       for q in range(len(B[0])))
                 for i in range(len(A)) for p in range(len(B)))


def finite_rank_audit(max_k=3):
    T,M=exact_single_cell_rank_and_minor()
    for sig,name in ((T,"T4"),(M,"LOOP_M4")):
        tensor=((Fraction(1),),)
        for k in range(1,max_k+1):
            tensor=kron(tensor,sig)
            observed=rank_exact(tensor)
            assert observed==3**k,(name,k,observed)
            print(f"EXACT_FREE_BOUNDARY_RANK_{name}_K{k}="
                  f"{observed} OF {4**k} ROWS",flush=True)


def replay_source_independent_boundary(rows,n,name):
    source=validate_sparse(rows,n)
    Q=paired_quartic_network(source,n)
    assert verify_paired_quartic_network(source,n,Q)
    I=source_greedy_independent_cells(Q)
    edges={v:[] for v in I}
    for eid,(a,b) in enumerate(Q["endpoints"]):
        for v,port in (a,b):
            if v in edges:
                edges[v].append((eid,port))
    assert all(len(z)==4 and set(p for eid,p in z)==set(range(4))
               for z in edges.values())
    assert all(not (
        e[0][0] in edges and e[1][0] in edges
    ) for e in Q["endpoints"])
    target=(n+4)//5
    assert len(I)>=target
    # We need no exponential-sized arrays to CERTIFY the exact
    # rank of this huge tensor. Rank of a tensor product equals
    # product of ranks, and a unit 3x3 local minor is explicit.
    rank=3**len(I)
    assert rank>=3**target
    print(f"ORIGINAL_{name}_N{n}_INDEPENDENT_T4_CELLS="
          f"{len(I)} BOUNDARY_RANK_3POWERK={rank} "
          f"BOUNDARY_WIRES={4*len(I)}",flush=True)
    return len(I)


def source_free_boundary_matrix(Q,chosen):
    """Independent actual SOURCE-WIRE enumeration of selected cells.

    Open every quotient incidence of chosen pairwise-nonadjacent
    source cells. The left tuple contains local ports 0 and 2,
    right tuple contains local ports 1 and 3. For k<=3 this
    explicitly enumerates all 4^k x 4^k boundary entries.
    """
    assert len(chosen)<=3
    selected=set(chosen)
    assert all(not (
        edge[0][0] in selected and edge[1][0] in selected
    ) for edge in Q["endpoints"])
    out=[]
    for left in product((0,1),repeat=2*len(chosen)):
        line=[]
        for right in product((0,1),repeat=2*len(chosen)):
            edge_values={}
            accepted=1
            for k,cell in enumerate(chosen):
                ports=Q["cells"][cell]
                assert len(ports)==4
                bits=(left[2*k],right[2*k],
                      left[2*k+1],right[2*k+1])
                for edge,value in zip(ports,bits):
                    if edge in edge_values:
                        assert edge_values[edge]==value
                    edge_values[edge]=value
                accepted*=int(bits in (
                    (1,0,0,0),(0,1,0,0),(0,0,1,1)
                ))
            assert len(edge_values)==4*len(chosen)
            line.append(Fraction(accepted))
        out.append(tuple(line))
    return tuple(out)


def source_rank_sat_unsat_same_size_controls():
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    import itertools
    count_profile={}
    for name,p,q in (("SAT",P_SAT,Q_SAT),("UNSAT",P_UNSAT,Q_UNSAT)):
        A=build_A(p,q)
        rows=validate_sparse(
            [tuple(j for j,v in enumerate(row) if v)
             for row in A],len(A)
        )
        Q=paired_quartic_network(rows,len(rows))
        selected=source_greedy_independent_cells(Q)
        assert len(selected)>=3
        actual=source_free_boundary_matrix(Q,selected[:3])
        assert rank_exact(actual)==27
        counts=sum(all(sum((mask>>v)&1 for v in row)==1
                       for row in rows) for mask in range(1<<len(rows)))
        count_profile[name]=counts
        print(f"REAL_SOURCE_E61_{name}12_OPEN_THREE_CELLS_RANK=27 "
              f"ORIGINAL_SOURCE_COUNT={counts}",flush=True)
    assert count_profile=={"SAT":1,"UNSAT":0}
    print("SAME_SIZE_SAT_UNSAT_IDENTICAL_LOCAL_FREE_BOUNDARY_RANK=PASS",
          flush=True)


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph
    )
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    finite_rank_audit(3)
    source_rank_sat_unsat_same_size_controls()
    cases=[
        ("FANO7",cyclic(7),7),
        ("K4_SCL18",*make_scl(K4())[:2]),
        ("K33_SCL27",*make_scl(K33())[:2]),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
        ("FLOWER_J5_SCL90",*make_scl(flower(5))[:2])
    ]
    for name,p,q in (("E61_SAT12",P_SAT,Q_SAT),
                     ("E61_UNSAT12",P_UNSAT,Q_UNSAT)):
        A=build_A(p,q)
        rows=validate_sparse(
            [tuple(j for j,v in enumerate(row) if v)
             for row in A],len(A)
        )
        cases.append((name,rows,len(A)))
    for name,rows,n in cases:
        replay_source_independent_boundary(rows,n,name)

    # Larger connected source proves the certificate can be
    # represented and audited without constructing a 4^k tensor.
    big,n,_,_=make_scl(flower(63))
    assert n==1134
    replay_source_independent_boundary(big,n,"FLOWER_J63_SCL1134")

    print("ALL_SCL_FREE_BOUNDARY_RANK_GE_3_POWER_CEIL_N_OVER5=PROVED")
    print("ALL_SCL_POLYNOMIAL_DIMENSION_EXPLICIT_LINEAR_BOUNDARY_FACTOR=REFUTED")
    print("IMPLICIT_POLYNOMIAL_TENSOR_NETWORK_REMAINS_POSSIBLE")
    print("GENERAL_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
