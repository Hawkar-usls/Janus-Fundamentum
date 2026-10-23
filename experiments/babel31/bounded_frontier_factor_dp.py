#!/usr/bin/env python3
"""BABEL31: exact bounded-frontier factor-graph count and SAT/UNSAT/UNKNOWN.

Unlike a splice-specific algorithm, ports are ORIGINAL incidence edges. All
joins enforce equality of the row-end and variable-end bits. The discovered
binary cut tree must have frontier <=B at EVERY subtree and leaves <=W
factor-graph vertices. Candidate discovery is polynomial but not complete.
"""
from collections import Counter, defaultdict, deque
from itertools import combinations


def legal_connected_scl(rows):
    n=len(rows)
    if not n or set(rows)!=set(range(n)):return False
    if any(len(row)!=3 or len(set(row))!=3 or
           any(v not in range(n) for v in row) for row in rows.values()):
        return False
    if Counter(v for row in rows.values() for v in row)!=Counter({v:3 for v in range(n)}):
        return False
    pairs=[tuple(sorted(p)) for row in rows.values() for p in combinations(row,2)]
    if len(set(pairs))!=3*n:return False
    graph={v:set() for v in range(n)}
    for row in rows.values():
        for v in row:graph[v].update(row)
    seen={0};q=[0]
    while q:
        for v in graph[q.pop()]-seen:
            seen.add(v);q.append(v)
    return len(seen)==n


def exact_one(rows,x):
    return all(sum((x>>v)&1 for v in row)==1 for row in rows.values())


