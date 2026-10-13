#!/usr/bin/env python3
"""R5 all-size Kempe six-port SATURATION-OR-FORBIDDEN constructive gate.

Input promise: a proper 3-edge-colouring of a cubic six-pole whose six
physical port roots are distinct and whose pair-equality bits are one
of {100,010,001}. No premise is made about OTHER colourings.

Proved dichotomy, in O(|V|+|E|) time (port number is constant):
1) Find an explicit proper colouring with forbidden bit signature
   by <=6 sequential two-colour path flips from the input witness; OR
2) Produce explicit proper colourings realizing all 36 physical
   boundary tuples of the input bit, each within <=4 path flips.

This is NOT a proof that forbidden states exist for every input;
the SATURATION branch is allowed. It is NOT a generic SCL solver.

Under the stronger GLOBAL hypothesis Bits(M) subset of {100,010,001},
outcome 1 is impossible. Therefore every nonempty bit fibre is fully
saturated (36 port tuples), and the number of full proper colourings
is UNIFORM on those 36 tuples.

The 108-state finite matching lemma:
- 36 balanced 2+2+2 states each have one GOOD-preserving matching
  for each of the 3 colour pairs;
- 72 unbalanced 4+2 states each have one GOOD-preserving matching
  for the 2 pairs that include the ABSENT colour, and 5 matchings
  for the remaining pair of PRESENT colours.
The 252 unique choices induce 432 directed single-path moves. All are
reversible/unique from both ends. They form three connected components
of size 36, each with diameter <=4 (exactly 4).
Thus under the global GOOD-only hypothesis, path-flip involutions
establish bijections of full internal-colouring fibres. No uniform
multiplicity is asserted for general six-poles admitting bad states.

Uses independently validated Kempe path extractor from earlier R5
n8 test; finite transition enumeration is recomputed here.
"""

from collections import Counter, defaultdict, deque
from itertools import combinations, product
from r5_kempe_coupled_involutions_n8_barrier import (
    COLORS, GOOD, bits, matchings, kempe_moves,
    N8_WITNESS_EDGES, N8_WITNESS_EDGE_COLORS, INITIAL_PORTS,
    verify_colouring, is_connected
)

PORT_PAIRS = ((0, 1), (2, 3), (4, 5))


def parity_states():
    return tuple(s for s in product(COLORS, repeat=6)
                 if bits(s) in GOOD
                 and all(Counter(s)[c] % 2 == 0 for c in COLORS))


def toggled_boundary(s, ab, m, mask):
    a, b = ab
    t = list(s)
    for j, (u, v) in enumerate(m):
        if mask & (1 << j):
            t[u] = a + b - t[u]
            t[v] = a + b - t[v]
    return tuple(t)


def forced_transition_graph():
    states = parity_states()
    assert len(states) == 108
    forced = defaultdict(list)
    candidates_hist = Counter()
    legal_state_pair_count = 0
    for s in states:
        for ab in combinations(COLORS, 2):
            roots = tuple(i for i, c in enumerate(s) if c in ab)
            good_matchings = [
                m for m in matchings(roots)
                if all(bits(toggled_boundary(s, ab, m, mask)) in GOOD
                       for mask in range(1 << len(m)))
            ]
            candidates_hist[len(good_matchings)] += 1
            assert len(good_matchings) in (1, 5)
            if len(good_matchings) != 1:
                assert tuple(sorted(Counter(s).values())) == (2, 4)
                assert len(roots) == 6
                continue
            legal_state_pair_count += 1
            m = good_matchings[0]
            for j, ends in enumerate(m):
                t = toggled_boundary(s, ab, m, 1 << j)
                assert bits(t) == bits(s)
                forced[s].append((t, ab, tuple(sorted(ends))))

    assert candidates_hist == Counter({1: 252, 5: 72}), candidates_hist
    assert legal_state_pair_count == 252
    assert sum(map(len, forced.values())) == 432

    # Crucially we only use a switch forced in BOTH directions. At t
    # the same bicoloured path remains the same (a,b)-component, so
    # it is the reverse bijection on full colouring fibres.
    for s, moves in forced.items():
        for t, ab, endpoints in moves:
            assert (s, ab, endpoints) in forced[t], (s, t, ab, endpoints)

    diameters = Counter()
    component_sizes = {}
    for s in states:
        routes = routes_from(s, forced)
        assert len(routes) == 36, (s, len(routes))
        assert all(bits(t) == bits(s) for t in routes)
        component_sizes[bits(s)] = len(routes)
        diameters[max(map(len, routes.values()))] += 1
    assert component_sizes == {"001":36, "010":36, "100":36}
    # The forced-move base for each bit is an undirected 36-vertex,
    # 72-edge graph. Its graph-theoretic cycle rank is 72-36+1=37.
    for b in GOOD:
        vertices = [x for x in states if bits(x) == b]
        undirected_edges = {
            tuple(sorted((x, y)))
            for x in vertices for y, _, _ in forced[x]
        }
        assert len(vertices) == 36
        assert len(undirected_edges) == 72
        assert len(undirected_edges) - len(vertices) + 1 == 37
    assert diameters == Counter({3: 36, 4: 72}), diameters
    print("GOOD_MATCHINGS_UNIQUE_252_AMBIGUOUS_72 PASS")
    print("BIDIRECTIONAL_FORCED_SINGLE_PATH_EDGES_432 PASS")
    print("SAME_BIT_COMPONENTS_THREE_OF_36 PASS")
    print("KEMPE_BASE_PER_BIT_V36_E72_CYCLE_RANK37 PASS")
    print("ALL_STARTS_DIAMETER_AT_MOST_4", dict(sorted(diameters.items())))
    return forced


