#!/usr/bin/env python3
"""R5 UNIVERSAL polynomial-closure gate, NP-complete source and exact rank witness.

TARGET: deterministic polynomial-time SolveLinearCubicXSAT on ALL legal
square + row/column cubic + linear positive Exact-One instances.

RESULTS:
(A) DIRECT POLYNOMIAL NP-COMPLETENESS BRIDGE, for a simple cubic
    graph G: variable x_(edge,colour), Exact-One clause for each edge
    and each vertex-colour. Incidence matrix is SQUARE with 3 ones
    in every row AND column, pairwise intersections <=1. Proper
    3-edge-colouring(G) iff this native SCL matrix has a Boolean cover.
    Hence a UNIVERSAL polynomial SCL solver would imply P=NP
    (Holyer, SIAM J Comput 10(4):718-720, 1981).
(B) EXACT closure (not complexity!): for any Boolean-valued
    GF3 polynomial-function Q, E_z Q = 1-prod_{a=0,1,2}(1-Q|z=a)
    represents existential elimination of z and remains Boolean.
    Iterating is sound and complete but no polynomial representation
    size, rewrite runtime, or zero-testing algorithm is proved.
(C) RIGOROUS REPRESENTATION LOWER BOUND for a SPECIFIC proposal,
    namely SUM OF SEPARABLE TERMS across a prescribed bipartition:
    k disjoint LEGAL square/cubic/linear GRID9 blocks admit a
    GF3 affine coordinate transformation (invertible) q=(u,v,z)
    on each block, after which existentially eliminating all z_i
    from the exact Boolean-point indicator produces the equality
    function Q_k(u,v)=[u=v] on F3^k x F3^k.
    Its evaluation matrix is I_(3**k), rank=3**k over ANY field.
    Therefore ANY representation
        Q_k(u,v) = sum_{r=1}^w f_r(u)g_r(v)
    requires w>=3**k=3**(n/9).
    This is an UNCONDITIONAL lower bound ONLY for the separated-term
    representation, not arithmetic circuit size or polynomial SAT:
        Q_k(u,v)=prod_i(1-(u_i-v_i)^2)
    has O(k) factored arithmetic circuits.
    The choice of split and GF3 coordinates is explicit. The
    instances are legal but DISCONNECTED; this disproves any
    unqualified "all SCL inputs have polynomial separable rank
    for every split" lemma, NOT all adaptive low-width methods.

Positive controls:
  K4 cubic: 6 proper 3-edge-colourings, native SCL SAT, n=18.
  K3,3 cubic: 12 proper 3-edge-colourings, native SCL SAT, n=27.
  Petersen cubic: 0 proper 3-edge-colourings, native SCL UNSAT, n=45.
  GRID9: 27 affine solutions and 3 Boolean covers; after change of
  affine variables q, three SAT points (u,v,z) are
      (0,0,0), (1,1,0), (2,2,1).
  Thus E_z P = 1-(u-v)^2 in the GF3 finite function ring.
  k=1,2,3 enumerate full projected truth table; k>=1 theorem
  follows by disjoint-product factorization.

NO universal polynomial SolveLinearCubicXSAT is constructed.
P versus NP remains OPEN.
"""
from collections import Counter
from itertools import combinations, product

from r5_universal_f3_boolean_exactification_connected_nullity_barrier import (
    GRID9, incidence, assert_legal, gf3_rref_affine
)

COLORS=(0,1,2)
K4=tuple(combinations(range(4),2))
K33=tuple((u,v) for u in range(3) for v in range(3,6))
PETERSEN=tuple(sorted(set(tuple(sorted(e)) for e in
    [(i,(i+1)%5) for i in range(5)]
    +[(i,i+5) for i in range(5)]
    +[(5,7),(7,9),(9,6),(6,8),(8,5)]
)))


def holyer_native_bridge(vertices, raw_edges):
    """Return EXACT legal native SCL incidence matrix and witnesses map."""
    E=tuple(sorted(tuple(sorted(e)) for e in raw_edges))
    assert len(E)==len(set(E))
    assert all(0<=u<v<vertices for u,v in E)
    assert all(sum(v in edge for edge in E)==3
               for v in range(vertices))
    assert 3*vertices==2*len(E)
    variables={(e,c):3*i+c for i,e in enumerate(E) for c in COLORS}
    rows=[tuple(variables[(e,c)] for c in COLORS) for e in E]
    for v in range(vertices):
        for c in COLORS:
            rows.append(tuple(variables[(e,c)] for e in E if v in e))
    A=incidence(rows)
    assert len(A)==len(variables)==3*len(E)
    assert_legal(A)
    # Return map, so an edge-colouring yields a native Boolean cover.
    return A,E,variables


def count_proper_three_edge_colours(vertices,E):
    """Exhaustively count proper edge colourings; tiny instances only."""
    incident=[0]*vertices
    assignment={}
    count=0
    witness=None

    def recurse():
        nonlocal count,witness
        if len(assignment)==len(E):
            count+=1
            if witness is None:witness=dict(assignment)
            return
        best=None;options=None
        for index,(u,v) in enumerate(E):
            if index in assignment:continue
            available=tuple(c for c in COLORS
                if not ((incident[u]|incident[v])&(1<<c)))
            if not available:return
            if options is None or len(available)<len(options):
                best=index;options=available
        u,v=E[best]
        for c in options:
            flag=1<<c
            assignment[best]=c
            incident[u] |= flag;incident[v] |= flag
            recurse()
            incident[u] ^= flag;incident[v] ^= flag
            del assignment[best]
    recurse()
    return count,witness


