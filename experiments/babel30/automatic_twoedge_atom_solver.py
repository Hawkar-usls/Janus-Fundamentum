#!/usr/bin/env python3
"""BABEL30: complete sound SAT/UNSAT/UNKNOWN on certified small-atom splices.

Real automatic graph-cut discovery; the solver DOES NOT receive a constructor
receipt, known block partition, SAT assignment, or complete tree. It builds
a verified cut-tree, solves restored atoms by exact Boolean DPLL, composes
integer two-state messages, and verifies a physical witness on ORIGINAL rows.

Unrestricted input can return UNKNOWN_NOT_ADMITTED. This is NOT P=NP.
"""
import hashlib
import itertools
import json
import sys
from collections import Counter

sys.setrecursionlimit(10000)

U=(
    (0,1,2),(0,3,6),(0,5,7),(3,5,20),(1,7,11),
    (3,8,12),(6,7,8),(2,5,8),(2,10,14),
    (9,10,11),(9,12,15),(9,14,22),
    (12,13,14),(10,13,16),(1,6,17),(15,16,17),
    (4,17,20),(11,13,21),(4,18,19),(15,18,24),
    (18,23,25),(21,22,23),(16,19,25),
    (19,21,26),(24,25,26),(4,23,26),(20,22,24)
)
U_SHA="9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
U_TRUE=(2,3,7,9,13,17,19,23,24)


def validate(rows,need_connected=True):
    """Rows keyed by immutable global row ids; variable ids also global."""
    if not rows:return False
    n=len(rows)
    allvars=set(v for row in rows.values() for v in row)
    if len(allvars)!=n:return False
    if any(len(row)!=3 or len(set(row))!=3 for row in rows.values()):return False
    if Counter(v for row in rows.values() for v in row)!=Counter({v:3 for v in allvars}):
        return False
    pairs=[tuple(sorted(p)) for row in rows.values()
           for p in itertools.combinations(row,2)]
    if len(set(pairs))!=3*n:return False
    if need_connected:
        adjacency={v:set() for v in allvars}
        for row in rows.values():
            for v in row:adjacency[v].update(row)
        seen={min(allvars)}; stack=[min(allvars)]
        while stack:
            for v in adjacency[stack.pop()]-seen:
                seen.add(v);stack.append(v)
        if len(seen)!=n:return False
    return True


def exactone(rows,assignment):
    return all(sum((assignment>>j)&1 for j in row)==1 for row in rows.values())


def exact_local_DPLL(rows):
    """Complete enumeration on at most w variables, safe unit propagation."""
    variables=sorted({v for row in rows.values() for v in row})
    n=len(variables)
    remap={v:i for i,v in enumerate(variables)}
    clauses=tuple(tuple(remap[v] for v in row) for row in rows.values())
    incidence=[sum(j in row for row in clauses) for j in range(n)]
    all_models=[];calls=0
    def explore(assigned,truth):
        nonlocal calls
        calls+=1
        while True:
            change=False
            for row in clauses:
                yes=sum((truth>>j)&1 for j in row)
                undec=[j for j in row if not assigned>>j&1]
                if yes>1 or yes+len(undec)<1:return
                if yes==1 and undec:
                    for j in undec:assigned|=1<<j
                    change=True
                elif yes==0 and len(undec)==1:
                    j=undec[0];assigned|=1<<j;truth|=1<<j;change=True
            if not change:break
        if assigned.bit_count()==n:
            global_assignment=sum(1<<variables[j] for j in range(n) if truth>>j&1)
            assert exactone(rows,global_assignment)
            all_models.append(global_assignment)
            return
        choices=(j for j in range(n) if not assigned>>j&1)
        var=max(choices,key=lambda j:(incidence[j],-j))
        explore(assigned|(1<<var),truth)
        explore(assigned|(1<<var),truth|(1<<var))
    explore(0,0)
    assert len(all_models)==len(set(all_models))
    return all_models,calls


def vertex_graph(rows,total_n):
    """Bipartite: 0..N-1 row vertices, N..2N-1 variable vertices."""
    edges=sorted((r,total_n+v) for r,row in rows.items() for v in row)
    adj={}
    for idx,(r,v) in enumerate(edges):
        adj.setdefault(r,[]).append((v,idx))
        adj.setdefault(v,[]).append((r,idx))
    return edges,adj


