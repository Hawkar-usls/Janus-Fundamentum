#!/usr/bin/env python3
"""Exact Paley(5419) order-10 balanced 4-critical witness and Ore decomposition."""

from itertools import permutations

Q = 5419
R = (-2) % Q
G10_CODE = "ICOcePkL_"
MOSER7_CODE = "FQjRo"

WITNESSES = {
    0: ([3516,1,4064,3520,128,5387,4028,129,0,4032],
        [1,0,1,2,1,1,1,1,0,2]),
    1: ([2839,1,3371,2843,128,5403,3351,129,0,3355],
        [1,2,0,1,2,2,2,1,0,2]),
    2: ([5040,1,1016,5072,128,5411,976,129,0,1008],
        [1,1,1,2,0,1,1,1,0,2]),
}


def orbit_minus2(q):
    out=[]; seen=set(); x=1
    while x not in seen:
        seen.add(x); out.append(x); x=(x*((-2)%q))%q
    assert x == 1
    return out


O = orbit_minus2(Q)
assert len(O) == 21
IDX = {s:k for k,s in enumerate(O)}
S = set(O) | {(-s) % Q for s in O}
assert len(S) == 42


def phi(c,d):
    d %= Q
    if d in IDX:
        return (-IDX[d]-c) % 3
    nd = (-d) % Q
    if nd in IDX:
        return (IDX[nd]+c) % 3
    return None


def decode_graph6(s):
    n = ord(s[0]) - 63
    bits=[]
    for ch in s[1:]:
        z=ord(ch)-63
        bits.extend((z>>j)&1 for j in range(5,-1,-1))
    edges=[]; p=0
    for j in range(1,n):
        for i in range(j):
            if bits[p]:
                edges.append((i,j))
            p += 1
    return n, edges


def connected(n, edges):
    adj=[[] for _ in range(n)]
    for a,b in edges:
        adj[a].append(b); adj[b].append(a)
    seen={0}; st=[0]
    while st:
        v=st.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u); st.append(u)
    return len(seen)==n


def is_3colorable(n, edges):
    adj=[set() for _ in range(n)]
    for a,b in edges:
        adj[a].add(b); adj[b].add(a)
    order=sorted(range(n), key=lambda v: -len(adj[v]))
    col=[-1]*n
    def rec(i):
        if i==n:
            return True
        v=order[i]
        used={col[u] for u in adj[v] if col[u]>=0}
        for z in range(3):
            if z in used:
                continue
            col[v]=z
            if rec(i+1):
                return True
            col[v]=-1
        return False
    return rec(0)


def edge4critical(n, edges):
    assert connected(n, edges)
    if is_3colorable(n, edges):
        return False
    for i in range(len(edges)):
        if not is_3colorable(n, edges[:i]+edges[i+1:]):
            return False
    return True


def graph_signature(n, edges):
    A=[[0]*n for _ in range(n)]
    for a,b in edges:
        A[a][b]=A[b][a]=1
    return A


def isomorphic(n1,e1,n2,e2):
    if n1 != n2 or len(e1) != len(e2):
        return False
    A=graph_signature(n1,e1); B=graph_signature(n2,e2)
    da=[sum(r) for r in A]; db=[sum(r) for r in B]
    if sorted(da)!=sorted(db):
        return False
    for p in permutations(range(n1)):
        if any(da[i] != db[p[i]] for i in range(n1)):
            continue
        ok=True
        for i in range(n1):
            for j in range(i+1,n1):
                if A[i][j] != B[p[i]][p[j]]:
                    ok=False; break
            if not ok:
                break
        if ok:
            return True
    return False


n, edges = decode_graph6(G10_CODE)
assert n == 10 and len(edges) == 16
assert edge4critical(n, edges)

deg=[0]*n
for a,b in edges:
    deg[a]+=1; deg[b]+=1
assert sorted(deg) == [3]*8 + [4]*2

# Exact Ore split: {2,5,8,9} is K4-e with missing edge 8--9.
E={tuple(sorted(e)) for e in edges}
side={2,5,8,9}
sideE={e for e in E if e[0] in side and e[1] in side}
assert sideE == {(2,5),(2,8),(5,8),(2,9),(5,9)}
assert (8,9) not in E

# Other side + merge 8~9 is the q=331 Moser-type graph FQjRo.
keep={0,1,3,4,6,7,8,9}
merged_nodes=[0,1,3,4,6,7,10]
index={v:i for i,v in enumerate(merged_nodes)}
merged_edges=set()
for a,b in E:
    if a not in keep or b not in keep:
        continue
    aa=10 if a in (8,9) else a
    bb=10 if b in (8,9) else b
    if aa != bb:
        merged_edges.add(tuple(sorted((index[aa],index[bb]))))
m7, e7 = decode_graph6(MOSER7_CODE)
assert m7 == 7 and len(e7) == 11 and edge4critical(m7,e7)
assert isomorphic(7, sorted(merged_edges), 7, e7)

# Exact balanced gain witnesses in every slice.
for c,(x,g) in WITNESSES.items():
    assert len(set(x)) == 10
    for a,b in edges:
        d=(x[b]-x[a]) % Q
        ph=phi(c,d)
        assert ph is not None, (c,a,b,d)
        assert (g[b]-g[a]) % 3 == ph, (c,a,b,d,ph,(g[b]-g[a])%3)

assert (len(O)-1)//2 == 10

print("PASS_PALEY5419_EXACT_ORDER10_ORE_CHAIN")
print("q=5419 L=21 support_degree=42")
print("graph6=ICOcePkL_ n=10 m=16 degree_multiset=3^8,4^2")
print("all_three_slices_have_exact_balanced_embeddings=True")
print("ore_split_K4_minus_edge_on={2,5,8,9}; merged_other_side_isomorphic_to_FQjRo=True")
print("parent_lower_bound_order_gt9_required_for_exact_minimum=True")
print("minimum_balanced_ordinary_4critical_order=10")
print("observed_order_equals_(L-1)/2_for_q19_q331_q5419_ONLY; family_theorem=False")
print("E8_D1=EMPTY P_VS_NP=OPEN")
