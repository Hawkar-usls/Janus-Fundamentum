#!/usr/bin/env python3
"""E4.9 SOURCE_STRUCTURAL_PROFILE — exact finite proof for frozen C45.

Source incidence Γ: 90 nodes, 135 edges, 3-regular bipartite.
Complete 3-edge-cut enumeration is reduced to:
 for every pair of removed edges, find EVERY remaining bridge.
Every 3-edge cut must contain a pair whose deletion leaves a
bridge as its third edge, so this is EXHAUSTIVE for all binom(135,3)
triples (400995) without making 400995 full graph copies.
All found 3-cuts are tested against 90 vertex stars.
A 4-edge cut from frozen old A36/B9 partition is independently
verified to split the graph into 72 and18 nodes, BOTH containing
cycles. Thus cyclic edge-connectivity exactly4.
Girth is exact BFS through all source vertices.

NOTE: a finite explicit cut gives a rigorous UPPER bound on Phi_alpha,
not its global optimum. Balanced vertex cut tested only at k<=2 here;
existing user-supplied stronger k<=4 is NOT represented as CI proved.
"""
import argparse,json
from collections import deque,Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path


def graph_from_rows(rows):
    n=len(rows)
    adj=[[] for _ in range(2*n)]
    E=[]
    for i,row in enumerate(rows):
        for j in row:
            eid=len(E);E.append((i,n+j))
            adj[i].append((n+j,eid))
            adj[n+j].append((i,eid))
    return adj,E


def comp_sizes(adj,removed_edges=frozenset(),removed_vertices=frozenset()):
    rem=set(range(len(adj)))-set(removed_vertices)
    sizes=[]
    while rem:
        start=next(iter(rem));rem.remove(start)
        todo=[start];size=0
        while todo:
            v=todo.pop();size+=1
            for nxt,edge in adj[v]:
                if edge in removed_edges or nxt in removed_vertices:continue
                if nxt in rem:
                    rem.remove(nxt);todo.append(nxt)
        sizes.append(size)
    return sorted(sizes)


def bridges_after_deleting_pair(adj,del_i,del_j):
    n=len(adj)
    seen=[-1]*n;low=[0]*n
    timer=0; bridges=[]
    def visit(u,parentedge):
        nonlocal timer
        seen[u]=low[u]=timer;timer+=1
        for v,eid in adj[u]:
            if eid==del_i or eid==del_j or eid==parentedge:continue
            if seen[v]<0:
                visit(v,eid)
                low[u]=min(low[u],low[v])
                if low[v]>seen[u]:bridges.append(eid)
            else:
                low[u]=min(low[u],seen[v])
    visit(0,-1)
    assert min(seen)>=0,("2-edge cut found",(del_i,del_j))
    return bridges


def girth_and_cycle(adj):
    best=10**9
    proof=None
    for start in range(len(adj)):
        dist=[-1]*len(adj)
        parent=[-1]*len(adj)
        dist[start]=0
        q=deque([start])
        while q:
            u=q.popleft()
            for v,e in adj[u]:
                if dist[v]<0:
                    dist[v]=dist[u]+1
                    parent[v]=u
                    q.append(v)
                elif parent[u]!=v and parent[v]!=u:
                    candidate=dist[u]+dist[v]+1
                    if candidate<best:
                        # candidate lengths upper bound actual graph
                        # cycle; 6 is minimum possible cubic linear
                        # incidence girth (no 4-cycles), and here
                        # repeated BFS computes true shortest cycle.
                        best=candidate
                        proof=(start,u,v)
    return best,proof


def balanced_separator_exhaustive(adj,kmax=2,fraction=Fraction(1,4)):
    n=len(adj);samples=0;smaller=None
    limit=(fraction.numerator*n+fraction.denominator-1)//fraction.denominator
    for k in range(1,kmax+1):
        for cut in combinations(range(n),k):
            samples+=1
            comps=comp_sizes(adj,removed_vertices=set(cut))
            if len(comps)<2:continue
            # Does removal partition graph into two unions of
            # components, each with size>=alpha*original_n?
            # For up to 2 removed vertices, an exhaustive subset
            # DP over components is safe (at most3 components).
            seen={0}
            for c in comps:
                seen|={v+c for v in tuple(seen)}
            nrest=n-k
            splits=[a for a in seen if limit<=a<=nrest-limit]
            if splits:
                smaller={"vertices":list(cut),"components":comps,
                         "partition_sizes":[min(splits),nrest-min(splits)]}
                return {"found":True,"proof":smaller,
                        "tested":samples,"kmax":kmax}
    return {"found":False,"proof":None,"tested":samples,
            "kmax":kmax,"alpha":str(fraction),
            "not_tested_k_greater_than":kmax}


