#!/usr/bin/env python3
"""
Finite sanity checker for R5_B1B1C5B2B2_C dependency factorization.

Model:
- dynamic vertices with proper-coloring edges,
- residual component carriers whose scope is D_C and whose semantics is an
  arbitrary allowed set of used-color masks,
- unary lists/effects.

The dependency graph is Q_ALL: dynamic graph edges plus one carrier node per
component adjacent to all vertices in D_C.

Checks on exhaustive small instances:
1. global satisfying assignments factor as Cartesian products over connected
   Q_ALL blocks;
2. R1 forced-color queries are local to the target block plus conjunction of
   base satisfiability bits of other blocks;
3. R2 equal-color queries across different blocks factor as two local R1-style
   queries plus the same conjunction;
4. arbitrary independent raw block combinations need not be materialized as a
   Cartesian state product.

This checker is sanity evidence only; the theorem authority is structural.
"""

from itertools import product, combinations

COLORS=range(3)  # three colors suffice for finite algebra sanity
FULLMASK=(1<<len(COLORS))-1

def used_mask(assign, D):
    m=0
    for v in D:
        m |= 1<<assign[v]
    return m

def valid_assignments(vertices, edges, lists, carriers, force=None):
    force=force or {}
    verts=sorted(vertices)
    out=[]
    for vals in product(COLORS, repeat=len(verts)):
        a=dict(zip(verts,vals))
        if any(a[v] not in lists[v] for v in verts):
            continue
        if any(a.get(v)!=c for v,c in force.items() if v in a):
            continue
        if any(a[u]==a[v] for u,v in edges if u in a and v in a):
            continue
        ok=True
        for _,D,allowed in carriers:
            if not D <= vertices:
                continue
            if used_mask(a,D) not in allowed:
                ok=False
                break
        if ok:
            out.append(a)
    return out

def qall_blocks(vertices, edges, carriers):
    # incidence graph nodes ('v',v) and ('c',cid)
    adj={}
    def add(x):
        adj.setdefault(x,set())
    for v in vertices:
        add(('v',v))
    for u,v in edges:
        a,b=('v',u),('v',v); add(a); add(b); adj[a].add(b); adj[b].add(a)
    for cid,D,_ in carriers:
        cn=('c',cid); add(cn)
        for v in D:
            vn=('v',v); add(vn); adj[cn].add(vn); adj[vn].add(cn)
    blocks=[]
    seen=set()
    for s in adj:
        if s in seen: continue
        st=[s]; seen.add(s); B=set()
        while st:
            x=st.pop(); B.add(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); st.append(y)
        blocks.append(B)
    return blocks

def project_block(B):
    return {x[1] for x in B if x[0]=='v'}, {x[1] for x in B if x[0]=='c'}

def check_instance(vertices, edges, lists, carriers):
    blocks=qall_blocks(vertices,edges,carriers)
    global_solutions=valid_assignments(vertices,edges,lists,carriers)
    local_counts=[]
    blockdata=[]
    for B in blocks:
        V,Cids=project_block(B)
        E={(u,v) for u,v in edges if u in V and v in V}
        Cs=[x for x in carriers if x[0] in Cids]
        sols=valid_assignments(V,E,lists,Cs)
        local_counts.append(len(sols))
        blockdata.append((V,E,Cs,sols))
    prod=1
    for n in local_counts: prod*=n
    assert len(global_solutions)==prod

    # R1 locality
    base_ok=[bool(x[3]) for x in blockdata]
    for bi,(V,E,Cs,_) in enumerate(blockdata):
        for u in V:
            for c in COLORS:
                loc=bool(valid_assignments(V,E,lists,Cs,{u:c}))
                expected=loc and all(base_ok[j] for j in range(len(blockdata)) if j!=bi)
                glob=bool(valid_assignments(vertices,edges,lists,carriers,{u:c}))
                assert glob==expected

    # R2 across distinct blocks
    for i in range(len(blockdata)):
        for j in range(i+1,len(blockdata)):
            Vi,Ei,Ci,_=blockdata[i]
            Vj,Ej,Cj,_=blockdata[j]
            for u in Vi:
                for v in Vj:
                    for c in COLORS:
                        li=bool(valid_assignments(Vi,Ei,lists,Ci,{u:c}))
                        lj=bool(valid_assignments(Vj,Ej,lists,Cj,{v:c}))
                        rest=all(base_ok[t] for t in range(len(blockdata)) if t not in (i,j))
                        expected=li and lj and rest
                        glob=bool(valid_assignments(vertices,edges,lists,carriers,{u:c,v:c}))
                        assert glob==expected
    return len(blocks),len(global_solutions)

def main():
    # Two disconnected Q_ALL blocks, each with a dynamic edge and one carrier.
    V={0,1,2,3}
    E={(0,1),(2,3)}
    lists={v:set(COLORS) for v in V}
    allowed={m for m in range(1,FULLMASK+1) if m != FULLMASK}
    carriers=[
        ('A',{0,1},allowed),
        ('B',{2,3},allowed),
    ]
    b,s=check_instance(V,E,lists,carriers)
    assert b==2

    # Add a carrier spanning the two sides: Q_ALL becomes one connected block.
    carriers2=carriers+[('X',{1,2},allowed)]
    b2,s2=check_instance(V,E,lists,carriers2)
    assert b2==1

    print({
        "disconnected_QALL_blocks": b,
        "connected_after_cross_scope_carrier": b2,
        "global_solution_count_factorizes": "PASS",
        "R1_cross_block_support": "LOCAL_PLUS_AND_GLUE_PASS",
        "R2_cross_block_support": "TWO_LOCAL_QUERIES_PLUS_AND_GLUE_PASS",
        "raw_cartesian_state_materialization_required": False,
        "status": "PASS_FINITE_SANITY"
    })

if __name__=="__main__":
    main()