class FactorGraph:
    def __init__(self,rows):
        self.rows=rows
        self.n=len(rows)
        self.all_vertices=set(range(2*self.n))
        self.edges=tuple(sorted((r,self.n+v) for r,row in rows.items() for v in row))
        self.adj={v:[] for v in self.all_vertices}
        for eid,(r,v) in enumerate(self.edges):
            self.adj[r].append((v,eid))
            self.adj[v].append((r,eid))

    def boundary(self,subset):
        return tuple(i for i,(r,v) in enumerate(self.edges)
                     if (r in subset)!=(v in subset))

    def distances(self,subset,start):
        dist={start:0};queue=deque([start])
        while queue:
            v=queue.popleft()
            for nxt,_ in self.adj[v]:
                if nxt in subset and nxt not in dist:
                    dist[nxt]=dist[v]+1
                    queue.append(nxt)
        return dist

    def connected(self,subset):
        return bool(subset) and len(self.distances(subset,min(subset)))==len(subset)

    def bounded_anchored_cut(self,subset,source,sink,limit):
        """Exact unit-edge mincut capped at limit+1; no probabilistic oracle."""
        # A wider anchor neighborhood blocks trivial radius-1 star cuts
        # when the frontier budget reaches six incidence edges. Candidate
        # selection is heuristic; every accepted edge cut remains exact.
        radius=2 if limit>=6 else 1
        def anchored_ball(center):
            return {v for v,distance in self.distances(subset,center).items()
                    if distance<=radius}
        anchor_a=anchored_ball(source)
        anchor_b=anchored_ball(sink)
        if anchor_a&anchor_b:return None
        head,tail=-1,-2
        big=limit+2
        residual=defaultdict(dict)

        def add_arc(u,v,capacity):
            residual[u][v]=residual[u].get(v,0)+capacity
            residual[v].setdefault(u,0)

        for u,v in self.edges:
            if u in subset and v in subset:
                add_arc(u,v,1)
                add_arc(v,u,1)
        for v in anchor_a:add_arc(head,v,big)
        for v in anchor_b:add_arc(v,tail,big)

        flow=0
        while flow<=limit:
            parent={head:None}
            queue=deque([head])
            while queue and tail not in parent:
                u=queue.popleft()
                for v,cap in residual[u].items():
                    if cap>0 and v not in parent:
                        parent[v]=u
                        queue.append(v)
            if tail not in parent:break
            augment=big;v=tail
            while v!=head:
                u=parent[v];augment=min(augment,residual[u][v]);v=u
            v=tail
            while v!=head:
                u=parent[v]
                residual[u][v]-=augment
                residual[v][u]+=augment
                v=u
            flow+=augment
        if flow>limit:return None

        reachable={head};queue=deque([head])
        while queue:
            u=queue.popleft()
            for v,cap in residual[u].items():
                if cap>0 and v not in reachable:
                    reachable.add(v)
                    queue.append(v)
        left=subset&reachable
        right=subset-left
        if not self.connected(left) or not self.connected(right):return None
        crossing=sum((u in left)!=(v in left)
                     for u,v in self.edges if u in subset and v in subset)
        assert crossing==flow
        # This all-original-edges guard prevents hidden ancestor frontier growth.
        if len(self.boundary(left))>limit or len(self.boundary(right))>limit:
            return None
        return left,right,crossing

    def proposed_split(self,subset,limit):
        row_nodes=sorted(v for v in subset if v<self.n)
        if len(row_nodes)<2:return None
        seeds=sorted(set(row_nodes[i] for i in
                         (0,len(row_nodes)-1,len(row_nodes)//2,
                          len(row_nodes)//4,3*len(row_nodes)//4)))
        choices=[]
        for first in seeds:
            distances=self.distances(subset,first)
            far=sorted((v for v in row_nodes if v!=first),
                       key=lambda v:(-distances.get(v,-1),v))[:4]
            for second in far:
                result=self.bounded_anchored_cut(subset,first,second,limit)
                if result is not None:
                    a,b,edges=result
                    choices.append((min(len(a),len(b)),-edges,first,second,a,b))
        if not choices:return None
        choices.sort(key=lambda x:(-x[0],-x[1],x[2],x[3]))
        _,_,first,second,a,b=choices[0]
        return a,b,(first,second)


def leaf_table(graph,subset,frontier):
    """Exhaustive Exact-One DPLL with free external-row port symbols."""
    local_vars=sorted(v-graph.n for v in subset if v>=graph.n)
    external_ports=[eid for eid in frontier
                    if graph.edges[eid][0] in subset]
    symbols=[("var",v) for v in local_vars]+[("port",eid) for eid in external_ports]
    index={token:i for i,token in enumerate(symbols)}
    clauses=[]
    for row_id in sorted(v for v in subset if v<graph.n):
        clause=[]
        for variable in graph.rows[row_id]:
            if graph.n+variable in subset:
                clause.append(index[("var",variable)])
            else:
                eid=next(eid for peer,eid in graph.adj[row_id]
                         if peer==graph.n+variable)
                clause.append(index[("port",eid)])
        assert len(set(clause))==3
        clauses.append(clause)
    degree=[sum(i in clause for clause in clauses) for i in range(len(symbols))]
    table={}
    calls=0

    def visit(assigned,true):
        nonlocal calls
        calls+=1
        while True:
            changed=False
            for row in clauses:
                ones=sum((true>>i)&1 for i in row)
                missing=[i for i in row if not (assigned>>i)&1]
                if ones>1 or ones+len(missing)<1:return
                if ones==1 and missing:
                    for i in missing:assigned|=1<<i
                    changed=True
                elif ones==0 and len(missing)==1:
                    i=missing[0]
                    assigned|=1<<i
                    true|=1<<i
                    changed=True
            if not changed:break

        if assigned.bit_count()==len(symbols):
            physical=sum(1<<v for v in local_vars
                         if (true>>index[("var",v)])&1)
            signature=[]
            for eid in frontier:
                r,variable_node=graph.edges[eid]
                if variable_node in subset:
                    signature.append((physical>>(variable_node-graph.n))&1)
                else:
                    signature.append((true>>index[("port",eid)])&1)
            key=tuple(signature)
            previous_count,previous_witness=table.get(key,(0,physical))
            table[key]=(previous_count+1,previous_witness)
            return
        candidates=(i for i in range(len(symbols)) if not (assigned>>i)&1)
        i=max(candidates,key=lambda i:(degree[i],-i))
        visit(assigned|(1<<i),true)
        visit(assigned|(1<<i),true|(1<<i))

    visit(0,0)
    return table,calls,len(symbols)


def join_tables(table_a,table_b,bound_a,bound_b,bound_parent):
    index_a={eid:i for i,eid in enumerate(bound_a)}
    index_b={eid:i for i,eid in enumerate(bound_b)}
    common=sorted(set(index_a)&set(index_b))
    assert not set(common)&set(bound_parent)
    right_lookup=defaultdict(list)
    for bits,(count,witness) in table_b.items():
        key=tuple(bits[index_b[e]] for e in common)
        right_lookup[key].append((bits,count,witness))
    output={}
    for bits_a,(count_a,witness_a) in table_a.items():
        key=tuple(bits_a[index_a[e]] for e in common)
        for bits_b,count_b,witness_b in right_lookup[key]:
            assert not (witness_a&witness_b)
            merged=tuple(bits_a[index_a[e]] if e in index_a
                         else bits_b[index_b[e]] for e in bound_parent)
            previous_count,previous_witness=output.get(
                merged,(0,witness_a|witness_b))
            output[merged]=(previous_count+count_a*count_b,previous_witness)
    return output


def exact_table_receipt(table):
    return [{"bits":list(bits),"count":count,"witness":str(witness)}
            for bits,(count,witness) in sorted(table.items())]


def solve(rows,leaf_vertices=54,frontier_limit=4):
    """Sound exact SAT/UNSAT/UNKNOWN; candidate discovery is not complete."""
    n=len(rows)
    if not legal_connected_scl(rows):
        return {"status":"INVALID_SCL_INPUT","n":n}
    if n%3:
        return {"status":"UNSAT","n":n,"count":0,"witness":None,
                "certificate":"3_REGULAR_GLOBAL_COUNT_MOD3"}
    if leaf_vertices<1 or frontier_limit<0:
        return {"status":"INVALID_PARAMETERS","n":n}
    graph=FactorGraph(rows)
    assert len(graph.edges)==3*n
    diagnostics={"splits":[],"leaves":[],"leaf_dpll_calls":0}

    def recurse(subset):
        boundary=graph.boundary(subset)
        assert len(boundary)<=frontier_limit
        if len(subset)<=leaf_vertices:
            table,calls,vars_and_ports=leaf_table(graph,subset,boundary)
            diagnostics["leaves"].append({
                "factor_vertices":len(subset),
                "frontier_edges":len(boundary),
                "table_entries":len(table),
                "leaf_variables_plus_ports":vars_and_ports})
            diagnostics["leaf_dpll_calls"]+=calls
            certificate={
                "type":"leaf",
                "vertices":sorted(subset),
                "frontier":list(boundary),
                "table":exact_table_receipt(table)
            }
            return table,certificate
        proposed=graph.proposed_split(subset,frontier_limit)
        if proposed is None:
            raise ValueError("No certified small-frontier split for "+
                             str(len(subset))+" factor-graph vertices")
        a,b,anchors=proposed
        cross=set(graph.boundary(a))&set(graph.boundary(b))
        diagnostics["splits"].append({
            "child_factor_vertices":[len(a),len(b)],
            "crossing_incidence_edges":len(cross),
            "parent_frontier":len(boundary),
            "anchor_clause_ids":list(anchors)})
        left,left_certificate=recurse(a)
        right,right_certificate=recurse(b)
        table=join_tables(left,right,graph.boundary(a),graph.boundary(b),
                          boundary)
        certificate={
            "type":"merge",
            "vertices":sorted(subset),
            "frontier":list(boundary),
            "table":exact_table_receipt(table),
            "left":left_certificate,
            "right":right_certificate
        }
        return table,certificate

    try:
        root_table,root_certificate=recurse(graph.all_vertices)
    except ValueError as err:
        return {"status":"UNKNOWN_NOT_ADMITTED","n":n,
                "reason":str(err),"diagnostics":diagnostics}
    assert set(root_table).issubset({()})
    count,witness=root_table.get((),(0,None))
    receipt={
        "schema":"BABEL31/EXACT-BOUNDARY-TABLE-TREE/v1",
        "leaf_vertices":leaf_vertices,"frontier_limit":frontier_limit,
        "original_rows":n,
        "root":root_certificate
    }
    if count:
        assert witness is not None
        assert exact_one(rows,witness), "FAIL: original Exact-One row"
        return {"status":"SAT","count":count,"n":n,"witness":witness,
                "witness_one_indices":[j for j in range(n) if (witness>>j)&1],
                "diagnostics":diagnostics,"receipt":receipt}
    return {"status":"UNSAT","count":0,"n":n,"witness":None,
            "diagnostics":diagnostics,"receipt":receipt}