def verify_holyer_bridge():
    for name,vertices,edges,expected in (
        ("K4",4,K4,6),
        ("K33",6,K33,12),
        ("PETERSEN",10,PETERSEN,0),
    ):
        A,E,variables=holyer_native_bridge(vertices,edges)
        count,colouring=count_proper_three_edge_colours(vertices,E)
        assert count==expected,(name,count,expected)
        if colouring is not None:
            x=[0]*len(variables)
            for i,e in enumerate(E):
                x[variables[(e,colouring[i])]]=1
            assert all(sum(row[j]*x[j] for j in range(len(x)))==1
                       for row in A)
        print("EXACT_HOLYER_TO_NATIVE_CUBIC_LINEAR",{
            "graph":name,"cubic_graph_vertices":vertices,
            "native_square_matrix_n":len(A),
            "native_all_row_column_degrees":3,
            "native_pairwise_intersections_max":1,
            "proper_edge_colouring_count":count,
            "native_SAT":bool(count),
        },flush=True)


def Boolean_indicator(x):
    """1 iff every F3 affine coordinate is Boolean."""
    product_value=1
    for v in x:
        product_value=product_value*((v-2)**2)%3
    return product_value


def transformed_grid9_support():
    A=incidence(GRID9)
    assert_legal(A)
    rank,consistent,base,basis=gf3_rref_affine(A)
    assert rank==6 and consistent and len(basis)==3
    # The free-variable coordinate order in the exact RREF code.
    free=tuple(j for j in range(9) if
        j not in (0,1,2,3,4,6)) # GF3 pivots
    assert free==(5,7,8),free
    t_to_q={}
    support=set()
    for t in product(COLORS,repeat=3):
        x=[(base[j]+sum(t[i]*basis[i][j] for i in range(3)))%3
           for j in range(9)]
        # Invertible GF3 linear coordinate change:
        #     u=2*t0+t2, v=2*t1+t2, z=t0.
        u,v,z=(2*t[0]+t[2])%3,(2*t[1]+t[2])%3,t[0]
        q=(u,v,z)
        assert q not in t_to_q
        t_to_q[q]=t
        P=Boolean_indicator(x)
        if P:support.add(q)
        # 1-(u-v)^2 is not P itself before eliminating z!
        assert P in (0,1)
    assert len(t_to_q)==27
    assert support=={(0,0,0),(1,1,0),(2,2,1)},support
    for u,v in product(COLORS,repeat=2):
        eliminated=int(any((u,v,z) in support for z in COLORS))
        equality=(1-(u-v)**2)%3
        assert eliminated==equality,(u,v,eliminated,equality)
    print("GRID9_F3_BOOLEAN_AFFINE_PROJECTS_TO_TERNARY_EQUALITY",{
        "GF3_affine_dimension":3,
        "GF3_affine_solutions":27,
        "Boolean_covers":3,
        "invertible_change_of_parameters":True,
        "q_support":sorted(support),
        "eliminated_equality_table_rank":3,
    },flush=True)
    return support


def verify_tensor_barrier(support):
    for k in (1,2,3):
        n=3**k
        accepted=0
        for u in product(COLORS,repeat=k):
            for v in product(COLORS,repeat=k):
                exists=any(all((u[i],v[i],z[i]) in support
                               for i in range(k))
                           for z in product(COLORS,repeat=k))
                expected=(u==v)
                assert exists==expected,(k,u,v)
                accepted+=bool(exists)
        assert accepted==n
        # The UNIQUE reduced polynomial normal form over
        # F3[u_i,v_i]/(u_i^3-u_i,v_i^3-v_i) also has exponential
        # coefficient list length: each pair equality is
        #   1 + 2*u_i^2 + 2*u_i*v_i + 2*v_i^2.
        # Variables of distinct blocks are disjoint, hence the
        # 4**k products are all distinct monomials, with nonzero
        # coefficients; no modular reductions or cancellations occur.
        for a,b in product(COLORS,repeat=2):
            one_factor=(1+2*a*a+2*a*b+2*b*b)%3
            assert one_factor==int(a==b)
        normal_form_monomials=4**k
        print("EXACT_EXISTENTIAL_PROJECTION_KRON_IDENTITY",{
            "grid9_blocks":k,
            "native_SCL_variables":9*k,
            "eliminated_variables":k,
            "remaining_variables":2*k,
            "evaluated_matrix_dimension":n,
            "rank_over_F3":n,
            "minimum_separated_summands":n,
            "dense_finite_field_normal_form_terms":normal_form_monomials,
            "factored_circuit_size":f"O({k})",
        },flush=True)
    print("ALL_K_DENSE_NORMAL_FORM_COEFFICIENT_LOWER_BOUND", 
          "4^k=4^(native_n/9) after actual existential elimination")
    print("ALL_K_SEPARATOR_RANK_LOWER_BOUND",
          "3^k=3^(native_n/9) for this prescribed F3 split")
    print("DOES_NOT_PROVE_ARITHMETIC_CIRCUIT_LOWER_BOUND")
    print("DOES_NOT_PROVE_NO_POLYNOMIAL_SCL_SOLVER")
    print("UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT_NOT_CONSTRUCTED")
    print("P_VS_NP_OPEN")


if __name__=="__main__":
    verify_holyer_bridge()
    verify_tensor_barrier(transformed_grid9_support())
