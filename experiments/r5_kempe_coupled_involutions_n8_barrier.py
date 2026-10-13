#!/usr/bin/env python3
"""R5: coupled Kempe involutions, exact 6-port states, and a 3-switch witness.

PROVED FINITELY (independent finite enumeration, not an all-n theorem):
* parity-legal six-port states: 183;
* parity-legal exact-one states: 108 = 36 of type 2+2+2 + 72 of type 4+2;
* at any 2+2+2 exact-one boundary state, each colour pair has exactly
  one boundary matching whose every independent Kempe-path switch
  remains exact-one, and this matching preserves the same Exact-One bit;
* at every 4+2 exact-one boundary state, the two present colours have
  five such matchings, four capable of changing the Exact-One bit;
  the other two colour pairs have one admissible matching each.
* for six distinct port roots on eight internal vertices, enumerate all
  15^3 labelled reference 3-colour matchings (reject duplicate edges and
  disconnected graphs): 1472 legal connected SIMPLE coloured sources.
  Their minimum number of Kempe switches to a forbidden port bit tuple
  is 1:1384, 2:72, 3:16.
* a concrete 8-vertex source has no forbidden tuple within <=2 Kempe
  switches of its displayed starting colouring, but reaches 000 after 3.

LIMIT: These are source-colouring facts and a finite witness. They do NOT
establish that any all-size cubic sixpole has a forbidden signature.
They do NOT imply a PC degree lower bound or a universal SCL solver.
Port roots are six distinct vertices; exact-one bit convention is
(0==1, 2==3, 4==5).
"""

from collections import Counter, defaultdict, deque
from itertools import combinations, product

COLORS = (0, 1, 2)
PAIRS = ((0, 1), (2, 3), (4, 5))
GOOD = {"100", "010", "001"}
INITIAL_PORTS = (0, 0, 1, 2, 1, 2)
N8_WITNESS_EDGES = (
    (2, 3), (4, 6), (5, 7),
    (0, 1), (3, 7), (5, 6),
    (0, 4), (1, 6), (2, 7),
)
N8_WITNESS_EDGE_COLORS = (0,) * 3 + (1,) * 3 + (2,) * 3


def bits(ports):
    return "".join(str(int(ports[u] == ports[v])) for u, v in PAIRS)


def matchings(vertices):
    """All perfect matchings, with a deterministic vertex order."""
    vertices = tuple(vertices)
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for j in range(1, len(vertices)):
        other = vertices[j]
        for tail in matchings(vertices[1:j] + vertices[j + 1:]):
            yield ((min(first, other), max(first, other)),) + tail


def valid_boundary_matching(ports, a, b, matching):
    """All simultaneous choices of independent (a,b)-path switches stay GOOD."""
    assert set(i for p in matching for i in p) == {
        i for i, c in enumerate(ports) if c in (a, b)
    }
    for mask in range(1 << len(matching)):
        new = list(ports)
        for j, (u, v) in enumerate(matching):
            if (mask >> j) & 1:
                new[u] = a + b - new[u]
                new[v] = a + b - new[v]
        if bits(new) not in GOOD:
            return False
    return True


def good_boundary_matchings(ports, a, b):
    roots = [i for i, c in enumerate(ports) if c in (a, b)]
    return tuple(
        mm for mm in matchings(roots)
        if valid_boundary_matching(ports, a, b, mm)
    )


def boundary_classification():
    even = [
        p for p in product(COLORS, repeat=6)
        if all(Counter(p)[c] % 2 == 0 for c in COLORS)
    ]
    good = [p for p in even if bits(p) in GOOD]
    assert len(even) == 183
    assert len(good) == 108
    types = Counter(tuple(sorted(Counter(p).values())) for p in good)
    assert types == Counter({(2, 2, 2): 36, (2, 4): 72})

    for p in good:
        ct = Counter(p)
        if sorted(ct.values()) == [2, 2, 2]:
            for a, b in combinations(COLORS, 2):
                ms = good_boundary_matchings(p, a, b)
                assert len(ms) == 1, (p, a, b, ms)
                for u, v in ms[0]:
                    altered = list(p)
                    altered[u], altered[v] = a+b-altered[u], a+b-altered[v]
                    assert bits(altered) == bits(p)
        else:
            major = next(c for c, count in ct.items() if count == 4)
            minor = next(c for c, count in ct.items() if count == 2)
            absent = next(c for c in COLORS if c not in ct)
            active = good_boundary_matchings(p, major, minor)
            assert len(active) == 5
            changing = 0
            for m in active:
                can_change = False
                for mask in range(1 << len(m)):
                    q = list(p)
                    for j, (u, v) in enumerate(m):
                        if mask >> j & 1:
                            q[u] = major + minor - q[u]
                            q[v] = major + minor - q[v]
                    if bits(q) != bits(p):
                        can_change = True
                changing += can_change
            assert changing == 4
            assert len(good_boundary_matchings(p, major, absent)) == 1
            assert len(good_boundary_matchings(p, minor, absent)) == 1
    print("BOUNDARY_183_EXACTONE_108_222_36_42_72 PASS")
    print("222_PAIR_MATCHING_UNIQUE_BIT_PRESERVING PASS")
    print("42_ACTIVE_MATCHINGS_5_CHANGE_CAPABLE_4 PASS")


