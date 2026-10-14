#!/usr/bin/env python3
"""R5: affine residual-class canonicalization is coNP-hard to recognize.

UNIVERSAL THEOREM, full native SCL input domain:
Take any legal square/cubic/linear positive Exact-One input A. Obtain
the polynomial-time GF(3) RREF x=x0+Bt, after treating linear
inconsistency as immediately UNSAT, and form the factored Boolean
indicator P_A(t)=prod_j(ell_j(t)-2)^2 on F3^d.

For every invertible affine map g:F3^d->F3^d:
    P_A identically zero iff P_A(g(t)) identically zero.
A test asking if P_A is affinely equivalent to the ZERO FUNCTION is
therefore EXACTLY the SCL-UNSAT test. Under a polynomial-size factored
input encoding, this test is coNP-COMPLETE:
  coNP membership: failure is witnessed by t with P_A(t)=1;
  coNP hardness: exact Holyer cubic 3-edge-colouring -> native SCL,
  including GF3-CONSISTENT SCL instances. See previous proof/experiment
  r5_universal_ei_closure_holyer_npcomplete_separation_rank.py.

Consequently a POLYNOMIAL upper bound on the NUMBER of affine
equivalence classes of semantic residual functions is INSUFFICIENT
for a universal polynomial solver, absent a UNIFORM polynomial
algorithm to recognize, compute and combine their canonical forms.
An exact polynomial zero recognizer for these indicators would itself
give P=NP; this code emphatically does NOT construct such recognizer.

FINITE CHECK ON HOLYER INSTANCES:
  K4:       n18, GF3 nullity4, 81 affine points, 6 Boolean covers
  K3,3:     n27, GF3 nullity8, 6561 affine points, 12 covers
  Petersen: n45, GF3 nullity10, 59049 affine points, 0 covers

For each, assign its first d-2 Gaussian free parameters and retain
a two-variable cofactor on F3^2. Exact affine group AGL(2,3) size=432
acts on all 9 table entries. The 3**(d-2) cofactors classify as:
  K4: 9 cofactors, 4 distinct truth tables, 2 AGL2 classes
  K3,3: 729 cofactors, 4 distinct tables, 2 AGL2 classes
  Petersen: 6561 cofactors, 1 distinct table, 1 AGL2 class (ZERO).

NO conclusion about efficient class discovery follows from these
small numbers. In fact, for a full UNSAT input ALL semantic cofactors
and ALL exact existential projections are identically zero:
ONE CLASS, however computationally hard it is to determine this.

ADDITIONAL independent local-vs-global control on Petersen:
Girth=5; every induced vertex set W with |W|<5 is a FOREST.
Requiring proper 3-edge-colouring at W (including ALL edge-colour
Exact-One constraints) yields exactly
    2**|W| * 3**(|E|-2*|W|)
partial proper edge-colour assignments. This is >0 for all 386
vertex sets of sizes 0..4, while imposing ALL 10 vertex constraints
gives 0 full proper edge-colourings. Independently count every
partial-colouring by explicit DFS respecting colours at vertices W;
do NOT assume the closed formula in the verifier.

This is a theorem about CO-NP-hard canonicalization, not a lower
bound on ALL arithmetic circuit sizes, affine class counts on SAT
instances, or P != NP. Universal polynomial SolveLinearCubicXSAT
remains NOT CONSTRUCTED; P vs NP remains OPEN.
"""
from collections import Counter
from itertools import combinations, product

from r5_universal_f3_boolean_exactification_connected_nullity_barrier import (
    gf3_rref_affine
)
from r5_universal_ei_closure_holyer_npcomplete_separation_rank import (
    K4, K33, PETERSEN, holyer_native_bridge,
    count_proper_three_edge_colours
)

DOMAIN=tuple(product(range(3),repeat=2))
INDEX={point:i for i,point in enumerate(DOMAIN)}


def affine_plane_transformations():
    perms=[]
    for a,b,c,d in product(range(3),repeat=4):
        if (a*d-b*c)%3==0:
            continue
        for p,q in DOMAIN:
            perm=tuple(INDEX[((a*x+b*y+p)%3,
                              (c*x+d*y+q)%3)] for x,y in DOMAIN)
            assert len(set(perm))==9
            perms.append(perm)
    assert len(perms)==432
    assert len(set(perms))==432
    return perms


def canonical_cofactor(mask,perms):
    answer=(1<<9)-1
    for perm in perms:
        converted=0
        for i,j in enumerate(perm):
            if mask>>i&1:
                converted|=1<<j
        answer=min(answer,converted)
    return answer


def exact_affine_truth_tables(A):
    rank,consistent,x0,basis=gf3_rref_affine(A)
    assert consistent
    d=len(basis)
    n=len(A)
    assert d>=2
    tables={}
    accepted=0
    accepted_params=[]
    # Pure-Python exhaustive finite test; not a proposed algorithm.
    for prefix in product(range(3),repeat=d-2):
        cofactor=0
        for k,suffix in enumerate(DOMAIN):
            coeffs=prefix+suffix
            good=True
            for j in range(n):
                value=(x0[j]+sum(coeffs[i]*basis[i][j]
                                 for i in range(d)))%3
                if value==2:
                    good=False
                    break
            if good:
                cofactor|=1<<k
                accepted+=1
                accepted_params.append(coeffs)
        tables[prefix]=cofactor
    return rank,d,accepted,tables,accepted_params


