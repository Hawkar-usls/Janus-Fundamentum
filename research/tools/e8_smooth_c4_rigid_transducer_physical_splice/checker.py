#!/usr/bin/env python3
"""Exact replay for v8.0 two-copy physical three-edge splice branching."""

from itertools import permutations, product

D = range(3)
S3 = list(permutations(D))
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
FREE = (0, 2, 3)
PI = {0: 1, 1: 0, 2: 2}
H = {
    0: (0, 2, 1),
    1: (0, 2, 1),
    2: (1, 2, 0),
}


def compose(p, q):
    return tuple(p[q[i]] for i in D)


def inverse(p):
    out = [0, 0, 0]
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def F(state):
    tau, g = state
    return (PI[tau], compose(g, inverse(H[tau])))


def color(state, port):
    tau, g = state
    return g[REPS[tau][port]]


def relation_for_matching(target_order):
    states = list(product(D, S3))
    full = {s: set() for s in states}
    quotient = {}

    for left_outer in states:
        left_inner = F(left_outer)
        for right_inner in states:
            if not all(
                color(left_inner, p) != color(right_inner, q)
                for p, q in zip(FREE, target_order)
            ):
                continue
            right_outer = F(right_inner)
            full[left_outer].add(right_outer)
            ta, ga = left_outer
            tb, gb = right_outer
            hab = compose(inverse(gb), ga)
            quotient.setdefault((ta, tb), set()).add(hab)
    return full, quotient


def main():
    states = list(product(D, S3))
    assert len(states) == 18
    assert len(set(F(s) for s in states)) == 18

    expected = {
        (0, 2, 3): (132, {6, 8}, 22, {2, 3}),
        (0, 3, 2): (84, {4, 6}, 14, {1, 2}),
        (2, 0, 3): (132, {6, 8}, 22, {2, 3}),
        (2, 3, 0): (84, {4, 6}, 14, {1, 2}),
        (3, 0, 2): (84, {4, 6}, 14, {1, 2}),
        (3, 2, 0): (84, {4, 6}, 14, {1, 2}),
    }

    for target_order in permutations(FREE):
        full, quotient = relation_for_matching(target_order)
        full_count = sum(len(v) for v in full.values())
        row_sizes = {len(v) for v in full.values()}
        quotient_count = sum(len(v) for v in quotient.values())
        gain_sizes = {len(v) for v in quotient.values()}
        assert (full_count, row_sizes, quotient_count, gain_sizes) == expected[target_order]
        assert set(quotient) == {(a, b) for a in D for b in D}
        assert not all(len(v) == 1 for v in full.values())
        assert full_count == 6 * quotient_count

    # Explicit four-output branching witness for target order (0,3,2).
    full, quotient = relation_for_matching((0, 3, 2))
    input_state = (0, (0, 1, 2))
    expected_outputs = {
        (0, (2, 1, 0)),
        (1, (2, 0, 1)),
        (2, (0, 1, 2)),
        (2, (0, 2, 1)),
    }
    assert full[input_state] == expected_outputs

    representative_sizes = {
        pair: len(gains) for pair, gains in quotient.items()
    }
    assert representative_sizes == {
        (0, 0): 1, (0, 1): 1, (0, 2): 2,
        (1, 0): 1, (1, 1): 1, (1, 2): 2,
        (2, 0): 2, (2, 1): 2, (2, 2): 2,
    }

    print("PASS: all 6 perfect matchings of free ports {0,2,3} exhausted")
    print("PASS: every physical splice has FULL_3x3 orbit projection")
    print("PASS: four matchings give 84 full-state pairs / 14 quotient triples")
    print("PASS: two matchings give 132 full-state pairs / 22 quotient triples")
    print("PASS: no splice preserves a functional 18-state transducer")
    print("PASS: explicit input state has exactly four legal outputs in 14-triple class")
    print("VERDICT: PHYSICAL_SPLICE_CREATES_SET_VALUED_S3_GAIN_BRANCHING")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