def bridges_excluding(adj,excluded):
    disc={};low={};clock=0;bridges=[]
    def dfs(v,parent_id):
        nonlocal clock
        clock+=1;disc[v]=low[v]=clock
        for nxt,idx in adj[v]:
            if idx==excluded or idx==parent_id:continue
            if nxt not in disc:
                dfs(nxt,idx)
                low[v]=min(low[v],low[nxt])
                if low[nxt]>disc[v]:
                    bridges.append(idx)
            else:
                low[v]=min(low[v],disc[nxt])
    start=min(adj)
    dfs(start,-1)
    if len(disc)!=len(adj):return []
    return sorted(bridges)


def components_after_two(adj,remove_a,remove_b):
    seen=set();comps=[]
    for start in sorted(adj):
        if start in seen:continue
        group={start};seen.add(start);stack=[start]
        while stack:
            for nxt,idx in adj[stack.pop()]:
                if idx in (remove_a,remove_b) or nxt in seen:continue
                seen.add(nxt);group.add(nxt);stack.append(nxt)
        comps.append(group)
    return comps


def certified_inverse_cut(rows,total_n):
    """Return first fully-validated inverse splice, or None in polynomial time."""
    edges,adj=vertex_graph(rows,total_n)
    ecount=len(edges)
    for e1 in range(ecount):
        for e2 in bridges_excluding(adj,e1):
            comps=components_after_two(adj,e1,e2)
            if len(comps)!=2:continue
            A,B=comps
            row1,var1=edges[e1]
            row2,var2=edges[e2]
            # Demand crossing orientations r_A -> v_B, r_B -> v_A.
            if row1 not in A or var1 not in B:
                if row1 in B and var1 in A:
                    A,B=B,A
                else:continue
            if row2 not in B or var2 not in A:continue
            left_roots={r for r in rows if r in A}
            right_roots=set(rows)-left_roots
            if not left_roots or not right_roots:continue
            if len(left_roots)%3 or len(right_roots)%3:continue
            left={r:[v for v in rows[r] if total_n+v in A]
                  for r in left_roots}
            right={r:[v for v in rows[r] if total_n+v in B]
                   for r in right_roots}
            va=var2-total_n
            vb=var1-total_n
            if va in left[row1] or vb in right[row2]:continue
            left[row1].append(va);right[row2].append(vb)
            l={r:tuple(sorted(v)) for r,v in left.items()}
            r={r:tuple(sorted(v)) for r,v in right.items()}
            if not validate(l) or not validate(r):continue
            # Independently replay forward cross exchange and reproduce
            # EVERY original incidence, including row/variable ownership.
            check_left={i:list(row) for i,row in l.items()}
            check_right={i:list(row) for i,row in r.items()}
            check_left[row1].remove(va);check_left[row1].append(vb)
            check_right[row2].remove(vb);check_right[row2].append(va)
            forward={i:tuple(sorted(v)) for i,v in check_left.items()}
            forward.update({i:tuple(sorted(v)) for i,v in check_right.items()})
            assert forward==rows
            assert (va in {v for row in l.values() for v in row})
            assert (vb in {v for row in r.values() for v in row})
            return l,r,(va,vb),{"cross_incidence_edges":
                                 [[row1,vb],[row2,va]],
                                 "restored_incidence_edges":
                                 [[row1,va],[row2,vb]],
                                 "subproblem_sizes":[len(l),len(r)],
                                 "e1_index":e1,"e2_index":e2}
    return None


def construct_atoms(rows,total_n,w):
    """Each split is certified by inverse forward-incidence equality."""
    leaves=[];links=[];receipts=[]
    def recurse(component):
        if len(component)<=w:
            assert validate(component)
            leaves.append(component)
            return True
        split=certified_inverse_cut(component,total_n)
        if split is None:return False
        left,right,link,receipt=split
        receipts.append(receipt)
        if not recurse(left):return False
        if not recurse(right):return False
        links.append(link)
        return True
    if not recurse(rows):return None
    return leaves,links,receipts


