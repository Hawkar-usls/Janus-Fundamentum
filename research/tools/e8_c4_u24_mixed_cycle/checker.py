from itertools import product
from collections import deque


def cycle_edges(cycle):
    return [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]


def undirected(edge):
    a, b = edge
    return (a, b) if a < b else (b, a)


def is_proper_coloring(edges, colors):
    return all(colors[u] != colors[v] for u, v in edges)


def count_colorings(n, edges):
    count = 0
    witness = None
    for colors in product(range(3), repeat=n):
        if is_proper_coloring(edges, colors):
            count += 1
            witness = witness or colors
    return count, witness


def make_graph(hamiltonian_cycle, factor_cycles):
    edges = set()
    for cycle in [hamiltonian_cycle] + factor_cycles:
        for edge in cycle_edges(cycle):
            key = undirected(edge)
            assert key not in edges, ("edge overlap", edge)
            edges.add(key)
    return edges


def cycle_state_dicts(cycle):
    states = []
    for values in product(range(3), repeat=len(cycle)):
        if all(values[i] != values[(i + 1) % len(cycle)] for i in range(len(cycle))):
            states.append({v: values[i] for i, v in enumerate(cycle)})
    return states


def block_csp_exists(hamiltonian_cycle, factor_cycles):
    local_states = [cycle_state_dicts(cycle) for cycle in factor_cycles]
    for state_tuple in product(*local_states):
        colors = {}
        for state in state_tuple:
            colors.update(state)
        if all(colors[u] != colors[v] for u, v in cycle_edges(hamiltonian_cycle)):
            return True, tuple(colors[i] for i in range(len(hamiltonian_cycle)))
    return False, None


def affine_orbit(coloring):
    return {
        tuple((a + s * value) % 3 for value in coloring)
        for a in range(3)
        for s in (1, 2)
    }


def potential_exists(n, oriented_values):
    adjacency = [[] for _ in range(n)]
    for u, v, value in oriented_values:
        adjacency[u].append((v, value % 3))
        adjacency[v].append((u, (-value) % 3))

    potential = [None] * n
    for start in range(n):
        if potential[start] is not None:
            continue
        potential[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v, delta in adjacency[u]:
                wanted = (potential[u] + delta) % 3
                if potential[v] is None:
                    potential[v] = wanted
                    queue.append(v)
                elif potential[v] != wanted:
                    return False, None
    return True, potential


def check_c4_classification():
    c4 = [0, 1, 2, 3]
    edges = cycle_edges(c4)
    full = [
        colors
        for colors in product(range(3), repeat=4)
        if is_proper_coloring(edges, colors)
    ]
    normalized = [colors for colors in full if colors[0] == 0]

    assert len(full) == 18
    assert len(normalized) == 6

    supports = set()
    for colors in normalized:
        differences = [
            (colors[c4[(i + 1) % 4]] - colors[c4[i]]) % 3
            for i in range(4)
        ]
        assert all(value in (1, 2) for value in differences)
        minus_support = tuple(i for i, value in enumerate(differences) if value == 2)
        assert len(minus_support) == 2
        supports.add(minus_support)
    assert len(supports) == 6
    assert supports == set(tuple(s) for s in __import__('itertools').combinations(range(4), 2))

    # Converse: every U_{2,4} base integrates to one normalized proper colouring.
    reconstructed = set()
    for support in supports:
        values = [2 if i in support else 1 for i in range(4)]
        assert sum(values) % 3 == 0
        colors = [0]
        for i in range(3):
            colors.append((colors[-1] + values[i]) % 3)
        assert (colors[0] - colors[3]) % 3 == values[3]
        assert is_proper_coloring(edges, tuple(colors))
        reconstructed.add(tuple(colors))
    assert reconstructed == set(normalized)

    unseen = set(full)
    orbit_shapes = set()
    orbit_sizes = []
    while unseen:
        coloring = next(iter(unseen))
        orbit = affine_orbit(coloring) & set(full)
        orbit_sizes.append(len(orbit))
        shapes = {(c[0] == c[2], c[1] == c[3]) for c in orbit}
        assert len(shapes) == 1
        orbit_shapes |= shapes
        unseen -= orbit
    assert sorted(orbit_sizes) == [6, 6, 6]
    assert orbit_shapes == {(True, True), (True, False), (False, True)}


def check_block_csp_and_mixed_cycle_control():
    hamiltonian = list(range(8))

    # Exact colourable control.
    good_factor = [[0, 3, 1, 5], [2, 6, 4, 7]]
    good_edges = make_graph(hamiltonian, good_factor)
    good_count, good_witness = count_colorings(8, good_edges)
    good_block, good_block_witness = block_csp_exists(hamiltonian, good_factor)
    assert good_count > 0 and good_witness is not None
    assert good_block and good_block_witness is not None
    assert is_proper_coloring(good_edges, good_block_witness)

    # Frozen false-positive control: every factor cycle can satisfy its own
    # GF(3) tension equation, but the full graph is not 3-colourable.
    bad_factor = [[0, 3, 1, 6], [2, 4, 7, 5]]
    bad_edges = make_graph(hamiltonian, bad_factor)
    degrees = [0] * 8
    for u, v in bad_edges:
        degrees[u] += 1
        degrees[v] += 1
    assert degrees == [4] * 8
    assert len(bad_edges) == 16

    bad_count, bad_witness = count_colorings(8, bad_edges)
    bad_block, bad_block_witness = block_csp_exists(hamiltonian, bad_factor)
    assert bad_count == 0 and bad_witness is None
    assert not bad_block and bad_block_witness is None

    # Local factor-cycle signs: H has four + and four -, each C4 has two + and two -.
    local_sequences = [
        (hamiltonian, [1, 1, 1, 1, 2, 2, 2, 2]),
        (bad_factor[0], [1, 1, 2, 2]),
        (bad_factor[1], [1, 1, 2, 2]),
    ]
    oriented_values = []
    used_edges = set()
    for cycle, values in local_sequences:
        assert sum(values) % 3 == 0
        for (u, v), value in zip(cycle_edges(cycle), values):
            key = undirected((u, v))
            assert key not in used_edges
            used_edges.add(key)
            oriented_values.append((u, v, value))
    assert used_edges == bad_edges

    global_tension, _ = potential_exists(8, oriented_values)
    assert not global_tension

    # Connected 4-regular n=8 graph: beta=|E|-|V|+1=9.
    cycle_rank = len(bad_edges) - 8 + 1
    factor_cycle_rank = 1 + len(bad_factor)
    assert cycle_rank == 9
    assert factor_cycle_rank == 3
    assert cycle_rank - factor_cycle_rank == 6


def main():
    check_c4_classification()
    check_block_csp_and_mixed_cycle_control()
    print("PASS: C4 tension states are U_{2,4} bases; block-CSP controls and mixed-cycle false positive verified.")


if __name__ == "__main__":
    main()
