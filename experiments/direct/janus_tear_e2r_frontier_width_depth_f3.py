#!/usr/bin/env python3
"""Provider replay for C025-E2R-L1G-F3 finite representation mechanics."""
from dataclasses import dataclass
from itertools import product
from math import log
Clause=frozenset[int]
@dataclass(frozen=True)
class Gate: var:int; left:int; right:int

def taut(c): return any(-x in c for x in c)
def or_cnf(a,b):
    out=set()
    for x in a:
        for y in b:
            c=frozenset(x|y)
            if not taut(c): out.add(c)
    return out

def analyze(local,gates):
    known=set(local); gm={}; pos={v:{frozenset({v})} for v in local}; neg={v:{frozenset({-v})} for v in local}; depth={v:0 for v in local}
    for g in gates:
        assert g.var not in known and abs(g.left) in known and abs(g.right) in known
        gm[g.var]=g
        E=lambda lit: pos[abs(lit)] if lit>0 else neg[abs(lit)]
        EN=lambda lit: neg[abs(lit)] if lit>0 else pos[abs(lit)]
        pos[g.var]=set(E(g.left))|set(E(g.right)); neg[g.var]=or_cnf(set(EN(g.left)),set(EN(g.right)))
        ds=[]
        for lit in (g.left,g.right):
            u=abs(lit); ds.append(0 if u in local else depth[u]+(1 if lit<0 else 0))
        depth[g.var]=max(ds); known.add(g.var)
    def cone(v):
        if v in local:return set()
        out={v}; g=gm[v]
        for lit in (g.left,g.right):
            u=abs(lit)
            if u not in local: out|=cone(u)
        return out
    def frontier(v):
        out=set(); stack=[v]; seen=set()
        while stack:
            p=stack.pop()
            if p in seen or p in local: continue
            seen.add(p); g=gm[p]
            for lit in (g.left,g.right):
                u=abs(lit)
                if u in local: continue
                if lit<0: out.add((p,u))
                else: stack.append(u)
        return out
    bw={v:max((len(frontier(u)) for u in cone(v)),default=0) for v in gm}
    return pos,neg,depth,bw

def family(k):
    local=set(range(1,2*k+1)); gates=[]; nxt=2*k+1; gs=[]
    for j in range(k):
        g=nxt;nxt+=1;gates.append(Gate(g,2*j+1,2*j+2));gs.append(g)
    out=nxt;nxt+=1;gates.append(Gate(out,-gs[0],-gs[1]))
    for j in range(2,k):
        new=nxt;nxt+=1;gates.append(Gate(new,out,-gs[j]));out=new
    return local,gates,out

def within(count,S,b,d):
    if count<=1:return True
    return log(count) <= ((b+2)**(d+1))*log(S)+1e-12

def main():
    for k in range(2,9):
        local,gates,out=family(k);pos,neg,d,b=analyze(local,gates)
        assert d[out]==1 and b[out]==k and len(pos[out])==k and len(neg[out])==2**k and len(gates)==2*k-1
    local={1,2,3,4}
    for s5,s6,s5b in product((-1,1),repeat=3):
        gates=[Gate(5,1,-2),Gate(6,s5*5,3),Gate(7,s6*6,s5b*5)]
        pos,neg,d,b=analyze(local,gates);S=len(local)+3*len(gates)
        for v in (5,6,7):
            assert within(len(pos[v]),S,b[v],d[v]);assert within(len(neg[v]),S,b[v],d[v])
    gates=[Gate(6,1,-2),Gate(7,6,3),Gate(8,7,-4),Gate(9,8,5)]
    pos,neg,d,b=analyze({1,2,3,4,5},gates)
    assert d[9]==0 and b[9]==0 and len(pos[9])==5 and len(neg[9])==1
    print('C025_E2R_L1G_F3_NEGATIVE_DEPTH_METRIC = PASS')
    print('C025_E2R_L1G_F3_FRONTIER_WIDTH_METRIC = PASS')
    print('C025_E2R_L1G_F3_DEPTH_ONE_EXPONENTIAL_FRONTIER = PASS')
    print('C025_E2R_L1G_F3_DEPTH_ALONE_POLY_ROUTE = REFUTED')
    print('C025_E2R_L1G_F3_BD_REPRESENTATION_BOUND_FINITE = PASS')
    print('C025_E2R_L1G_F3_Q0_MONOTONE_BASE = PASS')
    print('claim_boundary = representation mechanics only; proof-level bd cut elimination and NW restriction survival remain open')
if __name__=='__main__':main()
