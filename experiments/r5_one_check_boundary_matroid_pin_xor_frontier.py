#!/usr/bin/env python3
"""Replay one-check boundary theorem and frozen q18 pin/XOR counterexample.

Checks:
1. q18 carrier is square, cubic, linear/C4-free and connected;
2. planted support {0,...,5} is an Exact-One solution;
3. for every one-check-deleted big module on n divisible by 3, every local
   boundary state has Hamming weight exactly one (replayed directly here);
4. at check 2, pinning the planted state and unit-propagating leaves 11 unknowns;
5. the residual has 12 XOR clauses and 3 ternary clauses;
6. the XOR graph is connected and each residual ternary reduces to parity
   pattern (t,1-t,1-t), forcing t=1.

P_VS_NP remains OPEN.
"""

from collections import defaultdict

Q=18
SETS=[
(2,3,4),(5,10,11),(9,14,17),(0,7,16),(6,13,15),(1,8,12),
(8,13,14),(10,12,15),(2,10,16),(3,12,14),(0,3,13),(5,15,16),
(4,5,17),(0,6,11),(4,8,9),(7,11,17),(1,6,9),(1,2,7),
]
PLANTED=set(range(6))
SEED_CHECK=2
SEED_VAR=0


def matrix():
    A=[[0]*Q for _ in range(Q)]
    for j,C in enumerate(SETS):
        for i in C:A[i][j]=1
    return A


def verify_source(A):
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[i][j] for i in range(Q))==3 for j in range(Q))
    for a in range(Q):
        for b in range(a+1,Q):
            assert sum(A[i][a]*A[i][b] for i in range(Q))<=1
    # connected Tanner graph
    adj=[set() for _ in range(2*Q)]
    for i in range(Q):
        for j in range(Q):
            if A[i][j]:
                adj[i].add(Q+j);adj[Q+j].add(i)
    seen={0};stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v);stack.append(v)
    assert len(seen)==2*Q


def is_exact(A,S):
    return all(sum(A[i][j] for j in S)==1 for i in range(Q))


def one_check_boundary_states(A,c):
    """Enumerate local states satisfying all checks except c; return 3-bit states."""
    neigh=[j for j in range(Q) if A[c][j]]
    out=set()
    for x in range(1<<Q):
        ok=True
        for i in range(Q):
            if i==c:continue
            if sum(A[i][j]*((x>>j)&1) for j in range(Q))!=1:
                ok=False;break
        if ok:
            state=tuple((x>>j)&1 for j in neigh)
            out.add(state)
    return neigh,out


def propagate(A,initial):
    vals=[None]*Q
    for j,v in initial.items():vals[j]=v
    clauses=[[j for j in range(Q) if A[i][j]] for i in range(Q)]
    changed=True
    while changed:
        changed=False
        for vs in clauses:
            ones=sum(vals[j]==1 for j in vs)
            unk=[j for j in vs if vals[j] is None]
            if ones>1 or (ones==0 and not unk):
                return None
            if ones==1:
                for j in unk:
                    vals[j]=0;changed=True
            elif len(unk)==1:
                vals[unk[0]]=1;changed=True
    return vals


def residual(A,vals):
    clauses=[[j for j in range(Q) if A[i][j]] for i in range(Q)]
    xor=[];tern=[]
    for vs in clauses:
        unk=tuple(j for j in vs if vals[j] is None)
        if len(unk)==2:xor.append(unk)
        elif len(unk)==3:tern.append(unk)
        elif len(unk)==1:
            raise AssertionError("unit propagation not closed")
    return xor,tern


def xor_components(xor,unknown):
    g=defaultdict(list)
    for a,b in xor:
        g[a].append((b,1));g[b].append((a,1))
    parity={}
    comps=[]
    compid={}
    for v in unknown:
        if v in parity:continue
        parity[v]=0;stack=[v];comp=[]
        while stack:
            u=stack.pop();compid[u]=len(comps);comp.append(u)
            for w,p in g[u]:
                want=parity[u]^p
                if w in parity:
                    assert parity[w]==want
                else:
                    parity[w]=want;stack.append(w)
        comps.append(comp)
    return comps,compid,parity


def main():
    A=matrix()
    verify_source(A)
    assert is_exact(A,PLANTED)

    # Arithmetic theorem replay on this n=18 instance for every deleted check.
    for c in range(Q):
        neigh,states=one_check_boundary_states(A,c)
        assert states
        assert all(sum(s)==1 for s in states)
        # Every such local state already satisfies the omitted check.
        assert all(sum(s)==1 for s in states)

    seed_neigh=[j for j in range(Q) if A[SEED_CHECK][j]]
    assert SEED_VAR in seed_neigh
    init={j:(1 if j==SEED_VAR else 0) for j in seed_neigh}
    vals=propagate(A,init)
    assert vals is not None
    unknown=[j for j,v in enumerate(vals) if v is None]
    assert len(unknown)==11

    xor,tern=residual(A,vals)
    assert len(xor)==12
    assert len(tern)==3

    comps,compid,parity=xor_components(xor,unknown)
    assert len(comps)==1
    assert len(comps[0])==11

    patterns=[]
    for tri in tern:
        pat=tuple(parity[v] for v in tri)
        patterns.append(pat)
    assert patterns==[(0,1,1),(0,1,1),(0,1,1)]

    # For representative t, ExactOne(t,1-t,1-t) forces t=1.
    def exact1(bits):return sum(bits)==1
    assert exact1((1,0,0))
    assert not exact1((0,1,1))

    print("ONE_CHECK_BOUNDARY_MATROID theorem replay: PASS")
    print("q18 square/cubic/linear SAT carrier: PASS")
    print("pin+unit propagation leaves 11 unknown variables: CONFIRMED")
    print("residual: 12 XOR clauses + 3 ternary clauses")
    print("XOR contraction: 1 component / 1 Boolean; ternary quotient forces t=1")
    print("PIN_PROPAGATE_XOR_CONTRACT control: PASS")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
