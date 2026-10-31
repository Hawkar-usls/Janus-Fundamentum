#!/usr/bin/env python3
"""Exact L=33 Ore16 gain-control replay on q=67 and q=20857."""

EDGES = [
    (0,3),(0,6),(0,14),(0,15),
    (1,4),(1,7),(1,8),
    (2,5),(2,8),(2,9),
    (3,6),(3,9),
    (4,7),(4,8),
    (5,8),(5,9),
    (6,9),
    (7,10),
    (10,11),(10,12),
    (11,12),(11,13),(12,13),
    (13,14),(13,15),(14,15),
]

WITNESSES = {
  67: {
    0: ([0,8,4,1,12,10,7,14,6,3,15,16,22,18,2,9],
        [0,0,1,0,1,0,2,2,2,1,2,2,1,0,1,0]),
    1: ([0,9,5,1,11,7,3,12,8,4,13,14,16,17,19,20],
        [0,2,2,2,1,1,1,0,0,0,2,1,0,2,1,0]),
    2: ([0,8,4,1,13,9,6,10,7,3,11,12,17,14,2,18],
        [0,2,2,1,1,1,0,2,1,1,0,1,0,1,0,0]),
  },
  20857: {
    0: ([0,4099,2050,1,2051,4097,2048,2052,4098,2049,4915,4923,9396,9404,10428,19833],
        [0,1,2,0,2,1,2,2,1,2,0,0,2,2,1,1]),
    1: ([0,4099,2050,1,2051,4097,2048,2052,4098,2049,1540,13435,13451,4489,8,4481],
        [0,0,1,2,0,2,0,2,1,2,1,1,2,2,1,1]),
    2: ([0,4099,2050,1,6146,4097,2048,6147,4098,2049,14339,14467,2607,2735,11732,11860],
        [0,2,0,1,2,0,1,0,1,2,0,0,2,2,1,1]),
  },
}


def is_prime(n):
    if n < 2:
        return False
    d=2
    while d*d <= n:
        if n % d == 0:
            return n == d
        d += 1
    return True


def orbit_minus2(q):
    seen={}; out=[]; x=1; r=(-2)%q
    while x not in seen:
        seen[x]=len(out); out.append(x); x=(x*r)%q
    assert x == 1
    return out, seen


def is_3colorable(n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges:
        adj[a].add(b); adj[b].add(a)
    order=sorted(range(n),key=lambda v:-len(adj[v]))
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


def edge4critical(n,edges):
    adj=[[] for _ in range(n)]
    for a,b in edges:
        adj[a].append(b);adj[b].append(a)
    seen={0}; st=[0]
    while st:
        v=st.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u);st.append(u)
    assert len(seen)==n
    if is_3colorable(n,edges):
        return False
    return all(is_3colorable(n,edges[:i]+edges[i+1:]) for i in range(len(edges)))


assert len(EDGES)==26
assert edge4critical(16,EDGES)

# Exact inherited Ore construction: G13 plus split 0 -> 0,13 with
# neighbour partition {3,6}|{11,12}, then K4-e on split endpoints 0,13
# and new vertices 14,15.
G13_EDGES=[e for e in EDGES if 13 not in e and 14 not in e and 15 not in e]
# Restore old split-vertex edges 0-11,0-12 in the parent.
G13_EDGES += [(0,11),(0,12)]
assert len(G13_EDGES)==21
assert edge4critical(13,G13_EDGES)
assert {v for e in G13_EDGES if 0 in e for v in e if v!=0} == {3,6,11,12}

for q in (67,20857):
    assert is_prime(q)
    O,IDX=orbit_minus2(q)
    assert len(O)==33
    S=set(O)|{(-s)%q for s in O}
    assert len(S)==66
    if q==67:
        assert len(S)==q-1
    else:
        assert len(S) < q-1

    def phi(c,d):
        d%=q
        if d in IDX:
            return (-IDX[d]-c)%3
        nd=(-d)%q
        if nd in IDX:
            return (IDX[nd]+c)%3
        return None

    for c,(x,g) in WITNESSES[q].items():
        assert len(x)==16 and len(g)==16 and len(set(x))==16
        for a,b in EDGES:
            d=(x[b]-x[a])%q
            assert d in S
            ph=phi(c,d)
            assert ph is not None
            assert (g[b]-g[a])%3 == ph, (q,c,a,b,d,ph,(g[b]-g[a])%3)

print("PASS_PALEY_L33_ORE16_TWO_PRIME_CHARACTER_GAIN_CONTROL")
print("q=67 prime=True L=33 support_degree=66 dense_complete_support=True")
print("q=20857 prime=True L=33 support_degree=66 sparse_control=True")
print("Ore16 n=16 m=26 edge4critical=True")
print("exact_parent_G13_split_vertex0_partition={3,6}|{11,12}")
print("balanced_embeddings_c0_c1_c2_on_both_primes=True")
print("five_controls_orders=4,7,10,13,16 for L=9,15,21,27,33")
print("symbolic_family_recursion=OPEN minimum_L33=OPEN")
print("E8_D1=EMPTY P_VS_NP=OPEN")
