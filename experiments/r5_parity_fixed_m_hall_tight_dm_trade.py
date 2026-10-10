#!/usr/bin/env python3
"""Replay the fixed-M Hall-tight / DM trade characterization on the frozen 18x18 control."""

from collections import Counter, deque


def build_control(r=6):
    offsets=(0,1,3)
    edges=[]
    factors=[]
    for off in offsets:
        f=[]
        for i in range(r):
            e=(i,(i+off)%r)
            assert e not in edges
            edges.append(e); f.append(e)
        factors.append(f)
    eid={e:i for i,e in enumerate(edges)}
    al={i:[] for i in range(r)}
    ar={j:[] for j in range(r)}
    for e in edges:
        i,j=e
        al[i].append(eid[e]); ar[j].append(eid[e])
    H=[tuple(al[i]) for i in range(r)]+[tuple(ar[j]) for j in range(r)]
    for f in factors:
        f=sorted(f)
        for a in range(0,r,3):
            H.append(tuple(eid[e] for e in f[a:a+3]))
    assert len(H)==len(edges)==18
    return H


def fixed_m(H,r=6):
    inc=[[] for _ in range(len(H))]
    for e,h in enumerate(H):
        for c in h:
            inc[c].append(e)
    residual=list(range(r,len(H)))
    rid={e:i for i,e in enumerate(residual)}
    redges=[]
    label=[]
    kneigh=[set() for _ in residual]
    block_neigh=[set() for _ in range(r)]
    for xs in inc:
        m=[e for e in xs if e<r]
        q=[e for e in xs if e>=r]
        assert len(m)==1 and len(q)==2
        mm=m[0]
        u,v=rid[q[0]],rid[q[1]]
        redges.append(tuple(sorted((u,v))))
        label.append(mm)
        kneigh[u].add(mm); kneigh[v].add(mm)
        block_neigh[mm].update((u,v))
    assert all(len(x)==3 for x in kneigh)
    assert all(len(x)==6 for x in block_neigh)
    return redges,kneigh,block_neigh


def independent(redges,S):
    S=set(S)
    return all(not (u in S and v in S) for u,v in redges)


def N(kneigh,S):
    out=set()
    for u in S:
        out.update(kneigh[u])
    return out


def connected_K(kneigh,S,P):
    S=set(S); P=set(P)
    if not S:
        return False
    root=("L",next(iter(S)))
    seen={root}; q=deque([root])
    while q:
        side,x=q.popleft()
        if side=="L":
            nxt=[("R",m) for m in kneigh[x] if m in P]
        else:
            nxt=[("L",u) for u in S if x in kneigh[u]]
        for z in nxt:
            if z not in seen:
                seen.add(z); q.append(z)
    return len(seen)==len(S)+len(P)


def main():
    H=build_control()
    redges,kneigh,block_neigh=fixed_m(H)
    n=len(kneigh)

    independent_sets=[]
    tight=[]
    for mask in range(1<<n):
        S=frozenset(i for i in range(n) if (mask>>i)&1)
        if not independent(redges,S):
            continue
        independent_sets.append(S)
        surplus=len(N(kneigh,S))-len(S)
        assert surplus>=0
        if surplus==0:
            tight.append(S)

    # Inclusion-minimal nonempty tight sets.
    minimal=[]
    for S in tight:
        if not S:
            continue
        if not any(T and T<S for T in tight):
            minimal.append(S)

    # Minimal tight iff its balanced block is connected and strict Hall holds.
    for S in minimal:
        P=N(kneigh,S)
        assert len(P)==len(S)
        assert connected_K(kneigh,S,P)
        for mask in range(1,(1<<len(S))-1):
            xs=list(S)
            X={xs[i] for i in range(len(xs)) if (mask>>i)&1}
            assert len(N(kneigh,X))>len(X)

    # Every tight set decomposes as disjoint minimal connected components.
    for S in tight:
        if not S:
            continue
        P=N(kneigh,S)
        # Every touched block has exactly three selected neighbours.
        for m in P:
            d=sum(m in kneigh[u] for u in S)
            assert d==3

    # Compatible-trade uncrossing on all pairs of tight sets.
    for A in tight:
        for B in tight:
            U=A|B
            I=A&B
            if independent(redges,U):
                assert U in tight
                assert I in tight

    # Distinct minimal compatible trades are disjoint on both shores.
    compatible_pairs=0
    incompatible_pairs=0
    for i,A in enumerate(minimal):
        for B in minimal[i+1:]:
            if independent(redges,A|B):
                compatible_pairs+=1
                assert not (A&B)
                assert not (N(kneigh,A)&N(kneigh,B))
            else:
                incompatible_pairs+=1

    print("INDEPENDENT_SETS =",len(independent_sets))
    print("HALL_TIGHT_TRADE_UNIONS =",len(tight))
    print("CONNECTED_MINIMAL_DM_TRADES =",len(minimal))
    print("MINIMAL_TRADE_VOLUMES =",dict(sorted(Counter(map(len,minimal)).items())))
    print("STRICT_HALL_ON_EVERY_MINIMAL_TRADE = PASS")
    print("COMPATIBLE_TRADE_UNCROSSING = PASS")
    print("COMPATIBLE_MINIMAL_PAIRS =",compatible_pairs)
    print("INCOMPATIBLE_MINIMAL_PAIRS =",incompatible_pairs)
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
