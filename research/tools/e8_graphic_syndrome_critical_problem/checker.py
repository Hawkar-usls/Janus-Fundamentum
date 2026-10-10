from collections import deque
from itertools import product


def cycle_edges(cycle):
    return [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]


def undirected(edge):
    a, b = edge
    return (a, b) if a < b else (b, a)


def make_edges(hamiltonian, factor_cycles):
    edges = set()
    for cycle in [hamiltonian] + factor_cycles:
        for edge in cycle_edges(cycle):
            key = undirected(edge)
            assert key not in edges
            edges.add(key)
    return sorted(edges)


def spanning_tree(n, edges):
    adjacency = [[] for _ in range(n)]
    for edge in edges:
        u, v = edge
        adjacency[u].append((v, edge))
        adjacency[v].append((u, edge))
    seen = {0}
    queue = deque([0])
    tree = set()
    while queue:
        u = queue.popleft()
        for v, edge in adjacency[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
                tree.add(edge)
    assert len(seen) == n and len(tree) == n - 1
    return tree


def tree_path(tree, n, start, goal):
    adjacency = [[] for _ in range(n)]
    for u, v in tree:
        adjacency[u].append(v)
        adjacency[v].append(u)
    prev = {start: None}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == goal:
            break
        for v in adjacency[u]:
            if v not in prev:
                prev[v] = u
                queue.append(v)
    assert goal in prev
    reverse_path = []
    cur = goal
    while prev[cur] is not None:
        parent = prev[cur]
        reverse_path.append((parent, cur))
        cur = parent
    return list(reversed(reverse_path))


def fundamental_cycle_matrix(n, edges):
    tree = spanning_tree(n, edges)
    edge_index = {edge: i for i, edge in enumerate(edges)}
    rows = []
    for chord in edges:
        if chord in tree:
            continue
        u, v = chord
        row = [0] * len(edges)
        row[edge_index[chord]] = 1
        for a, b in tree_path(tree, n, v, u):
            edge = undirected((a, b))
            row[edge_index[edge]] = 1 if edge == (a, b) else 2
        rows.append(tuple(row))
    assert len(rows) == len(edges) - n + 1
    return rows


def syndromes(Q):
    m = len(Q[0])
    return {
        tuple(sum(row[j] * signs[j] for j in range(m)) % 3 for row in Q)
        for signs in product((1, 2), repeat=m)
    }


def add(a, b):
    return tuple((x + y) % 3 for x, y in zip(a, b))


def scale(c, a):
    return tuple((c * x) % 3 for x in a)


def span(basis):
    d = len(basis[0]) if basis else 0
    return {
        tuple(sum(coeffs[i] * basis[i][j] for i in range(len(basis))) % 3 for j in range(d))
        for coeffs in product(range(3), repeat=len(basis))
    }


def projective(v):
    for x in v:
        if x:
            inv = 1 if x == 1 else 2
            return scale(inv, v)
    raise ValueError("zero has no projective representative")


def no_projective_line(allowed_nonzero_projective):
    points = sorted(allowed_nonzero_projective)
    for i, a in enumerate(points):
        for b in points[i + 1:]:
            line = {
                projective(a),
                projective(b),
                projective(add(a, b)),
                projective(add(a, scale(2, b))),
            }
            if len(line) == 4 and line <= allowed_nonzero_projective:
                return False, line
    return True, None


def main():
    n = 8
    hamiltonian = list(range(n))
    zero = (0,) * 9
    universe = set(product(range(3), repeat=9))

    bad_edges = make_edges(hamiltonian, [[0, 3, 1, 6], [2, 4, 7, 5]])
    bad_Q = fundamental_cycle_matrix(n, bad_edges)
    bad_S = syndromes(bad_Q)
    assert len(bad_Q) == 9
    assert len(bad_S) == 18550
    assert zero not in bad_S

    safe_basis = [
        (0, 0, 0, 0, 2, 0, 2, 2, 2),
        (1, 0, 1, 1, 0, 2, 2, 0, 0),
        (2, 1, 2, 2, 0, 2, 2, 0, 0),
        (2, 0, 2, 2, 1, 1, 1, 0, 0),
    ]
    safe_D = span(safe_basis)
    assert len(safe_D) == 3 ** 4 == 81
    assert safe_D.isdisjoint(bad_S)

    good_edges = make_edges(hamiltonian, [[0, 3, 1, 5], [2, 6, 4, 7]])
    good_Q = fundamental_cycle_matrix(n, good_edges)
    good_S = syndromes(good_Q)
    assert len(good_Q) == 9
    assert len(good_S) == 18637
    assert zero in good_S

    # Strong zero-reflection forbids every attainable nonzero syndrome from the kernel.
    good_allowed = universe - (good_S - {zero})
    good_projective = {projective(v) for v in good_allowed if v != zero}
    assert len(good_projective) == 523
    no_line, witness = no_projective_line(good_projective)
    assert no_line and witness is None

    print("PASS: zero-reflecting quotient iff safe kernel; bad control has 4D safe kernel, good control has no 2D strong safe kernel.")


if __name__ == "__main__":
    main()
