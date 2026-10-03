#!/usr/bin/env python3
"""Exact controls for R5 E51 complementary two-claw permutation propagation.

The 3x3 toroidal carrier has exactly two complementary claws at every conflict
vertex. E51 converts every conflict edge into a permutation of the three local
states C,0,1 and propagates from one root. Exactly three consistent global state
assignments are obtained, matching the three Exact-One witnesses.

P_VS_NP remains OPEN.
"""
from itertools import combinations


def rows_torus3():
    k=3
    def vid(i,j): return (i%k)*k+(j%k)
    return [
        {vid(i,j),vid(i+1,j),vid(i,j+1)}
        for i in range(k) for j in range(k)
    ]

ROWS=rows_torus3()
N=9


def conflict_graph():
    adj=[set() for _ in range(N)]
    for r in ROWS:
        for a,b in combinations(r,2):
            adj[a].add(b); adj[b].add(a)
    assert all(len(x)==6 for x in adj)
    return adj


def claws(v,adj):
    return [set(t) for t in combinations(sorted(adj[v]),3)
            if all(b not in adj[a] for a,b in combinations(t,2))]


def canonical_sides(v,adj):
    c=claws(v,adj)
    assert len(c)==2
    assert c[0].isdisjoint(c[1])
    assert c[0] | c[1] == adj[v]
    c=sorted(c,key=lambda s:tuple(sorted(s)))
    return c[0],c[1]


def edge_map(v,u,sides):
    # states encoded 0=C, 1=side0, 2=side1
    a = 0 if u in sides[v][0] else 1
    b = 0 if v in sides[u][0] else 1
    # C_v -> side b at u; side a at v -> C_u; other side -> other side.
    out={0:1+b, 1+a:0, 1+(1-a):1+(1-b)}
    assert set(out)=={0,1,2} and set(out.values())=={0,1,2}
    return out


def propagate(root_state,adj,sides):
    state=[None]*N
    state[0]=root_state
    stack=[0]
    while stack:
        v=stack.pop()
        for u in adj[v]:
            want=edge_map(v,u,sides)[state[v]]
            if state[u] is None:
                state[u]=want; stack.append(u)
            elif state[u]!=want:
                return None
    return state


def witness_from_states(state):
    return {v for v,s in enumerate(state) if s==0}


def brute_witnesses():
    out=[]
    for S in combinations(range(N),N//3):
        S=set(S)
        if all(len(S&r)==1 for r in ROWS): out.append(S)
    return out


def main():
    adj=conflict_graph()
    sides=[canonical_sides(v,adj) for v in range(N)]
    states=[]
    witnesses=[]
    for root in range(3):
        st=propagate(root,adj,sides)
        assert st is not None
        S=witness_from_states(st)
        assert len(S)==N//3
        assert all(len(S&r)==1 for r in ROWS)
        states.append(st); witnesses.append(S)

    brute=brute_witnesses()
    assert {frozenset(S) for S in witnesses} == {frozenset(S) for S in brute}
    assert len(brute)==3

    print("R5 E51 complementary two-claw permutation propagation: PASS")
    print("all_vertices_have_exactly_two_complementary_claws=True")
    print("consistent_root_states=3")
    print("witnesses=", [sorted(S) for S in witnesses])


if __name__ == "__main__":
    main()
