#!/usr/bin/env python3
"""R5: exact 2-wire missing-colour multipole gates, not a global SCL lower bound.

Standalone Python 3.12, standard library only. Check ALL 3^5 4-pole and
ALL 3^9 6-pole colour assignments; independently assemble two 6-poles into
a simple cubic graph and verify the native square/cubic/linear SCL rows.

Mathematical theorems (separate human proof in paired research memo):
- Every cubic multipole's boundary colours XOR to zero in F2^2.
- For k pairs with distinct colours, missing-colour XOR is zero.
- 4 poles / 2 pairs must encode EQUAL missing colours.
- 6 poles / 3 pairs must encode ALL-DIFFERENT missing colours.
- For any k>=3, a pure k-way missing-colour copier is impossible:
  odd k by parity, even k>=4 by one two-colour Kempe-path swap.
Neither finite enumeration nor theorem yields an unbounded PC degree bound.
"""
from collections import Counter
from itertools import product

COLOURS = (0, 1, 2)
GF2X2 = (1, 2, 3)


def enumerate_multipole(internal_edges, ports, vertices):
    edges = list(internal_edges) + list(ports)
    incidence = {
        v: tuple(i for i, edge in enumerate(edges) if v in edge)
        for v in vertices
    }
    assert all(len(incidence[v]) == 3 for v in vertices)
    assert len(set(edges)) == len(edges)
    for colours in product(COLOURS, repeat=len(edges)):
        if all(len({colours[i] for i in incidence[v]}) == 3 for v in vertices):
            yield colours


def missing(left, right):
    assert left != right
    return next(c for c in COLOURS if c not in (left, right))


def check_affine_decoder(colours, port_a, port_b, internal):
    # The SCL vertex-colour row is a_c+b_c+y_c=1.
    # Hence the coded missing-colour indicator P_c=1-a_c-b_c equals y_c
    # as a literal GF(3) polynomial consequence of ONE source clause.
    for c in COLOURS:
        a, b, y = (int(colours[i] == c) for i in (port_a, port_b, internal))
        assert (1 - a - b - y) % 3 == 0
        assert 1 - a - b in (0, 1)


def four_pole():
    # K4 after removing two adjacent vertices: one internal edge uv and
    # two ports at each endpoint.
    inside = (("u", "v"),)
    ports = (("u", "L0"), ("u", "L1"), ("v", "R0"), ("v", "R1"))
    signatures = Counter()
    n = 0
    for x in enumerate_multipole(inside, ports, ("u", "v")):
        n += 1
        left, right = x[1:3], x[3:5]
        assert left[0] != left[1] and right[0] != right[1]
        assert missing(*left) == missing(*right) == x[0]
        assert GF2X2[left[0]] ^ GF2X2[left[1]] ^ GF2X2[right[0]] ^ GF2X2[right[1]] == 0
        check_affine_decoder(x, 1, 2, 0)
        check_affine_decoder(x, 3, 4, 0)
        signatures[(left, right)] += 1
    assert n == 12
    assert len(signatures) == 12
    assert set(signatures.values()) == {1}
    print("FOUR_POLE: 3^5=243 checked; 12 valid; two-wire EQUALITY PASS")


def six_pole():
    # K3,3 with two vertices of the same partition deleted:
    # an internal 3-star and six ports, two at each leaf.
    inside = (("c", "u"), ("c", "v"), ("c", "w"))
    ports = (
        ("u", "u0"), ("u", "u1"),
        ("v", "v0"), ("v", "v1"),
        ("w", "w0"), ("w", "w1"),
    )
    signatures = Counter()
    n = 0
    for x in enumerate_multipole(inside, ports, ("c", "u", "v", "w")):
        n += 1
        pairs = (x[3:5], x[5:7], x[7:9])
        assert all(a != b for a, b in pairs)
        decoded = tuple(missing(*pair) for pair in pairs)
        assert len(set(decoded)) == 3
        assert decoded == x[:3]
        assert GF2X2[decoded[0]] ^ GF2X2[decoded[1]] ^ GF2X2[decoded[2]] == 0
        assert 0 == __import__("functools").reduce(
            lambda a, b: a ^ b, (GF2X2[colour] for colour in x[3:]), 0
        )
        for leaf in range(3):
            check_affine_decoder(x, 3 + 2 * leaf, 4 + 2 * leaf, leaf)
        signatures[decoded] += 1
    assert n == 48
    assert len(signatures) == 6 and set(signatures.values()) == {8}
    print("SIX_POLE: 3^9=19683 checked; 48 valid; decoded ALL-DIFFERENT PASS")


def legal_native_scl(edges, vertices):
    # Original direct Holyer edge/colour indicator source, not a relaxation.
    norm = lambda e: tuple(sorted(e))
    edges = tuple(norm(e) for e in edges)
    assert len(set(edges)) == len(edges)
    assert all(u != v for u, v in edges)
    assert set(v for edge in edges for v in edge) == set(vertices)
    assert all(sum(v in e for e in edges) == 3 for v in vertices)
    rows = []
    for edge in edges:
        rows.append(frozenset((edge, c) for c in COLOURS))
    for v in vertices:
        for c in COLOURS:
            rows.append(frozenset((e, c) for e in edges if v in e))
    n = 3 * len(edges)
    vars_ = set().union(*rows)
    counts = Counter(x for row in rows for x in row)
    assert n == len(vars_) == len(rows)
    assert all(len(row) == 3 for row in rows)
    assert set(counts.values()) == {3}
    assert all(len(a & b) <= 1 for i, a in enumerate(rows) for b in rows[i + 1:])
    return rows, edges


def check_closed_two_stars():
    # Glue two 6-pole stars by a 6-cycle across their 3+3 leaves,
    # avoiding parallel edges. The resulting graph is the cube graph.
    edges = (
        (0, 1), (0, 2), (0, 3),
        (4, 5), (4, 6), (4, 7),
        (1, 5), (1, 6), (2, 6), (2, 7), (3, 7), (3, 5),
    )
    rows, edges = legal_native_scl(edges, tuple(range(8)))
    incident = {
        v: tuple(j for j, e in enumerate(edges) if v in e)
        for v in range(8)
    }
    colours = [-1] * len(edges)
    n = 0

    def dfs(i):
        nonlocal n
        if i == len(edges):
            n += 1
            witness = frozenset((edge, colours[j]) for j, edge in enumerate(edges))
            assert all(len(row & witness) == 1 for row in rows)
            return
        for c in COLOURS:
            if all(colours[j] != c for v in edges[i] for j in incident[v] if j != i):
                colours[i] = c
                dfs(i + 1)
                colours[i] = -1

    dfs(0)
    assert n == 24
    print("CLOSED_CUBE: 8 vertices, 12 edges, native legal SCL36; 24 source witnesses PASS")


def main():
    four_pole()
    six_pole()
    check_closed_two_stars()
    print("GATES: local encodings PROVED; 6-regular 3COL->SCL degree transfer OPEN;")
    print("       unbounded native PC degree OPEN; P vs NP OPEN")


if __name__ == "__main__":
    main()
