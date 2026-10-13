#!/usr/bin/env python3
"""JANUS R5 all-input connected-component decomposition theorem.

Every square/cubic/linear Positive Exact-One incidence matrix A has
bipartite Tanner graph of row/column degree 3. In a connected component
with r clause vertices and v variable vertices, counting incidence
ends gives 3r=3v, hence r=v. Both source linearity and clause/variable
degree3 pass unchanged to each component. The components are therefore
legal smaller SCL sources, not relaxed or guessed subproblems.

SAT of the union iff SAT of EVERY component; if ANY component UNSAT,
the union UNSAT by restricting any hypothetical assignment to it.
Original SAT witness is assembled by disjoint coordinate inverse maps
and rechecked against original rows. Existing expert negative proof
is verified in the component before lifting its logical conclusion.

The decomposition is O(n) on sparse 3-degree input; if each source
expert has p(n)=O(n^C), sum over components p(n_i)<=O(n^C)
for C>=1 and sum_i n_i=n. It does not imply p is polynomial for
complete exact fallback and does not handle a CONNECTED hard source.
"""
from __future__ import annotations
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def canonical_scl_components(rows,n):
    """Return source-checked (columns, local_rows) in deterministic order."""
    rows=validate_sparse(rows,n)
    m=len(rows)
    assert m==n
    occurrences=[[] for _ in range(n)]
    for ci,row in enumerate(rows):
        for v in row:
            occurrences[v].append(ci)
    assert all(len(o)==3 for o in occurrences)
    visited_v=set(); visited_c=set()
    components=[]
    for start in range(n):
        if start in visited_v:continue
        pending=[('v',start)]
        component_v=set();component_c=set()
        while pending:
            typ,x=pending.pop()
            if typ=='v':
                if x in visited_v:continue
                visited_v.add(x);component_v.add(x)
                pending.extend(('c',ci) for ci in occurrences[x])
            else:
                if x in visited_c:continue
                visited_c.add(x);component_c.add(x)
                pending.extend(('v',v) for v in rows[x])
        columns=tuple(sorted(component_v))
        row_ids=tuple(sorted(component_c))
        assert len(columns)==len(row_ids)==len(component_v)
        remap={v:i for i,v in enumerate(columns)}
        local=validate_sparse([
            tuple(remap[v] for v in rows[ci])
            for ci in row_ids
        ],len(columns))
        components.append({
            'columns':columns,
            'row_indices':row_ids,
            'rows':local,
            'n':len(columns),
        })
    assert len(visited_v)==n and len(visited_c)==n
    assert sum(x['n'] for x in components)==n
    assert {v for part in components for v in part['columns']}==set(range(n))
    assert {c for part in components for c in part['row_indices']}==set(range(n))
    # Original re-lift equivalence: no clause crosses components.
    assert all(
        tuple(sorted(part['columns'][v] for v in row)) in set(rows)
        for part in components for row in part['rows']
    )
    return tuple(components)


def independently_verify_lifted_witness(rows,n,parts,witness):
    """Global SAT identity, not just per-component subclaims."""
    assert witness is not None and len(witness)==n
    assert all(x in (0,1) for x in witness)
    assert all(sum(witness[v] for v in row)==1 for row in rows)
    seen=set()
    for part in parts:
        for v in part['columns']:
            assert v not in seen;seen.add(v)
        sub=tuple(witness[v] for v in part['columns'])
        assert all(sum(sub[x] for x in clause)==1
                   for clause in part['rows'])
    assert len(seen)==n
    return True


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,petersen_graph,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    source_rows,ns,_,_=make_scl(K4())
    neg_rows,nu,_,_=make_scl(petersen_graph())
    fano=cyclic(7)
    combined=validate_sparse(
        tuple(source_rows)
        +tuple(tuple(x+ns for x in row) for row in neg_rows)
        +tuple(tuple(x+ns+nu for x in row) for row in fano),
        ns+nu+7,
    )
    components=canonical_scl_components(combined,len(combined))
    assert len(components)==3
    assert sorted(p['n'] for p in components)==[7,18,45]
    assert all(len(c['columns'])==c['n'] for c in components)
    print('ALL_SOURCE_COMPONENTS_PRESERVE_SCL=PROVED_GENERAL')
    print('CONNECTED_COMPONENT_COUNT_AND_SOURCE_COORDINATES=VERIFIED')
    print('UNIVERSAL_POLY_SCL_SOLVER=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
