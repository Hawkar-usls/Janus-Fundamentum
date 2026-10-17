#!/usr/bin/env python3
"""Exact finite rooted F7/F7* census for frozen source controls.

This is a regression / hostile-control checker only.  It is not a proof of a
universal polynomial SAT algorithm.
"""
from itertools import combinations
import json


def gf2_rank(vecs):
    basis = {}
    for x in vecs:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in basis:
                y ^= basis[p]
            else:
                basis[p] = y
                break
    return len(basis)


def cols_from_supports(n, supports):
    out = []
    for supp in supports:
        v = 0
        for r in supp:
            assert 0 <= r < n
            v |= 1 << r
        out.append(v)
    return out


def exactone_models(n, cols):
    ans = []
    full = (1 << n) - 1
    for mask in range(1 << len(cols)):
        # Integer exact cover: selected supports pairwise disjoint and cover all rows.
        used = 0
        ok = True
        for j, col in enumerate(cols):
            if (mask >> j) & 1:
                if used & col:
                    ok = False
                    break
                used |= col
        if ok and used == full:
            ans.append(mask)
    return ans


def rooted_dual_fano_census(n, cols):
    """Count 7-element rooted F7 and F7* minors of [A|1].

    The root is kept.  Six original elements are kept; every other original
    element is independently deleted or contracted.

    F7 test: a simple rank-3 binary matroid on seven elements is necessarily
    PG(2,2)=F7.

    F7* test: rank 4, cycle-space dimension 3, and all seven nonzero cycles
    have size four.
    """
    b = (1 << n) - 1
    allcols = list(cols) + [b]
    root = len(cols)
    f7 = []
    f7s = []

    for keep_orig in combinations(range(len(cols)), 6):
        keep = list(keep_orig) + [root]
        removed = [i for i in range(len(cols)) if i not in keep_orig]
        for mask in range(1 << len(removed)):
            contracted = [removed[i] for i in range(len(removed)) if (mask >> i) & 1]
            deleted = [i for i in removed if i not in contracted]
            base = [allcols[i] for i in contracted]
            r0 = gf2_rank(base)
            rminor = gf2_rank(base + [allcols[i] for i in keep]) - r0

            if rminor == 3:
                simple = True
                for i in keep:
                    if gf2_rank(base + [allcols[i]]) - r0 != 1:
                        simple = False
                        break
                if simple:
                    for i, j in combinations(keep, 2):
                        if gf2_rank(base + [allcols[i], allcols[j]]) - r0 != 2:
                            simple = False
                            break
                if simple:
                    f7.append((tuple(keep_orig), tuple(contracted), tuple(deleted)))

            if rminor == 4:
                cycle_weights = []
                for sm in range(1, 1 << 7):
                    x = 0
                    for t in range(7):
                        if (sm >> t) & 1:
                            x ^= allcols[keep[t]]
                    if gf2_rank(base + [x]) == r0:
                        cycle_weights.append(sm.bit_count())
                if len(cycle_weights) == 7 and set(cycle_weights) == {4}:
                    f7s.append((tuple(keep_orig), tuple(contracted), tuple(deleted)))

    return f7, f7s


def fano_control():
    supports = [
        (0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)
    ]
    cols = cols_from_supports(7, supports)
    f7, f7s = rooted_dual_fano_census(7, cols)
    assert len(f7) == 7
    assert len(f7s) == 7
    assert len(exactone_models(7, cols)) == 0
    return {
        "n": 7,
        "rooted_F7": len(f7),
        "rooted_F7star": len(f7s),
        "first_F7": f7[0],
        "first_F7star": f7s[0],
        "exactone_models": 0,
    }


def affine9_control():
    pts = [(x,y) for y in range(3) for x in range(3)]
    idx = {p:i for i,p in enumerate(pts)}
    supports = []
    for x0 in range(3):
        supports.append(tuple(idx[(x0,y)] for y in range(3)))
    for y0 in range(3):
        supports.append(tuple(idx[(x,y0)] for x in range(3)))
    for c in range(3):
        supports.append(tuple(idx[(x,(x+c)%3)] for x in range(3)))
    cols = cols_from_supports(9, supports)
    f7, f7s = rooted_dual_fano_census(9, cols)
    models = exactone_models(9, cols)
    assert len(f7) == 0
    assert len(f7s) == 0
    assert len(models) == 3
    return {"n":9,"rooted_F7":0,"rooted_F7star":0,"exactone_models":3}


def sat12_control():
    supports = [
        (0,1,2),(3,4,5),(6,7,8),(9,10,11),
        (10,1,8),(11,2,3),(3,1,6),(10,4,0),
        (8,4,11),(9,5,6),(2,9,7),(7,5,0),
    ]
    cols = cols_from_supports(12, supports)
    f7, f7s = rooted_dual_fano_census(12, cols)
    models = exactone_models(12, cols)
    assert len(models) == 1
    assert len(f7) == 80
    assert len(f7s) == 144
    witness = [j for j in range(12) if (models[0] >> j) & 1]
    assert witness == [0,1,2,3]
    return {
        "n":12,
        "rooted_F7":len(f7),
        "rooted_F7star":len(f7s),
        "exactone_models":1,
        "unique_witness":witness,
        "first_F7":f7[0],
        "first_F7star":f7s[0],
    }


def main():
    out = {
        "status":"PASS_ROOTED_DUAL_FANO_SOURCE_CONTROLS",
        "scientific_ceiling":"FINITE_EXACT_CONTROLS_ONLY__NO_D1_PROMOTION__P_VS_NP_OPEN",
        "FANO_7_3":fano_control(),
        "AFFINE_3X3":affine9_control(),
        "SAT_12_3":sat12_control(),
        "conclusion":"dual-Fano intersection is source-generated and contains SAT instances",
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
