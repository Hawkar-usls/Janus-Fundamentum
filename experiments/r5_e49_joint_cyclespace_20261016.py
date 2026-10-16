#!/usr/bin/env python3
"""JANUS E4.9 JOINT_CYCLESPACE_GEOMETRY: finite exact signed 2-lift control.

Standalone stdlib verifier. Reads immutable E4.8 legal connected
UNSAT SCL45 source, with two distinct feasible z and explicit sign.
Derives each G_z by source incidence, fundamental cycle voltage
conditions, joint rank kappa, gauge dimension and quotient dimension.
No reliance on JANUS generator, linear algebra code or prior certificate.

All-n theorem: for a fixed z of even weight, G_z simple cubic,
and its |z|/2+c fundamental cycles impose INDEPENDENT linear GF2
conditions on the original incidence voltage bits, since each
G_z cycle has a unique incidence-edge support. Gauge flips
p_row+q_column annihilate every incidence cycle condition.
For multiple z, their combined kappa is rank of the UNION of
the incidence cycle constraints, not sum of individual ranks.

This script computes explicit 27 independent non-gauge voltage
generators preserving BOTH z in this specific C45 and independently
checks their lifted exact-one witnesses by integer row sums.
It DOES NOT enumerate 2^27 possibilities and proves no polynomial
algorithm for arbitrary SCL.
"""
import argparse,hashlib,json
from collections import deque
from pathlib import Path


def gaussian(rows,width):
    v=list(rows);p=[];rank=0
    for j in range(width):
        i=next((i for i in range(rank,len(v)) if (v[i]>>j)&1),None)
        if i is None:continue
        v[rank],v[i]=v[i],v[rank]
        for k in range(len(v)):
            if k!=rank and ((v[k]>>j)&1):v[k]^=v[rank]
        p.append(j);rank+=1
    return v[:rank],p


def gf2rank(rows,width):
    return len(gaussian(rows,width)[1])


def nullspace(rows,width):
    rr,piv=gaussian(rows,width)
    basis=[]
    for j in range(width):
        if j in piv:continue
        v=1<<j
        for i,p in enumerate(piv):
            if (rr[i]>>j)&1:v|=1<<p
        assert all((v&r).bit_count()%2==0 for r in rows)
        basis.append(v)
    return basis


def independent_generators(existing,candidates,width):
    # Low-pivot rank-evolving selection, no exponential enumeration.
    piv={}
    def append(v):
        while v:
            j=v.bit_length()-1
            if j in piv:v^=piv[j]
            else:
                piv[j]=v
                return True
        return False
    for v in existing:
        append(v)
    count=len(piv)
    chosen=[]
    for v in candidates:
        if append(v):chosen.append(v)
    return chosen,count,len(piv)


def cycle_equations(rows,z,lookup):
    n=len(rows)
    nodes=[j for j in range(n) if (z>>j)&1]
    graph={j:[] for j in nodes}
    links=[]
    for i,row in enumerate(rows):
        both=[j for j in row if (z>>j)&1]
        assert len(both) in (0,2)
        if not both:continue
        j,k=both
        mask=(1<<lookup[(i,j)])|(1<<lookup[(i,k)])
        edge=len(links);links.append((j,k,i,mask))
        graph[j].append((k,edge));graph[k].append((j,edge))
    assert all(len(graph[j])==3 for j in nodes)
    visited={};parent_edge={};depth={};tree=set()
    cc=0
    for root in nodes:
        if root in visited:continue
        cc+=1
        visited[root]=None
        depth[root]=0
        queue=deque([root])
        while queue:
            v=queue.popleft()
            for other,e in graph[v]:
                if other in visited:continue
                visited[other]=v
                parent_edge[other]=e
                depth[other]=depth[v]+1
                tree.add(e)
                queue.append(other)
    def path(u,v):
        parts=[]
        while depth[u]>depth[v]:
            parts.append(parent_edge[u]);u=visited[u]
        while depth[v]>depth[u]:
            parts.append(parent_edge[v]);v=visited[v]
        while u!=v:
            parts.extend((parent_edge[u],parent_edge[v]))
            u=visited[u];v=visited[v]
        return parts
    equations=[]
    for e,(j,k,i,mask) in enumerate(links):
        if e in tree:continue
        trail=[e]+path(j,k)
        q=0
        for a in trail:q^=links[a][3]
        # For each fundamental cycle the RHS is parity length,
        # from row equation lambda_j+lambda_k=1+sigma_j+sigma_k.
        equations.append((q,len(trail)%2,tuple(trail)))
    assert len(equations)==len(links)-len(nodes)+cc
    assert len(equations)==len(nodes)//2+cc
    assert gf2rank([e[0] for e in equations],len(lookup))==len(equations)
    return {"z":z,"nodes":nodes,"links":links,"components":cc,
            "equations":equations,"beta":len(equations)}


