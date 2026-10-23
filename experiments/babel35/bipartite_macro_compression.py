#!/usr/bin/env python3
"""BABEL35 proof-carrying 3-state macro CSP compression: count1 vs count3.

The 24-row local relation is independently obtained through COMPLETE Boolean
DPLL and ALL exact rational free-coordinate projections. The macro compiler
and inverse verifier do not use earlier BABEL33 producers. Actual physical
SAT witnesses are replayed on all original Exact-One clauses.
"""
import hashlib
import itertools
import json
import random
from collections import Counter,deque
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from experiments.babel34.local_three_port_forcing import (
    ROWS, SHA, ONES, local_dpll, exhaustive_q_boolean_projection,
    gf2_rank, exact_one
)

PORTS=((0,1),(8,10),(16,4))
STATE_PAIRS=((0,0),(0,1),(1,0))


def get_relation():
    assert len(ROWS)==27
    assert hashlib.sha256(json.dumps(ROWS,separators=(",",":")).encode()).hexdigest()==SHA
    punctured=tuple(row for i,row in enumerate(ROWS) if i not in (0,8,16))
    dpll,dpll_calls=local_dpll(punctured)
    by_Q,rank,free=exhaustive_q_boolean_projection(punctured)
    assert dpll==by_Q
    assert len(dpll)==3 and rank==24 and free==(23,25,26)
    model_lookup={}
    full_local=[]
    for x in sorted(dpll):
        out=tuple((x>>v)&1 for row,v in PORTS)
        required=tuple(1-sum((x>>j)&1 for j in ROWS[row] if j!=v)
                       for row,v in PORTS)
        assert all(z in (0,1) for z in required)
        assert len(set(out))==1 and len(set(required))==1
        state=(out[0],required[0])
        assert state in STATE_PAIRS and state not in model_lookup
        model_lookup[state]=x
        full_local.append({
           "state":list(state),
           "export_bits":list(out),
           "import_bits":list(required),
           "true_indices":[j for j in range(27) if x>>j&1]
        })
    assert set(model_lookup)==set(STATE_PAIRS)
    assert tuple(i for i in range(27) if model_lookup[(0,0)]>>i&1)==ONES
    assert sorted(tuple(i for i in range(27) if x>>i&1) for x in dpll)==sorted([
        (2,3,7,9,13,17,19,23,24),
        (5,6,11,12,16,18,22,26),
        (0,1,4,8,10,14,15,20,21,25)])
    # Each port-deleted interior block stays connected.
    adjacency={i:set() for i in range(54)}
    for r,row in enumerate(ROWS):
        for v in row:
            if (r,v) in PORTS:continue
            adjacency[r].add(27+v)
            adjacency[27+v].add(r)
    seen={0};q=[0]
    while q:
        for v in adjacency[q.pop()]-seen:
            seen.add(v);q.append(v)
    assert len(seen)==54
    return model_lookup,{
      "punctured_Q_rank":rank,
      "Q_free_coordinates":list(free),
      "Q_boolean_projections_checked":1<<len(free),
      "Boolean_DPLL_calls":dpll_calls,
      "complete_punctured_model_count":3,
      "full_feasible_boundary_relation":full_local,
      "all_port_deleted_interior_vertices_connected":True
    }


def prism_macro(t,seed,shuffle_ports):
    assert t>=8 and t%2==0
    m=t//2
    edges=set()
    for off in (0,m):
        for i in range(m):
            edges.add(tuple(sorted((off+i,off+(i+1)%m))))
    for i in range(m):
        edges.add((i,m+i))
    assert len(edges)==3*t//2
    adj={i:set() for i in range(t)}
    for a,b in edges:
        adj[a].add(b);adj[b].add(a)
    assert all(len(v)==3 for v in adj.values())
    rng=random.Random(seed)
    port_map={}
    for i in range(t):
        near=sorted(adj[i])
        if shuffle_ports:rng.shuffle(near)
        port_map[i]={v:j for j,v in enumerate(near)}
    return tuple(sorted(edges)),adj,port_map


def two_color(adj):
    color={}
    for start in sorted(adj):
        if start in color:continue
        color[start]=0
        q=deque([start])
        while q:
            a=q.popleft()
            for b in adj[a]:
                if b in color:
                    if color[b]==color[a]:
                        return None
                else:
                    color[b]=1-color[a]
                    q.append(b)
    return color


def build_J(t,edges,adj,ports):
    n=27*t
    clauses=[list(27*block+j for j in row)
             for block in range(t) for row in ROWS]
    for a,b in edges:
        ra,va=PORTS[ports[a][b]]
        rb,vb=PORTS[ports[b][a]]
        r_a=27*a+ra
        r_b=27*b+rb
        v_a=27*a+va
        v_b=27*b+vb
        assert v_a in clauses[r_a] and v_b in clauses[r_b]
        clauses[r_a][clauses[r_a].index(v_a)]=v_b
        clauses[r_b][clauses[r_b].index(v_b)]=v_a
    return tuple(tuple(sorted(row)) for row in clauses)


