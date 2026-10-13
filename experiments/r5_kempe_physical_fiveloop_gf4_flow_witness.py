#!/usr/bin/env python3
"""R5 physical five-step cross-colour Kempe holonomy and GF(2)^2 flow audit.

PROOF / FINITE FACTS (not an Exact-One 6-pole construction):
- At the fixed boundary s=(0,0,1,2,1,2), enumerate all triples of
  reference proper-colour matchings on 8 labelled vertices, with one
  distinct semiedge at each of vertices 0..5. 15^3 candidates.
- 1472 are simple and connected; the specified 5-move boundary loop
  actually lifts to 192 of the starting FULL colourings.
- 160 lifts return the same full colouring; 32 are nontrivial and return
  the SAME ordered physical boundary s but DIFFERENT interior.
- The explicit witness has exactly TWO proper full colourings above s.
  The nontrivial five-step loop from the first to the second swaps
  colours 0<->1 on its interior 4-cycle (3,6,7,5,3).
- The same prescribed 5-loop need not lift starting from the other
  colouring: this example admits forbidden signatures and is NOT a
  global-GOOD covering-space witness.

ALL-SIZE PROVED IDENTITY:
Represent colours 0,1,2 by nonzero elements 1,2,3 in F2^2. At every
cubic vertex these xor to zero. If c,c' are two proper colourings with
identical ordered physical port colours, their difference
D_e = code(c_e) XOR code(c'_e) is an F2^2 circulation with no boundary:
the xor of its incident internal edge labels vanishes at each vertex.
For a connected 6-pole with n internal vertices, m=(3n-6)/2 ordinary
edges and cycle rank beta=m-n+1=(n-4)/2; the full-colouring fibre over
any fixed port tuple therefore injects into a 2*beta=n-4 dimensional
binary vector space. So fibre size <=2**(n-4). This exponential bound
is necessary, NOT polynomial and NOT a generic SCL solver.

IMPORTANT LIMIT:
The physical witness does not satisfy the GLOBAL good-only Exact-One
signature hypothesis. Thus it disproves the unconditional five-loop
identity but NOT an identity postulated only for globally Exact-One
sixpoles. No universal gadget no-go or native PC degree lower bound.
"""
from collections import Counter
from itertools import product

PORTS = (0, 0, 1, 2, 1, 2)
COLOURS = (0, 1, 2)
PORT_PAIRS = ((0, 1), (2, 3), (4, 5))
REFERENCE_C = (0,)*3 + (1,)*3 + (2,)*3

# Each (colour pair, ordered terminal endpoints, resulting port tuple).
STEPS = (
    ((0, 1), (0, 1), (1, 1, 1, 2, 1, 2)),
    ((0, 1), (2, 4), (1, 1, 0, 2, 0, 2)),
    ((1, 2), (0, 1), (2, 2, 0, 2, 0, 2)),
    ((0, 1), (2, 4), (2, 2, 1, 2, 1, 2)),
    ((0, 2), (0, 1), PORTS),
)

# Edge indices in groups of three reference colours 0, 1, 2.
WITNESS_EDGES = (
    (2, 4), (3, 6), (5, 7),
    (0, 1), (3, 5), (6, 7),
    (0, 2), (1, 6), (4, 7),
)
WITNESS_AFTER = (0, 1, 1, 1, 0, 0, 2, 2, 2)


def bits(p):
    return ''.join(str(int(p[a] == p[b])) for a, b in PORT_PAIRS)


def matching(xs):
    xs = tuple(xs)
    if not xs:
        yield ()
        return
    a = xs[0]
    for k in range(1, len(xs)):
        b = xs[k]
        for rest in matching(xs[1:k] + xs[k+1:]):
            yield ((a, b),) + rest


