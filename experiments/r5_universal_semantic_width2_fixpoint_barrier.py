#!/usr/bin/env python3
"""Exact semantic width-2 closure barrier on connected legal SCL K3,3.

Even an IDEAL oracle supplying EVERY true unary/binary forbidden
assignment cannot, via unit propagation alone, derive a single
forced variable in a symmetric SAT SCL instance whose model set
contains both values of each variable.

This is an explicit theorem against the proposed "knowledge potential
falls, hence a final verdict follows" shortcut, NOT a lower bound on
unrestricted algorithms, nor a proof that the exact JANUS PC3 closure
itself is universally incomplete. An additional SAT witness-constructor
is indispensable to turn fixpoint knowledge into SAT.

Independent complete finite source enumeration: edge coloring of K3,3
(3^9 assignments, 12 proper 3-edge colorings). Source-to-SCL bijection
is checked by enumerating every chosen (edge,color) literal.
"""
from __future__ import annotations
from itertools import product,combinations
from collections import Counter

from r5_universal_cubic_edgecolor_direct_scl_bridge import K33,make_scl
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_shared_proof_state import CertifiedSharedState


def all_source_colours(edges):
    seen=sorted({v for edge in edges for v in edge})
    solutions=[]
    for colors in product(range(3),repeat=len(edges)):
        if all(len({colors[i] for i,e in enumerate(edges) if v in e})==3
               for v in seen):
            solutions.append(colors)
    return solutions


def semantic_pair_projection(models,n):
    assert models
    possible0=[{w[i] for w in models} for i in range(n)]
    nogoods=[]
    for i in range(n):
        for b in (0,1):
            if b not in possible0[i]:
                nogoods.append(((i,b),))
    for i,j in combinations(range(n),2):
        pairs={(w[i],w[j]) for w in models}
        for b,c in product((0,1),repeat=2):
            if (b,c) not in pairs:
                nogoods.append(((i,b),(j,c)))
    return nogoods,possible0


def proof():
    rows,n,edges,idx=make_scl(K33())
    rows=validate_sparse(rows,n)
    colors=all_source_colours(edges)
    assert n==27 and len(edges)==9 and len(colors)==12
    models=[]
    for assignment in colors:
        witness=[0]*n
        for i,e in enumerate(edges):
            witness[idx[(e,assignment[i])]]=1
        assert sum(witness)==9
        assert all(sum(witness[j] for j in row)==1 for row in rows)
        models.append(tuple(witness))
    assert len(models)==len(set(models))==12
    # Prove no unary consequence without even needing enumeration:
    # color permutation S3 sends any given edge-color variable from
    # 1 to 0 and vice versa, preserving every original clause.
    nogoods,projections=semantic_pair_projection(models,n)
    assert all(s=={0,1} for s in projections)
    assert all(len(g)==2 for g in nogoods)
    oracle_count=len(nogoods)
    assert oracle_count>0
    st=CertifiedSharedState(rows,n)
    status,pins,trace=st.propagate()
    assert status=='FIXPOINT' and pins=={} and trace==[]
    # Complete true length-2 nogoods are inert without a previously
    # fixed literal; no no-good becomes unit and exact-one rows
    # have no singleton forcing rule. No SAT model can be extracted
    # by such closure alone (even though 12 witnesses exist).
    assert all(len(ng)==2 for ng in nogoods)
    print(f'EXACT_SEMANTIC_PAIR_PROJECTION_K33_SCL_N={n} '
          f'colorings={len(colors)} pair_nogoods={oracle_count} '
          f'globally_forced_singletons=0 unit_propagation_pins=0',
          flush=True)
    print('WIDTH2_SEMANTIC_ORACLE_PLUS_UNIT_PROPAGATION_NOT_DECISION = PROVED_FINITE')
    print('MONOTONE_KNOWLEDGE_POTENTIAL_IS_NOT_COMPLETENESS = PROVED')
    print('GLOBAL_SCL_POLYNOMIAL_COVERAGE = OPEN')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    proof()