def is_connected(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen, stack = {0}, [0]
    while stack:
        for w in adj[stack.pop()]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n


def verify_colouring(n, edges, ec, ports):
    assert len(edges) == len(ec) == (3*n-6)//2
    assert len(ports) == 6
    assert len(set(edges)) == len(edges)
    incident = [[] for _ in range(n)]
    for (u, v), col in zip(edges, ec):
        assert 0 <= u < v < n and col in COLORS
        incident[u].append(col)
        incident[v].append(col)
    for v in range(n):
        if v < 6:
            incident[v].append(ports[v])
        assert sorted(incident[v]) == list(COLORS), (v, incident[v])


def kempe_moves(n, edges, ec, ports):
    """Actual path and cycle components of all three bicoloured graphs."""
    full = tuple(ec) + tuple(ports)
    ne = len(edges)
    output = []
    for a, b in combinations(COLORS, 2):
        adj = defaultdict(list)
        for j, (u, v) in enumerate(edges):
            if full[j] in (a, b):
                adj[("v", u)].append((("v", v), j))
                adj[("v", v)].append((("v", u), j))
        for i, colour in enumerate(ports):
            if colour in (a, b):
                adj[("v", i)].append((("p", i), ne+i))
                adj[("p", i)].append((("v", i), ne+i))
        remaining = set(adj)
        while remaining:
            start = min(remaining)
            seen, todo, indices = {start}, [start], set()
            while todo:
                node = todo.pop()
                for dest, j in adj[node]:
                    indices.add(j)
                    if dest not in seen:
                        seen.add(dest)
                        todo.append(dest)
            remaining -= seen
            swapped = list(full)
            for j in indices:
                swapped[j] = a + b - swapped[j]
            new_ec = tuple(swapped[:ne])
            new_ports = tuple(swapped[ne:])
            verify_colouring(n, edges, new_ec, new_ports)
            touched_ports = tuple(sorted(j-ne for j in indices if j >= ne))
            output.append((new_ec, new_ports, (a, b), touched_ports))
    return output


def first_bad_depth(n, edges, ec, ports, limit=3):
    start = (tuple(ec), tuple(ports))
    seen, queue = {start}, deque([(start, 0)])
    while queue:
        (e, p), distance = queue.popleft()
        if bits(p) not in GOOD:
            return distance
        if distance == limit:
            continue
        for new_ec, new_ports, _, _ in kempe_moves(n, edges, e, p):
            state = (new_ec, new_ports)
            if state not in seen:
                seen.add(state)
                queue.append((state, distance+1))
    return None


def test_witness():
    e, ec, p = N8_WITNESS_EDGES, N8_WITNESS_EDGE_COLORS, INITIAL_PORTS
    verify_colouring(8, e, ec, p)
    assert is_connected(8, e)
    assert first_bad_depth(8, e, ec, p, limit=2) is None
    assert first_bad_depth(8, e, ec, p, limit=3) == 3
    trace = (
        ((0, 1), (2, 4), (0, 0, 0, 2, 0, 2)),
        ((0, 2), (1, 5), (0, 2, 0, 2, 0, 0)),
        ((0, 1), (2, 5), (0, 2, 1, 2, 0, 1)),
    )
    for ab, endpoints, expected_ports in trace:
        candidates = [
            (new_ec, new_ports) for new_ec, new_ports, pair, touched
            in kempe_moves(8, e, ec, p)
            if pair == ab and touched == endpoints
        ]
        assert len(candidates) == 1, (ab, endpoints, candidates)
        ec, p = candidates[0]
        assert p == expected_ports
    assert bits(p) == "000"
    print("N8_THREE_SWITCH_WITNESS 100 -> 100 -> 001 -> 000 PASS")


def census_n8():
    choices = {
        c: list(matchings(tuple(v for v in range(8)
                 if v >= 6 or INITIAL_PORTS[v] != c)))
        for c in COLORS
    }
    assert tuple(len(choices[c]) for c in COLORS) == (15, 15, 15)
    freq = Counter()
    for a, b, c in product(choices[0], choices[1], choices[2]):
        edges = a+b+c
        if len(set(edges)) != len(edges) or not is_connected(8, edges):
            continue
        ec = (0,)*3 + (1,)*3 + (2,)*3
        verify_colouring(8, edges, ec, INITIAL_PORTS)
        d = first_bad_depth(8, edges, ec, INITIAL_PORTS, limit=3)
        freq[d] += 1
    assert freq == Counter({1:1384, 2:72, 3:16}), freq
    print("N8_EXHAUSTIVE_CONNECTED_SIMPLE_COLOURED_1472", dict(sorted(freq.items())))
    print("NO_N_INDEPENDENT_EXACTONE_NO_GO; PC_UNBOUNDED_OPEN; P_VS_NP_OPEN")


if __name__ == "__main__":
    boundary_classification()
    test_witness()
    census_n8()