def connected(edges):
    adj = [[] for _ in range(8)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen, stack = {0}, [0]
    while stack:
        for b in adj[stack.pop()]:
            if b not in seen:
                seen.add(b); stack.append(b)
    return len(seen) == 8


def check_colouring(edges, ec, p):
    assert len(edges) == len(ec) == 9
    assert len(p) == 6 and len(set(edges)) == 9
    incident = [([] if v >= 6 else [p[v]]) for v in range(8)]
    for (a, b), c in zip(edges, ec):
        assert 0 <= a < b < 8 and c in COLOURS
        incident[a].append(c)
        incident[b].append(c)
    assert all(sorted(x) == [0, 1, 2] for x in incident)


def actual_flip(edges, ec, p, pair, expected_ends):
    """Find genuine bicolour path through a physical semiedge."""
    a, b = pair
    adj = [[] for _ in range(14)]
    for k, (u, v) in enumerate(edges):
        if ec[k] in pair:
            adj[u].append((v, k))
            adj[v].append((u, k))
    for j, colour in enumerate(p):
        if colour in pair:
            k = 9+j
            adj[j].append((8+j, k))
            adj[8+j].append((j, k))
    seen, stack, touched = {8+expected_ends[0]}, [8+expected_ends[0]], set()
    while stack:
        for v, k in adj[stack.pop()]:
            touched.add(k)
            if v not in seen:
                seen.add(v);stack.append(v)
    terminals = tuple(sorted(v-8 for v in seen if v>=8))
    if terminals != expected_ends:
        return None
    mixed = list(ec) + list(p)
    for k in touched:
        mixed[k] = a+b-mixed[k]
    new_ec,new_p = tuple(mixed[:9]), tuple(mixed[9:])
    check_colouring(edges, new_ec, new_p)
    return new_ec, new_p


def lift_five_path(edges, ec=REFERENCE_C, p=PORTS):
    initial = (ec, p)
    for pair, ends, required_p in STEPS:
        result = actual_flip(edges, ec, p, pair, ends)
        if result is None:
            return None
        ec,p = result
        assert p == required_p, (p, required_p)
    assert p == initial[1]
    return ec, p


def xor_circulation(edges, ec, other):
    """Validate the zero-boundary GF(2)^2 flow difference."""
    codes = (1, 2, 3)
    div = [0]*8
    changed = []
    for k, ((u,v), a,b) in enumerate(zip(edges, ec, other)):
        d = codes[a] ^ codes[b]
        div[u] ^= d; div[v] ^= d
        if d:
            changed.append((k, (u,v), a,b,d))
    assert all(x == 0 for x in div), (div, changed)
    return changed


def fibre_at_fixed_ports(edges, p=PORTS):
    """Independent exhaustive 3-colour DFS for nine ordinary edges."""
    used = [set([p[v]]) if v < 6 else set() for v in range(8)]
    colours = [-1]*9
    found = []
    def dfs(k):
        if k == 9:
            assert all(len(s)==3 for s in used)
            found.append(tuple(colours));return
        u,v=edges[k]
        for c in COLOURS:
            if c in used[u] or c in used[v]:
                continue
            colours[k]=c; used[u].add(c);used[v].add(c)
            dfs(k+1)
            used[u].remove(c);used[v].remove(c);colours[k]=-1
    dfs(0)
    return found


def run():
    assert bits(PORTS) == '100'
    check_colouring(WITNESS_EDGES, REFERENCE_C, PORTS)
    assert connected(WITNESS_EDGES)
    assert lift_five_path(WITNESS_EDGES) == (WITNESS_AFTER, PORTS)
    actual_fibre = fibre_at_fixed_ports(WITNESS_EDGES)
    assert actual_fibre == [REFERENCE_C, WITNESS_AFTER] or set(actual_fibre)=={REFERENCE_C,WITNESS_AFTER}
    differences = xor_circulation(WITNESS_EDGES, REFERENCE_C, WITNESS_AFTER)
    assert {edge for _,edge,_,_,_ in differences} == {
        (3,6), (5,7), (3,5), (6,7)
    }
    # The other fibre element does not lift through the full prescribed
    # five moves, so this is a PARTIAL lift, not an honest 2-sheet cover.
    assert lift_five_path(WITNESS_EDGES, WITNESS_AFTER, PORTS) is None
    print('EXPLICIT_N8_PHYSICAL_NONTRIVIAL_FIVE_LOOP PASS', differences)
    print('EXPLICIT_N8_FIBRE_OVER_001212 EXACTLY_TWO PASS')

    matchings = {c: tuple(matching(
        tuple(v for v in range(8) if v>=6 or PORTS[v]!=c)
    )) for c in COLOURS}
    assert [len(matchings[c]) for c in COLOURS] == [15,15,15]
    counts = Counter()
    nontrivial_witnesses = 0
    for a,b,c in product(matchings[0], matchings[1], matchings[2]):
        edges = a+b+c
        if len(set(edges))!=9 or not connected(edges):
            continue
        check_colouring(edges, REFERENCE_C, PORTS)
        counts['simple_connected'] += 1
        lift=lift_five_path(edges)
        if lift is None:
            continue
        counts['fully_liftable'] += 1
        assert lift[1] == PORTS
        xor_circulation(edges, REFERENCE_C, lift[0])
        if lift[0] == REFERENCE_C:
            counts['identity'] += 1
        else:
            counts['nontrivial'] += 1
            nontrivial_witnesses += 1
    assert counts == Counter({
        'simple_connected':1472,
        'fully_liftable':192,
        'identity':160,
        'nontrivial':32
    }), counts
    assert nontrivial_witnesses == 32
    print('N8_LABELLED_CONNECTED_1472_FIVE_LOOP_192_TRIVIAL_160_NONTRIVIAL_32 PASS')
    # For n=8, m=(3n-6)/2=9 and beta=m-n+1=2; fibre bound 2^(2*beta)=16.
    assert len(actual_fibre) == 2 <= (1 << (8-4))
    print('ALL_N_FIXED_BOUNDARY_FIBRE_EMBEDS_GF2_CYCLE_SPACE_DIM_N_MINUS_4')
    print('GLOBAL_GOOD_ONLY_SIXPOLE_NO_GO=OPEN; SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN')


if __name__ == '__main__':
    run()