def verify_holyer_class_observation():
    perms=affine_plane_transformations()
    expected=(
        ("K4",4,K4,18,14,4,6,9,4,2),
        ("K33",6,K33,27,19,8,12,729,4,2),
        ("PETERSEN",10,PETERSEN,45,35,10,0,6561,1,1),
    )
    for name,vertices,E,n,rk,d,count,num,raw,agl in expected:
        A,edges,vars_=holyer_native_bridge(vertices,E)
        proper,_=count_proper_three_edge_colours(vertices,edges)
        rank,dim,boolean_points,tables,points=exact_affine_truth_tables(A)
        table_masks=Counter(tables.values())
        canon_masks=Counter(canonical_cofactor(x,perms)
                            for x in tables.values())
        assert (len(A),rank,dim,boolean_points,len(tables),
                len(table_masks),len(canon_masks))==(
                n,rk,d,count,num,raw,agl)
        assert proper==count
        expected_all_depth_raw={
            "K4":(2,4,4,3,1),
            "K33":(2,3,4,8,7,6,4,3,1),
            "PETERSEN":(1,)*11,
        }[name]
        raw_across_all_depths=[]
        for remaining in range(dim+1):
            prefixes={prefix:set() for prefix in product(
                range(3),repeat=dim-remaining)}
            for t in points:
                prefixes[t[:dim-remaining]].add(t[dim-remaining:])
            raw_across_all_depths.append(len(set(
                frozenset(v) for v in prefixes.values())))
        assert tuple(raw_across_all_depths)==expected_all_depth_raw
        if name=="PETERSEN":
            assert table_masks==Counter({0:3**(d-2)})
            assert canon_masks==Counter({0:3**(d-2)})
        print("EXACT_HOLYER_AFFINE_RESIDUAL_ORBIT_AUDIT",{
            "graph":name,"native_scl_n":n,
            "GF3_rank":rank,"GF3_nullity":dim,
            "exhausted_affine_points":3**dim,
            "proper_3edge_colours":proper,
            "Boolean_points":boolean_points,
            "all_prefix_cofactors":len(tables),
            "raw_distinct_two_variable_tables":len(table_masks),
            "AGL2_equivalence_classes":len(canon_masks),
            "nonzero_cofactors":sum(x!=0 for x in tables.values()),
            "raw_residual_class_counts_at_all_suffix_depths":raw_across_all_depths,
        },flush=True)


def count_colours_at_selected_vertices(E,chosen):
    """Direct DFS respecting selected vertex constraints, not formula."""
    W=set(chosen)
    touched=tuple(e for e in E if e[0] in W or e[1] in W)
    colours={v:0 for v in W}
    count=0
    def walk(k):
        nonlocal count
        if k==len(touched):
            count+=1
            return
        u,v=touched[k]
        for col in range(3):
            flag=1<<col
            if (u in W and colours[u]&flag) or (
                v in W and colours[v]&flag):
                continue
            if u in W:colours[u]^=flag
            if v in W:colours[v]^=flag
            walk(k+1)
            if u in W:colours[u]^=flag
            if v in W:colours[v]^=flag
    walk(0)
    return count*3**(len(E)-len(touched))


def verify_petersen_local_vs_global():
    assert len(PETERSEN)==15
    counts=Counter()
    for s in range(5):
        for W in combinations(range(10),s):
            internal=sum(u in W and v in W for u,v in PETERSEN)
            assert internal<=max(0,s-1)
            measured=count_colours_at_selected_vertices(PETERSEN,W)
            predicted=2**s * 3**(15-2*s)
            assert measured==predicted,(W,measured,predicted)
            counts[s]+=1
    assert counts==Counter({0:1,1:10,2:45,3:120,4:210})
    assert sum(counts.values())==386
    assert count_proper_three_edge_colours(10,PETERSEN)[0]==0
    print("PETERSEN_PROPER_COLOUR_LOCAL_VS_GLOBAL",{
        "partial_vertex_subsets_size_0_to_4":386,
        "all_local_colouring_counts_positive":True,
        "partial_subset_counts":dict(counts),
        "local_colours_4_vertices":16*3**7,
        "global_3edge_colourings":0
    },flush=True)


def main():
    verify_holyer_class_observation()
    verify_petersen_local_vs_global()
    print("THEOREM_AFFINE_EQUIVALENCE_TO_ZERO_coNP_COMPLETE_VIA_HOLYER")
    print("SMALL_AFFINE_RESIDUAL_ORBIT_COUNT_NOT_POLYTIME_CANONICALIZATION")
    print("UNIFORM_POLYNOMIAL_SolveLinearCubicXSAT_NOT_CONSTRUCTED")
    print("P_VS_NP_OPEN")


if __name__=="__main__":
    main()