def run(path):
    F=json.loads(Path(path).read_text())
    rows=F["base_45_rows"]
    assert len(rows)==45
    adj,E=graph_from_rows(rows)
    assert len(adj)==90 and len(E)==135
    assert comp_sizes(adj)==[90]
    girth,proof=girth_and_cycle(adj)
    assert girth==6
    edge_stars={
        tuple(sorted(eid for eid,(u,v) in enumerate(E)
                     if u==vertex or v==vertex))
        for vertex in range(len(adj))}
    assert len(edge_stars)==90
    threecuts=set()
    pair_checks=0
    for i in range(len(E)):
        for j in range(i+1,len(E)):
            pair_checks+=1
            for third in bridges_after_deleting_pair(adj,i,j):
                threecuts.add(tuple(sorted((i,j,third))))
    assert pair_checks==9045
    assert len(threecuts)==90,("unexpected 3-edge cuts",len(threecuts))
    assert threecuts==edge_stars,("nontrivial 3-edge cut")
    # A 3-edge star isolates a degree3 vertex and is TRIVIAL
    # (not a cyclic edge cut). Two-edge cuts were excluded
    # independently by the exhaustive 9045 pair tests.
    assert all(comp_sizes(adj,removed_edges=set(cut))==[1,89]
               for cut in threecuts)
    n=45
    cross_ids=[
        i for i,(u,v) in enumerate(E) if ((u<36)!=(v-n<36))]
    assert len(cross_ids)==4
    sizes=comp_sizes(adj,removed_edges=set(cross_ids))
    assert sizes==[18,72]
    # Both components have >=18 vertices, remain cubic except
    # cut edges; prove containing cycle by E−V+c per component.
    # A connected acyclic bipartite graph on 18 vertices has
    # at most17 internal edges; original internal edge counts:
    # 3*18−4? compute 18-vertex component internal E=25.
    parts=[]
    for region in (list(range(36))+list(range(n,n+36)),
                   list(range(36,n))+list(range(n+36,2*n))):
        Z=set(region)
        internal=sum(u in Z and v in Z for u,v in E)
        parts.append({"vertices":len(Z),"internal_edges":internal,
                      "cyclomatic_number":internal-len(Z)+1})
    assert [a["vertices"] for a in parts]==[72,18]
    assert all(x["cyclomatic_number"]>0 for x in parts)
    small=18
    conductance=Fraction(len(cross_ids),3*small)
    assert conductance==Fraction(2,27)
    # This exact cut certifies upper bounds on the expansion
    # curve for alpha<=18/90=0.20, but gives no bound at alpha=0.25.
    uppers={}
    for pct in (10,15,20,25):
        alpha=Fraction(pct,100)
        uppers[str(alpha)]=(
            str(conductance) if alpha<=Fraction(1,5) else None)
    sep=balanced_separator_exhaustive(adj,2,Fraction(1,4))
    assert sep["found"]==False
    return {"gate":"E4_9_EXACT_SOURCE_STRUCTURAL_PROFILE",
            "source_sha256":F["base_canonical_sha256"],
            "vertices":90,"edges":135,"degree":3,
            "source_connected":True,
            "incidence_girth":girth,
            "girth_BFS_proof":proof,
            "two_edge_pairs_checked":pair_checks,
            "all_3edge_cut_classes_exhaustively_recovered":len(threecuts),
            "all_3edge_cuts_trivial_vertex_stars":True,
            "possible_three_edge_sets_total":400995,
            "cyclic_edge_connectivity":4,
            "explicit_four_edge_cut_indices":cross_ids,
            "explicit_four_edge_cut_source_incidence":[
                [u,v-n] for i,(u,v) in enumerate(E) if i in cross_ids],
            "after_cut_component_sizes":sizes,
            "both_parts_contain_cycles":parts,
            "edge_conductance_upper_bound_fraction":str(conductance),
            "edge_conductance_upper_bound_approx":float(conductance),
            "explicit_cut_small_side_fraction":"1/5",
            "Phi_alpha_upper_bound_by_explicit_cut":uppers,
            "Phi_alpha_exact_minima":"NOT_COMPUTED",
            "balanced_25pct_vertex_cut_k_le2":sep,
            "balanced_vertex_separators_k3_k4":"NOT_RECHECKED_IN_THIS_GATE",
            "spectral_expansion_lower_bound":"PENDING_EXACT_INERTIA",
            "large_n_hardness":"NOT_PROVED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    x=p.parse_args()
    print(json.dumps(run(x.fixture),sort_keys=True,indent=2))
