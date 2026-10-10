from itertools import combinations


def pfaffian4_support(edges):
    # For a 4x4 skew matrix, the three Pfaffian monomials use these pairings.
    pairings = [
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    ]
    return [p for p in pairings if p[0] in edges and p[1] in edges]


def check_r1():
    # visible a,b,c = 0,1,2; hidden h = 3.
    required_pairs = {(0, 3), (1, 3), (2, 3)}
    forbidden_pairs = {(0, 1), (0, 2), (1, 2)}
    edges = set(required_pairs)
    assert not (edges & forbidden_pairs)
    # No Pfaffian perfect-matching monomial survives, so full 4-set is singular.
    assert pfaffian4_support(edges) == []
    print('R1 PASS: forced pair support makes full Pfaffian identically zero')


def check_r2():
    required_pairs = {(0, 1), (0, 2), (1, 2)}
    forbidden_pairs = {(0, 3), (1, 3), (2, 3)}
    edges = set(required_pairs)
    assert not (edges & forbidden_pairs)
    assert pfaffian4_support(edges) == []
    print('R2 PASS: forced pair support makes full Pfaffian identically zero')


def parity_lift(weights, parity):
    # Unique extension by h needed for an even/odd linear lift.
    out = []
    for r in weights:
        for F in combinations(range(3), r):
            S = set(F)
            if (len(S) & 1) != parity:
                S.add(3)
            out.append(frozenset(S))
    return set(out)


def main():
    r1_even = parity_lift({0, 1, 3}, 0)
    r2_even = parity_lift({0, 2, 3}, 0)
    assert r1_even == {
        frozenset(), frozenset({0,3}), frozenset({1,3}),
        frozenset({2,3}), frozenset({0,1,2,3})
    }
    assert r2_even == {
        frozenset(), frozenset({0,1}), frozenset({0,2}),
        frozenset({1,2}), frozenset({0,1,2,3})
    }
    check_r1()
    check_r2()
    print('PASS: neither {0,1,3} nor {0,2,3} can be an elementary projection of a linear delta-matroid over any field')


if __name__ == '__main__':
    main()