def witness_for_z(rows,z,sign,lookup):
    # For frozen C45, the full exact residual audit proves the
    # only y2 columns for both nonzero z are 1,16.
    n=len(rows)
    double={1,16}
    assert all(((z>>j)&1)==0 for j in double)
    row_graph={j:[] for j in range(n) if (z>>j)&1}
    for i,row in enumerate(rows):
        both=[j for j in row if (z>>j)&1]
        if both:
            assert len(both)==2
            other=next(j for j in row if j not in both)
            assert other not in double
            j,k=both
            t=1 ^ ((sign>>lookup[(i,j)])&1) ^ ((sign>>lookup[(i,k)])&1)
            row_graph[j].append((k,t))
            row_graph[k].append((j,t))
        else:
            assert sum(j in double for j in row)==1
    labels={}
    for root in row_graph:
        if root in labels:continue
        labels[root]=0
        queue=[root]
        while queue:
            j=queue.pop()
            for k,par in row_graph[j]:
                rhs=labels[j]^par
                if k in labels:
                    if labels[k]!=rhs:return None
                else:
                    labels[k]=rhs;queue.append(k)
    x=0
    for j in double:x|=(1<<j)|(1<<(n+j))
    for j,label in labels.items():x|=1<<(j+n*label)
    for layer in (0,1):
        for i,row in enumerate(rows):
            total=sum((x>>(j+n*(layer^((sign>>lookup[(i,j)])&1))))&1
                      for j in row)
            assert total==1
    assert (x&((1<<n)-1))^(x>>n)==z
    return x


def run(path):
    F=json.loads(Path(path).read_text())
    rows=[tuple(row) for row in F["base_45_rows"]]
    n=len(rows)
    assert n==45
    E=[(i,j) for i,row in enumerate(rows) for j in row]
    assert len(E)==135
    lookup={edge:k for k,edge in enumerate(E)}
    sigma=int(F["sat_lift_voltage_bits_decimal"])
    zlist=[int(z) for z in F["distinct_z_decimal"]]
    assert len(zlist)==2 and zlist[0]!=zlist[1]
    cycle=[cycle_equations(rows,z,lookup) for z in zlist]
    assert [c["beta"] for c in cycle]==[14,14]
    all_eq=[q for C in cycle for q,rhs,trail in C["equations"]]
    all_rhs=[rhs for C in cycle for q,rhs,trail in C["equations"]]
    assert all(((q&sigma).bit_count()&1)==rhs
               for q,rhs in zip(all_eq,all_rhs))
    kappa=gf2rank(all_eq,len(E))
    assert kappa==19
    separate_sum=sum(c["beta"] for c in cycle)
    intersection=separate_sum-kappa
    assert intersection==9
    # All 45 row swaps +45 column swaps produce a gauge
    # code of dimension 90−1=89. Each leaves cycle parities
    # unchanged. The source is connected.
    gauge=[]
    for i in range(n):
        gauge.append(sum(1<<k for k,(r,v) in enumerate(E) if r==i))
    for j in range(n):
        gauge.append(sum(1<<k for k,(r,v) in enumerate(E) if v==j))
    assert gf2rank(gauge,len(E))==89
    assert all(((q&g).bit_count()&1)==0
               for q in all_eq for g in gauge)
    # Full voltage solution space is sigma + ker Q, so its
    # dimension 135-19=116. Take quotient by gauge dim89.
    basis=nullspace(all_eq,len(E))
    assert len(basis)==len(E)-kappa==116
    quotient,rg,rfull=independent_generators(gauge,basis,len(E))
    assert rg==89 and rfull==116 and len(quotient)==27
    # Verify every independent quotient generator is legal,
    # and preserves the exact two-z lifted SAT witnesses.
    base_witnesses=[witness_for_z(rows,z,sigma,lookup) for z in zlist]
    assert all(w is not None for w in base_witnesses)
    for delta in quotient:
        assert all(((q&delta).bit_count()&1)==0 for q in all_eq)
        for z in zlist:
            assert witness_for_z(rows,z,sigma^delta,lookup) is not None
    # Each individual G_z cycle parity equation is independent
    # even modulo gauge, since all q annihilate gauge and source
    # cycle-space dimension is 46.
    source_cycle_dim=len(E)-(2*n-1)
    assert source_cycle_dim==46
    return {
        "gate":"E4_9_JOINT_CYCLESPACE_GEOMETRY",
        "frozen_source_sha256":F["base_canonical_sha256"],
        "vertex_count":2*n,"incidence_edges":len(E),
        "z_values":[str(z) for z in zlist],
        "G_z":[{"z":str(C["z"]),"vertices":len(C["nodes"]),
                "edges":len(C["links"]),"components":C["components"],
                "cycle_rank":C["beta"],
                "fundamental_cycle_constraints":[{
                    "incidence_mask_decimal":str(q),
                    "rhs":rhs,"G_z_trail":list(trail)}
                   for q,rhs,trail in C["equations"]]}
              for C in cycle],
        "single_direction_cycle_ranks":[14,14],
        "joint_cycle_rank_kappa":kappa,
        "joint_constraint_overlap_dimension":intersection,
        "source_cycle_space_dimension":source_cycle_dim,
        "gauge_rank":rg,
        "total_compatible_voltage_affine_dimension":len(E)-kappa,
        "compatible_switching_quotient_dim":len(quotient),
        "compatible_switching_class_count_decimal":str(1<<len(quotient)),
        "non_gauge_compatible_voltage_generators_decimal":[str(v) for v in quotient],
        "gauge_invariance_checked":True,
        "all_27_basis_generators_preserve_both_ternary_SAT_lifts":True,
        "previous_frozen_voltage_in_affine_family":True,
        "exact_2lift_SAT_witnesses_for_both_z":[str(w) for w in base_witnesses],
        "global_polynomial_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.fixture),sort_keys=True,indent=2))