def routes_from(start, graph):
    """Shortest abstract path-swap routes from start to each reached tuple."""
    discovered = {start: ()}
    queue = deque([start])
    while queue:
        s = queue.popleft()
        for t, ab, ends in graph[s]:
            if t not in discovered:
                discovered[t] = discovered[s] + ((ab, ends, t),)
                queue.append(t)
    return discovered


def path_moves(edges, ec, ports, ab):
    """Compute the actual pairing of port endpoints of a/b Kempe paths."""
    real = {}
    for new_ec, new_ports, pair, ends in kempe_moves(
        max(max(edge) for edge in edges)+1, edges, ec, ports
    ):
        if pair == ab and len(ends) == 2:
            assert ends not in real
            real[ends] = (new_ec, new_ports)
    required = {i for i, c in enumerate(ports) if c in ab}
    assert {j for ends in real for j in ends} == required
    return real


def flip_path(edges, ec, ports, ab, endpoints):
    moves = path_moves(edges, ec, ports, ab)
    return moves[endpoints]


def saturation_or_forbidden(edges, ec, ports, forced):
    """Return ("FORBIDDEN", colouring, flip_count) or ("SATURATED", 36 witnesses).

    A forbidden certificate is always a legal full colouring, not an
    abstract tuple. With six ports the total work is linear in |E|.
    """
    n = max(max(edge) for edge in edges) + 1
    verify_colouring(n, edges, ec, ports)
    assert is_connected(n, edges)
    assert bits(ports) in GOOD
    start = tuple(ports)
    routes = routes_from(start, forced)
    assert len(routes) == 36 and max(map(len, routes.values())) <= 4
    witnesses = {}
    for desired, route in sorted(
        routes.items(), key=lambda kv: (len(kv[1]), kv[0])
    ):
        curr_e, curr_p = tuple(ec), tuple(ports)
        for step_number, (ab, ends, expected) in enumerate(route):
            choices = path_moves(edges, curr_e, curr_p, ab)
            # This is the exact matching that is uniquely GOOD-safe
            # in the abstract finite calculation.
            allowed = tuple(
                endpoints for _, pair, endpoints in forced[curr_p]
                if pair == ab
            )
            canonical = frozenset(allowed)
            if frozenset(choices) != canonical:
                # By uniqueness, SOME SUBSET of actual alternating
                # terminal paths yields a forbidden bit. Find it in <=
                # 2^3 possibilities, then flip the paths consecutively.
                pairs = sorted(choices)
                for mask in range(1, 1 << len(pairs)):
                    bad_e, bad_p = curr_e, curr_p
                    num = 0
                    for j, xy in enumerate(pairs):
                        if mask & (1 << j):
                            bad_e, bad_p = flip_path(
                                edges, bad_e, bad_p, ab, xy)
                            num += 1
                    if bits(bad_p) not in GOOD:
                        verify_colouring(n, edges, bad_e, bad_p)
                        flips = step_number + num
                        assert flips <= 6
                        return "FORBIDDEN", (bad_e, bad_p), flips
                raise AssertionError("finite uniqueness violated: noncanonical matching all GOOD")
            curr_e, curr_p = choices[ends]
            assert curr_p == expected
        assert curr_p == desired
        witnesses[desired] = (curr_e, curr_p)
    assert len(witnesses) == 36
    return "SATURATED", witnesses, max(map(len, routes.values()))


def main():
    graph = forced_transition_graph()
    result, witness, flips = saturation_or_forbidden(
        N8_WITNESS_EDGES, N8_WITNESS_EDGE_COLORS,
        INITIAL_PORTS, graph
    )
    assert result == "FORBIDDEN"
    assert bits(witness[1]) == "000", (result, witness[1])
    assert flips == 3, flips
    print("N8_CONSTRUCTIVE_FORBIDDEN_WITNESS_IN_THREE_KEMPE_PATH_SWITCHES PASS")
    print("ALL_N_THEOREM: FORBIDDEN_WITHIN_SIX_OR_SATURATE_36_WITHIN_FOUR")
    print("GLOBAL_GOOD_ONLY => 36_PHYSICAL_STATES_PER_BIT + UNIFORM_FIBRE_COUNTS")
    print("NO_UNIVERSAL_EXACTONE_NO_GO; NO_PC_DEGREE_LOWER_BOUND")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
