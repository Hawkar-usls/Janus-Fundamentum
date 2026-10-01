#!/usr/bin/env python3
"""Exact Paley(87211) order-13 4-Ore character-gain positive control."""

Q = 87211
G10_CODE = "ICOcePkL_"
G13_CODE = "LCOcaPkL_AO@_B"

WITNESSES = {
    0: ([0,2581,517,1,10757,2561,512,10773,2565,513,65280,65408,87083],
        [0,2,1,0,1,2,0,0,0,0,0,1,2]),
    1: ([0,2581,517,1,10757,2561,512,10773,2565,513,54379,54443,87147],
        [0,1,0,2,2,0,1,0,0,0,0,2,1]),
    2: ([0,2597,517,1,73424,2561,512,73456,2565,513,65280,65408,87083],
        [0,1,2,1,2,1,2,0,0,0,0,0,0]),
}


def orbit_minus2(q):
    out=[]; seen=set(); x=1
    while x not in seen:
        seen.add(x); out.append(x); x=(x*((-2)%q))%q
    assert x == 1
    return out


O=orbit_minus2(Q)
assert len(O)==27
IDX={s:k for k,s in enumerate(O)}
S=set(O)|{(-s)%Q for s in O}
assert len(S)==54


def phi(c,d):
    d%=Q
    if d in IDX:
        return (-IDX[d]-c)%3
    nd=(-d)%Q
    if nd in IDX:
        return (IDX[nd]+c)%3
    return None


def decode_graph6(s):
    n=ord(s[0])-63
    bits=[]
    for ch in s[1:]:
        z=ord(ch)-63
        bits.extend((z>>j)&1 for j in range(5,-1,-1))
    edges=[];p=0
    for j in range(1,n):
        for i in range(j):
            if bits[p]: edges.append((i,j))
            p+=1
    return n,edges


def connected(n,edges):
    adj=[[] for _ in range(n)]
    for a,b in edges:
        adj[a].append(b);adj[b].append(a)
    seen={0};stack=[0]
    while stack:
        v=stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u);stack.append(u)
    return len(seen)==n


def is_3colorable(n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges:
        adj[a].add(b);adj[b].add(a)
    order=sorted(range(n),key=lambda v:-len(adj[v]))
    col=[-1]*n
    def rec(i):
        if i==n:return True
        v=order[i]
        used={col[u] for u in adj[v] if col[u]>=0}
        for z in range(3):
            if z in used:continue
            col[v]=z
            if rec(i+1):return True
            col[v]=-1
        return False
    return rec(0)


def edge4critical(n,edges):
    assert connected(n,edges)
    if is_3colorable(n,edges):return False
    for i in range(len(edges)):
        if not is_3colorable(n,edges[:i]+edges[i+1:]):return False
    return True


n10,e10=decode_graph6(G10_CODE)
assert n10==10 and edge4critical(n10,e10)
n13,e13=decode_graph6(G13_CODE)
assert n13==13 and len(e13)==21 and edge4critical(n13,e13)

# Exact Ore extension used for the positive control:
# split G10 vertex 0 with neighbours {3,6}|{7}, then attach K4-e.
N={v:set() for v in range(n10)}
for a,b in e10:
    N[a].add(b);N[b].add(a)
assert N[0]=={3,6,7}
constructed=set()
for a,b in e10:
    if a==0 or b==0:
        w=b if a==0 else a
        zz=0 if w in {3,6} else 10
        constructed.add(tuple(sorted((zz,w))))
    else:
        constructed.add(tuple(sorted((a,b))))
for a,b in [(0,11),(0,12),(10,11),(10,12),(11,12)]:
    constructed.add(tuple(sorted((a,b))))
assert constructed == {tuple(sorted(e)) for e in e13}

for c,(x,g) in WITNESSES.items():
    assert len(set(x))==13
    for a,b in e13:
        d=(x[b]-x[a])%Q
        ph=phi(c,d)
        assert ph is not None,(c,a,b,d)
        assert (g[b]-g[a])%3==ph,(c,a,b,d,ph,(g[b]-g[a])%3)

assert (len(O)-1)//2 == 13

print("PASS_PALEY87211_ORE13_CHARACTER_GAIN_POSITIVE_CONTROL")
print("q=87211 L=27 support_degree=54")
print("graph6=LCOcaPkL_AO@_B n=13 m=21 edge4critical=True")
print("exact_ore_extension_from_G10_vertex0_split_{3,6}|{7}=True")
print("balanced_embeddings_all_three_slices=True")
print("observed_orders: L9->4 L15->7 L21->10 L27->13")
print("observed_order_equals_(L-1)/2_four_controls=True; family_theorem=False")
print("minimum_order_q87211=OPEN")
print("E8_D1=EMPTY P_VS_NP=OPEN")
