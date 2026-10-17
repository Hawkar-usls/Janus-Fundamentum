from collections import deque
from itertools import product


def undirected(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def cycle_edges(cycle):
    return [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]


def spanning_tree(n, edges):
    adj = [[] for _ in range(n)]
    for e in edges:
        u, v = e
        adj[u].append((v, e)); adj[v].append((u, e))
    seen = {0}; q = deque([0]); tree = set()
    while q:
        u = q.popleft()
        for v, e in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v); tree.add(e)
    assert len(seen) == n
    return tree


def tree_path(tree, n, s, t):
    adj = [[] for _ in range(n)]
    for u, v in tree:
        adj[u].append(v); adj[v].append(u)
    prev = {s: None}; q = deque([s])
    while q:
        u = q.popleft()
        if u == t: break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u; q.append(v)
    out = []; cur = t
    while prev[cur] is not None:
        p = prev[cur]; out.append((p, cur)); cur = p
    return list(reversed(out))


def fundamental_cycle_matrix(n, edges):
    edges = sorted(undirected(e) for e in edges)
    idx = {e:i for i,e in enumerate(edges)}
    tree = spanning_tree(n, edges)
    rows = []
    for chord in edges:
        if chord in tree: continue
        u, v = chord
        row = [0]*len(edges); row[idx[chord]] = 1
        for a, b in tree_path(tree, n, v, u):
            e = undirected((a,b))
            row[idx[e]] = 1 if e == (a,b) else 2
        rows.append(tuple(row))
    assert len(rows) == len(edges)-n+1
    return rows


def mat_vec(lam, Q):
    return tuple(sum(lam[i]*Q[i][j] for i in range(len(Q))) % 3 for j in range(len(Q[0])))


def signed_scalar_image(coeffs):
    image = {0}
    for a in coeffs:
        image = {(x + a*s) % 3 for x in image for s in (1,2)}
    return image


def check_graph(n, edges):
    Q = fundamental_cycle_matrix(n, edges)
    beta = len(Q)
    assert beta > 0
    checked = 0
    for lam in product(range(3), repeat=beta):
        if not any(lam): continue
        a = mat_vec(lam, Q)
        support = [x for x in a if x]
        assert len(support) >= 2
        assert signed_scalar_image(a) == {0,1,2}
        checked += 1
    return checked


def graph_from_cycles(H, Fs):
    edges = set()
    for cyc in [H]+Fs:
        for e in cycle_edges(cyc):
            ue = undirected(e)
            assert ue not in edges
            edges.add(ue)
    return edges


def main():
    # K4: beta=3, exhaustive all 26 nonzero characters.
    k4 = {(i,j) for i in range(4) for j in range(i+1,4)}
    assert check_graph(4, k4) == 26

    H = list(range(8))
    good = graph_from_cycles(H, [[0,3,1,5],[2,6,4,7]])
    bad  = graph_from_cycles(H, [[0,3,1,6],[2,4,7,5]])
    # beta=9 => 3^9-1 = 19682 nonzero characters each.
    assert check_graph(8, good) == 19682
    assert check_graph(8, bad) == 19682

    print('PASS: every nonzero rank-one graphic syndrome character is surjective on GF(3).')


if __name__ == '__main__':
    main()
