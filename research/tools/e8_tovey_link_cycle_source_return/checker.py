#!/usr/bin/env python3
"""Exact finite regression for the Tovey link-cycle witness source-return theorem.

The symbolic proof is in the companion JSON.  This checker exhaustively verifies,
for copy cycles up to length 7 and every inherited-sign/selection pattern, that a
conflict-free selection of one witness from every link clause exists iff all
selected inherited occurrences use at most one sign.  It also verifies that every
conflict-free link-only selection is constant around the cycle.
"""

from itertools import product


def link_selection_conflict_free(y):
    k = len(y)
    # Copy i gets positive from outgoing C_i iff y_i=1, and negative from
    # incoming C_{i-1} iff y_{i-1}=0.
    return all(not (y[i] == 1 and y[(i - 1) % k] == 0) for i in range(k))


def full_selection_conflict_free(y, inherited_signs, selected):
    k = len(y)
    if not link_selection_conflict_free(y):
        return False
    for i in range(k):
        pos = y[i] == 1
        neg = y[(i - 1) % k] == 0
        if selected[i]:
            if inherited_signs[i] == 1:
                pos = True
            else:
                neg = True
        if pos and neg:
            return False
    return True


def inherited_is_sign_consistent(inherited_signs, selected):
    used = {inherited_signs[i] for i, bit in enumerate(selected) if bit}
    return len(used) <= 1


def main():
    patterns = 0
    feasible_patterns = 0
    for k in range(2, 8):
        ys = list(product((0, 1), repeat=k))

        # Link-only theorem: the only conflict-free cycle choices are all-0/all-1.
        good_y = [y for y in ys if link_selection_conflict_free(y)]
        assert set(good_y) == {tuple([0] * k), tuple([1] * k)}

        for signs in product((-1, 1), repeat=k):
            for selected in product((0, 1), repeat=k):
                expected = inherited_is_sign_consistent(signs, selected)
                actual = any(full_selection_conflict_free(y, signs, selected) for y in ys)
                assert actual == expected, (k, signs, selected, actual, expected)
                patterns += 1
                feasible_patterns += int(actual)

    print("PASS_TOVEY_LINK_CYCLE_WITNESS_SOURCE_RETURN")
    print("cycle_lengths_tested=2..7")
    print(f"inherited_patterns_tested={patterns}")
    print(f"feasible_sign_consistent_patterns={feasible_patterns}")
    print("link_only_choices_per_cycle=2")
    print("eliminated_relation=ORIGINAL_GLOBAL_SIGN_CONSISTENCY")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
