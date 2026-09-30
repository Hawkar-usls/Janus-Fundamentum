#!/usr/bin/env python3
"""Provider boundary probe: cardinality-local != NW-neighborhood-local."""


def cardinality_local(support, kappa):
    return len(support) <= kappa


def containing_neighborhood(support, neighborhoods):
    for i, neighborhood in enumerate(neighborhoods):
        if support <= neighborhood:
            return i
    return None


def nw_local(support, neighborhoods):
    return containing_neighborhood(support, neighborhoods) is not None


def main():
    neighborhoods = [{1,2}, {3,4}]
    mixed = {1,3}
    assert cardinality_local(mixed, 2)
    assert not nw_local(mixed, neighborhoods)

    neighborhoods2 = [{1,2,3,4}, {3,4,5,6}]
    g = {1,2}
    h = {2,4}
    assert containing_neighborhood(g, neighborhoods2) == 0
    assert containing_neighborhood(h, neighborhoods2) == 0
    s = g | h
    assert s <= neighborhoods2[0]
    assert nw_local(s, neighborhoods2)

    g2 = {1,2}
    h2 = {5,6}
    assert nw_local(g2, neighborhoods2)
    assert nw_local(h2, neighborhoods2)
    assert not nw_local(g2 | h2, neighborhoods2)

    print("C025_E2R_L1C_KAPPA_LOCAL_TO_NW_LOCAL_TRANSFER = REFUTED")
    print("C025_E2R_L1C_SAME_NEIGHBORHOOD_EXTENSION_CLOSURE = PASS")
    print("C025_E2R_L1C_DIFFERENT_NEIGHBORHOOD_ESCAPE = PASS")
    print("claim_boundary = locality transfer mechanics only; heavy-width theorem transfer remains open")


if __name__ == "__main__":
    main()
