#!/usr/bin/env python3
"""
Finite symbolic sanity checks for B2B1 forced-color class return.

Not a theorem prover. It verifies the finite color-mask facts used by the
source-structural proof for one forced color (R1) and an equal-color pair (R2).
"""

from itertools import combinations

COLORS = range(4)
FULL = (1 << 4) - 1

def pop(x): return x.bit_count()
def add_color(mask, c, adjacent):
    return mask | ((1 << c) if adjacent else 0)

def source_class(mask):
    # source list size = 4 - number of distinct seed colors seen
    return 4 - pop(mask)

def check_vi_single():
    # old Y adjacent to residual Y0: exactly one old seed color c0
    for c0 in COLORS:
        old = 1 << c0
        for forced in COLORS:
            for adj in (0,1):
                new = add_color(old, forced, adj)
                if source_class(new) == 3:  # remains Y
                    assert new == old
    return True

def check_vi_equal_pair():
    # equal-color pair contributes at most one new distinct seed color
    for c0 in COLORS:
        old = 1 << c0
        for forced in COLORS:
            for adj_u in (0,1):
                for adj_v in (0,1):
                    new = old
                    if adj_u or adj_v:
                        new |= 1 << forced
                    if source_class(new) == 3:
                        assert new == old
    return True

def check_old_classes_cannot_create_residual_Y():
    # old X sees 2 seed colors; adding one distinct forced color cannot make
    # it a 3-list Y. old Y0 sees 0 colors; hit by one/equal-pair color becomes
    # a 3-list Y, but B2B0 whole-component removal handles its residual adjacency.
    for old_mask in range(16):
        old_cls = source_class(old_mask)
        for forced in COLORS:
            new = old_mask | (1 << forced)
            new_cls = source_class(new)
            if old_cls == 2:  # old X
                assert new_cls <= 2
            if old_cls == 4:  # old Y0
                assert new_cls in (3,4)
    return True

def immediate_query_bound(n):
    r1 = 4*n
    r2 = 4*(n*(n-1)//2)
    return r1+r2

def main():
    assert check_vi_single()
    assert check_vi_equal_pair()
    assert check_old_classes_cannot_create_residual_Y()
    for n in range(1,20):
        assert immediate_query_bound(n) <= 2*n*n + 2*n
    print({
        "vi_single_mask_check": "PASS",
        "vi_equal_pair_mask_check": "PASS",
        "old_X_cannot_become_Y": "PASS",
        "old_Y0_hit_by_equal_color_has_at_most_one_new_seed_color": "PASS",
        "immediate_R1_R2_successor_bound": "O(n^2)",
        "global_recursion_tree_bound": "NOT_PROVED",
        "status": "PASS_FINITE_SANITY"
    })

if __name__ == "__main__":
    main()
