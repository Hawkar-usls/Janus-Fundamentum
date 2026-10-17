#!/usr/bin/env python3
from itertools import product, combinations

COLORS=(0,1,2)


def list_colorable(n, edges, lists):
    adj=[set() for _ in range(n)]
    for u,v in edges:
        adj[u].add(v); adj[v].add(u)
    order=sorted(range(n), key=lambda v:(len(lists[v]),-len(adj[v])))
    col=[None]*n
    def dfs(k):
        if k==n: return True
        v=order[k]
        used={col[w] for w in adj[v] if col[w] is not None}
        for c in lists[v]:
            if c not in used:
                col[v]=c
                if dfs(k+1): return True
                col[v]=None
        return False
    return dfs(0)


def admissible_lists(degrees):
    opts=[]
    for d in degrees:
        choices=[]
        for k in range(max(1,d),4):
            choices += [set(s) for s in combinations(COLORS,k)]
        opts.append(choices)
    return product(*opts)


def check_all_degree_lists(n, edges):
    deg=[0]*n
    for u,v in edges:
        deg[u]+=1; deg[v]+=1
    count=0
    for L in admissible_lists(deg):
        count+=1
        assert list_colorable(n,edges,L), (edges,L)
    return count


def main():
    # Non-Gallai controls: even cycle C4 and K_{2,3}.
    C4=[(0,1),(1,2),(2,3),(3,0)]
    c4_count=check_all_degree_lists(4,C4)
    assert c4_count==4**4  # each degree-2 vertex has one of 3 two-lists or the full list

    K23=[(u,v) for u in (0,1) for v in (2,3,4)]
    k23_count=check_all_degree_lists(5,K23)
    assert k23_count==4**3  # degree-3 side has forced full list; degree-2 side has 4 choices

    # Exact boundary replay for a degree-3 C4 component: one already-coloured outside
    # neighbour per vertex removes at most one colour, leaving a 2-list.
    for boundary_colors in product(COLORS, repeat=4):
        lists=[set(COLORS)-{boundary_colors[v]} for v in range(4)]
        assert all(len(L)==2 for L in lists)
        assert list_colorable(4,C4,lists)

    # Gallai negative controls show why the kernel must stop there.
    C5=[(i,(i+1)%5) for i in range(5)]
    two=[{0,1} for _ in range(5)]
    assert not list_colorable(5,C5,two)

    K3=[(0,1),(1,2),(0,2)]
    assert not list_colorable(3,K3,[{0,1},{0,1},{0,1}])

    print('PASS: non-Gallai degree-list extension controls')
    print('C4 all degree-list assignments:',c4_count)
    print('K2,3 all degree-list assignments:',k23_count)
    print('all 3^4 boundary colourings extend across degree-3 C4 component')
    print('Gallai controls C5 and K3 admit obstructing degree lists')


if __name__=='__main__':
    main()