def tree_messages(leaves,links):
    """Exact full integer #SAT and physically verified model for each tree."""
    owners={}
    leafmodels=[];dpll_calls=0
    for atom_id,atom in enumerate(leaves):
        for v in {x for row in atom.values() for x in row}:
            assert v not in owners
            owners[v]=atom_id
        models,calls=exact_local_DPLL(atom)
        leafmodels.append(models);dpll_calls+=calls
    adj=[[] for _ in leaves]
    for a,b in links:
        ia,ib=owners[a],owners[b]
        assert ia!=ib
        adj[ia].append((ib,a,b))
        adj[ib].append((ia,b,a))
    assert len(links)==len(leaves)-1
    reached={0};queue=[0]
    while queue:
        for j,_,_ in adj[queue.pop()]:
            if j not in reached:reached.add(j);queue.append(j)
    assert len(reached)==len(leaves)
    msgs={}
    root_count=None
    def compute(i,parent,parent_var):
        children=[]
        for j,mine,theirs in adj[i]:
            if j==parent:continue
            child=compute(j,i,theirs)
            children.append((mine,child))
        acc=[0,0] if parent!=-1 else 0
        for model in leafmodels[i]:
            weight=1
            for mine,child_msg in children:
                weight*=child_msg[(model>>mine)&1]
                if not weight:break
            if parent==-1:
                acc+=weight
            else:
                acc[(model>>parent_var)&1]+=weight
        if parent!=-1:msgs[(i,parent)]=acc
        return acc
    root_count=compute(0,-1,None)
    assert isinstance(root_count,int) and root_count>=0
    witness=None
    if root_count>0:
        parts=[]
        def recover(i,parent,parent_bit,parent_var):
            for model in leafmodels[i]:
                if parent!=-1 and ((model>>parent_var)&1)!=parent_bit:
                    continue
                good=True
                for j,mine,theirs in adj[i]:
                    if j==parent:continue
                    if msgs[(j,i)][(model>>mine)&1]==0:
                        good=False;break
                if not good:continue
                parts.append(model)
                for j,mine,theirs in adj[i]:
                    if j!=parent:recover(j,i,(model>>mine)&1,theirs)
                return
            raise AssertionError("positive message without compatible model")
        recover(0,-1,0,None)
        assert len(parts)==len(leaves)
        witness=0
        for p in parts:
            assert not(witness&p),"atoms must be disjoint"
            witness|=p
        for a,b in links:
            assert ((witness>>a)&1)==((witness>>b)&1)
    return root_count,witness,{"atom_sizes":[len(x) for x in leaves],
                               "number_of_atoms":len(leaves),
                               "two_state_links":len(links),
                               "total_DPLL_nodes":dpll_calls,
                               "message_tables":len(msgs),
                               "model_count_binary_bits":root_count.bit_length()}


def solve_admitted(rows,w=27):
    """Full three-way result; SAT/UNSAT only after certified small-atom split."""
    n=len(rows)
    if not validate(rows):
        return {"status":"INVALID_SCL_INPUT","n":n}
    if n%3:
        return {"status":"UNSAT","certificate":"THREE_REGULAR_N_MOD3","n":n,
                "count":0,"witness":None}
    decomposition=construct_atoms(rows,n,w)
    if decomposition is None:
        return {"status":"UNKNOWN_NOT_ADMITTED","n":n,"witness":None,
                "reason":"no certified 2-edge splice tree with atoms <=w"}
    leaves,links,receipts=decomposition
    count,witness,work=tree_messages(leaves,links)
    if count:
        assert witness is not None
        assert exactone(rows,witness),"invalid output on ORIGINAL input"
        status="SAT"
    else:
        assert witness is None
        status="UNSAT"
    return {"status":status,"n":n,"count":count,"witness":witness,
            "witness_ones":[j for j in range(n) if witness>>j&1]
                if witness is not None else None,
            "work":work,"splice_receipts":receipts}


def chain_frozen(t):
    assert t>=1
    rows={r:tuple(row) for r,row in enumerate(U)}
    base_true=sum(1<<v for v in U_TRUE)
    combined_true=base_true
    for step in range(2,t+1):
        old_n=27*(step-1)
        right={old_n+r:tuple(old_n+v for v in row) for r,row in enumerate(U)}
        row_left=0;row_right=old_n
        a=min(v for v in rows[row_left] if not combined_true>>v&1)
        b=min(v for v in right[row_right] if not (base_true>>(v-old_n))&1)
        left_row=[v for v in rows[row_left] if v!=a]+[b]
        right_row=[v for v in right[row_right] if v!=b]+[a]
        rows[row_left]=tuple(sorted(left_row))
        right[row_right]=tuple(sorted(right_row))
        rows.update(right)
        combined_true|=base_true<<old_n
        assert validate(rows)
        assert exactone(rows,combined_true)
    return rows


