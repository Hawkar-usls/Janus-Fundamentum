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
            assert key not in edges, ("overlap", edge)
            edges.add(key)
    return sorted(edges)


def count_colorings(n, edges):
    count = 0
    for colors in product(range(3), repeat=n):
        if all(colors[u] != colors[v] for u, v in edges):
            count += 1
    return count


def spanning_tree(n, edges):
    adjacency = [[] for _ in range(n)]
    for edge in edges:
        u, v = edge
        adjacency[u].append((v, edge))
        adjacency[v].append((u, edge))

    root = 0
    seen = {root}
    queue = deque([root])
    tree = set()
    while queue:
        u = queue.popleft()
        for v, edge in adjacency[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
                tree.add(edge)
    assert len(seen) == n
    assert len(tree) == n - 1
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
    edge_index = {edge: i for i, edge in enumerate(edges)}
    tree = spanning_tree(n, edges)
    rows = []

    for chord in edges:
        if chord in tree:
            continue
        u, v = chord  # canonical orientation u -> v because u < v
        row = [0] * len(edges)
        row[edge_index[chord]] = 1

        # Close the fundamental cycle by traversing the tree from v back to u.
        for a, b in tree_path(tree, n, v, u):
            edge = undirected((a, b))
            coefficient = 1 if edge == (a, b) else -1
            row[edge_index[edge]] = coefficient % 3
        rows.append(row)

    beta = len(edges) - n + 1
    assert len(rows) == beta
    return rows


def zero_label_sign_bases(n, edges):
    Q = fundamental_cycle_matrix(n, edges)
    witnesses = []
    for signs in product((1, 2), repeat=len(edges)):  # 2 represents -1 in GF(3)
        syndrome = [
            sum(row[j] * signs[j] for j in range(len(edges))) % 3
            for row in Q
        ]
        if not any(syndrome):
            witnesses.append(signs)
    return Q, witnesses


def integrate_tension(n, edges, signs):
    adjacency = [[] for _ in range(n)]
    for (u, v), value in zip(edges, signs):
        # Canonical edge orientation is u -> v.
        adjacency[u].append((v, value % 3))
        adjacency[v].append((u, (-value) % 3))

    color = [None] * n
    color[0] = 0
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v, delta in adjacency[u]:
            wanted = (color[u] + delta) % 3
            if color[v] is None:
                color[v] = wanted
                queue.append(v)
            else:
                assert color[v] == wanted
    assert all(value is not None for value in color)
    assert all(color[u] != color[v] for u, v in edges)
    return tuple(color)


def check_control(factor_cycles, expected_colorings, expected_zero_bases):
    n = 8
    hamiltonian = list(range(n))
    edges = make_edges(hamiltonian, factor_cycles)
    assert len(edges) == 16
    assert all(sum(v in edge for edge in edges) == 4 for v in range(n))

    coloring_count = count_colorings(n, edges)
    Q, bases = zero_label_sign_bases(n, edges)

    assert len(Q) == len(edges) - n + 1 == 9
    assert coloring_count == expected_colorings
    assert len(bases) == expected_zero_bases
    assert coloring_count == 3 * len(bases)

    reconstructed = {integrate_tension(n, edges, basis) for basis in bases}
    assert len(reconstructed) == len(bases)
    assert all(colors[0] == 0 for colors in reconstructed)


def main():
    # Colourable C8 + two C4 factors: six labelled colourings = two tensions.
    check_control([[0, 3, 1, 5], [2, 6, 4, 7]], 6, 2)

    # Frozen v5.3 mixed-cycle false-positive control: zero colourings/tensions.
    check_control([[0, 3, 1, 6], [2, 4, 7, 5]], 0, 0)

    print("PASS: 3-colouring iff zero-label basis of the two-choice edge partition matroid; good/bad 8-vertex controls replayed.")


if __name__ == "__main__":
    main()