def independent_template_verifier(rows,t):
    """Checks every local kept row, every exported/imported port reciprocity."""
    n=27*t
    assert len(rows)==n
    assert Counter(v for row in rows for v in row)==Counter({v:3 for v in range(n)})
    assert all(len(row)==3 and len(set(row))==3 for row in rows)
    pairs=[tuple(sorted(pair)) for row in rows
           for pair in itertools.combinations(row,2)]
    assert len(set(pairs))==3*n
    adj={v:set() for v in range(t)}
    for block in range(t):
        for ri,original in enumerate(ROWS):
            actual=rows[27*block+ri]
            ps=[v for r,v in PORTS if r==ri]
            if not ps:
                assert actual==tuple(27*block+v for v in original)
            else:
                assert len(ps)==1
                localset={v for v in actual if v//27==block}
                assert localset=={27*block+v for v in original if v!=ps[0]}
                outside=[v for v in actual if v//27!=block]
                assert len(outside)==1
                target=outside[0]//27
                assert target!=block
                # The imported variable must be exactly one of the neighbor's
                # three exported original port variables, reciprocally swapped.
                indices=[i for i,(r,v) in enumerate(PORTS) if v==outside[0]%27]
                assert len(indices)==1
                remote_row=PORTS[indices[0]][0]
                assert 27*block+ps[0] in rows[27*target+remote_row]
                adj[block].add(target)
    assert all(len(ad)==3 for ad in adj.values())
    assert all(a in adj[b] for a in adj for b in adj[a])
    seen={0};q=[0]
    while q:
        for b in adj[q.pop()]-seen:seen.add(b);q.append(b)
    assert len(seen)==t
    return adj


def global_model(rows,states,lookup):
    assignment=sum(lookup[states[b]]<<(27*b) for b in range(len(states)))
    assert exact_one(rows,assignment)
    return assignment


def independent_macro_exhaustive(adj,t):
    """Independent 3^t enumeration of compressed local state assignments."""
    assert t<=10,"finite 3**t brute control only"
    count=0
    for candidate in itertools.product(range(3),repeat=t):
        if all(STATE_PAIRS[candidate[a]][0]==STATE_PAIRS[candidate[b]][1]
               and STATE_PAIRS[candidate[b]][0]==STATE_PAIRS[candidate[a]][1]
               for a in range(t) for b in adj[a] if a<b):
            count+=1
    return count


def one_test(t,seed,shuffle_ports,lookup):
    edges,adj,portmap=prism_macro(t,seed,shuffle_ports)
    rows=build_J(t,edges,adj,portmap)
    recovered=independent_template_verifier(rows,t)
    assert recovered==adj
    bipartite=two_color(recovered)
    predicted=3 if bipartite is not None else 1
    candidate_states=[[(0,0)]*t]
    if bipartite is not None:
        for orientation in (0,1):
            candidate_states.append([
                (0,1) if bipartite[i]==orientation else (1,0)
                for i in range(t)])
    assert len(candidate_states)==predicted
    models=set()
    for states in candidate_states:
        x=global_model(rows,states,lookup)
        assert x not in models
        models.add(x)
    assert len(models)==predicted
    brute=None
    if t<=10:
        brute=independent_macro_exhaustive(adj,t)
        assert brute==predicted
    d=27*t-gf2_rank(rows)
    assert d>=3*t//2
    return {
       "macro_blocks":t,"n_variables":len(rows),
       "macro_bipartite":bipartite is not None,
       "exact_SAT_count_from_all_n_theorem":predicted,
       "independent_all_macro_3_pow_t_state_count":brute,
       "GF2_nullity_exact":d,
       "GF2_nullity_lower_bound":3*t//2,
       "physical_models_replayed_against_every_original_row":len(models),
       "macro_vertex_port_permutation":shuffle_ports,
       "certified_port_template_structure":"PASS",
       "macro_rows_sha256":hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest()
    }


def main():
    lookup,local=get_relation()
    controls=[
        one_test(t,seed=3500+t,shuffle_ports=False,lookup=lookup)
        for t in (8,10,12,14,16,24,40)
    ]
    controls.extend(
        one_test(t,seed=35000+t,shuffle_ports=True,lookup=lookup)
        for t in (8,10,12,16)
    )
    assert [x["exact_SAT_count_from_all_n_theorem"] for x in controls[:4]]==[3,1,3,1]
    assert all(x["certified_port_template_structure"]=="PASS" for x in controls)
    print(json.dumps({
       "gate":"BABEL35_MACRO_TWO_COLOR_STATE_COMPRESSION",
       "local_complete_boundary_relation":"{00,01,10}",
       "all_n_exact_count":"3_IF_BIPARTITE_ELSE_1",
       "admitted_template_SAT_and_count_runtime":"O(N)",
       "all_n_high_GF2_nullity":"GE_3T_OVER_2",
       "general_unknown_template_discovery":"OPEN",
       "universal_P_time_SCL":"NOT_PROVED",
       "P_vs_NP":"OPEN",
       "local":local,
       "controls":controls
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