def single_splice_control(right_literal):
    rows={i:tuple(row) for i,row in enumerate(U)}
    rows.update({27+i:tuple(27+v for v in row) for i,row in enumerate(U)})
    assert 0 in rows[0] and 27+right_literal in rows[27]
    rows[0]=tuple(sorted([v for v in rows[0] if v!=0]+[27+right_literal]))
    rows[27]=tuple(sorted([v for v in rows[27] if v!=27+right_literal]+[0]))
    assert validate(rows)
    return rows


def two_splice_unadmitted_control():
    rows={i:tuple(row) for i,row in enumerate(U)}
    rows.update({27+i:tuple(27+v for v in row) for i,row in enumerate(U)})
    for ri,a,si,b in ((11,22,22,25),(22,25,11,22)):
        r=ri;s=27+si;vv=27+b
        rows[r]=tuple(sorted([v for v in rows[r] if v!=a]+[vv]))
        rows[s]=tuple(sorted([v for v in rows[s] if v!=vv]+[a]))
    assert validate(rows)
    return rows


def main():
    assert hashlib.sha256(json.dumps(U,separators=(",",":")).encode()).hexdigest()==U_SHA
    assert solve_admitted({i:tuple(r) for i,r in enumerate(U)})["status"]=="SAT"
    tests=[]
    for t in (2,3,5,9):
        rows=chain_frozen(t)
        result=solve_admitted(rows,w=27) # no constructor receipt passed
        assert result["status"]=="SAT",(t,result)
        assert result["count"]==1
        assert result["work"]["number_of_atoms"]==t,result["work"]
        assert exactone(rows,result["witness"])
        tests.append({"fixture":f"CONNECTED_CHAIN_C{t}",
                      "n":len(rows),"status":result["status"],
                      "count":result["count"],
                      "atoms":result["work"]["number_of_atoms"],
                      "largest_atom":max(result["work"]["atom_sizes"]),
                      "two_state_links":result["work"]["two_state_links"],
                      "cut_discovered_without_history":True,
                      "physical_witness_verified":True})
    for name,lit,expected in (
        ("CONNECTED_SCL54_MATCHING_SAT",0,"SAT"),
        ("CONNECTED_SCL54_MISMATCH_UNSAT",2,"UNSAT")):
        rows=single_splice_control(lit)
        result=solve_admitted(rows,w=27)
        assert result["status"]==expected,(name,result)
        assert result["count"]==(1 if expected=="SAT" else 0)
        assert result["work"]["number_of_atoms"]==2
        tests.append({"fixture":name,"n":54,"status":result["status"],
                      "count":result["count"],
                      "two_state_links":1,"atoms":2})
    two=solve_admitted(two_splice_unadmitted_control(),w=27)
    assert two["status"] in ("UNKNOWN_NOT_ADMITTED","SAT")
    if two["status"]=="SAT":
        assert two["count"]==2
    tests.append({"fixture":"CONNECTED_SCL54_TWO_CROSS_SWAPS",
                  "n":54,"status":two["status"],
                  "count":two.get("count"),
                  "unsupported_is_not_unsat":True})
    print(json.dumps({
      "gate":"BABEL30_AUTOMATIC_ADMITTED_TWOEDGE_ATOM_TREE_DECIDER",
      "theorem_scope":"FIXED_ATOM_SIZE_w_CERTIFIED_RECURSIVE_TWOEDGE_SPLICE",
      "unknown_preserved_on_nonadmission":True,
      "automatic_cut_discovery_without_receipts":True,
      "sound_SAT_witness_recovery":True,
      "sound_UNSAT_exact_integer_tree_DP":True,
      "arbitrary_connected_SCL_poly_admission":"NOT_PROVED",
      "general_SAT_in_P":"NOT_PROVED",
      "P_vs_NP":"OPEN",
      "controls":tests
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
