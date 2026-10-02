#!/usr/bin/env python3
"""Exact finite rooted-F7* source controls.

Scientific ceiling: finite regression/control only.  It proves neither a universal
rooted-F7* contraction nor P=NP.
"""
from itertools import combinations
import json


def rank_vecs(vecs):
    basis = {}
    for x in vecs:
        y = x
        while y:
            b = y.bit_length() - 1
            if b in basis:
                y ^= basis[b]
            else:
                basis[b] = y
                break
    return len(basis)


def span_set(vecs):
    out = {0}
    for v in vecs:
        out |= {x ^ v for x in list(out)}
    return out


def A_from_colblocks(blocks, n):
    return [[1 if i in blocks[j] else 0 for j in range(n)] for i in range(n)]


def check_linear_cubic(blocks, n):
    assert len(blocks) == n
    deg = [0] * n
    used_pairs = set()
    for B in blocks:
        assert len(B) == 3 and len(set(B)) == 3
        for v in B:
            deg[v] += 1
        for p in combinations(sorted(B), 2):
            assert p not in used_pairs
            used_pairs.add(p)
    assert deg == [3] * n


def exactone_witnesses(A):
    n = len(A[0])
    out = []
    for mask in range(1 << n):
        ok = True
        for row in A:
            s = sum(row[j] * ((mask >> j) & 1) for j in range(n))
            if s != 1:
                ok = False
                break
        if ok:
            out.append(mask)
    return out


def augmented_columns(A):
    n = len(A)
    cols = [sum((A[i][j] & 1) << i for i in range(n)) for j in range(n)]
    return cols + [(1 << n) - 1]


def f7star_minor_fingerprint(aug, keep, contract):
    """Return (is_F7star, cycles) for M/contract restricted to keep.

    `keep` has exactly seven element indices and includes the root.
    Deleted elements do not enter this computation.
    """
    assert len(keep) == 7
    cvec = [aug[i] for i in contract]
    kv = [aug[i] for i in keep]
    rC = rank_vecs(cvec)
    if rank_vecs(cvec + kv) - rC != 4:
        return False, []
    cspan = span_set(cvec)
    cycles = []
    for sm in range(1, 1 << 7):
        x = 0
        S = []
        for t, i in enumerate(keep):
            if (sm >> t) & 1:
                x ^= aug[i]
                S.append(i)
        if x in cspan:
            cycles.append(S)
    good = len(cycles) == 7 and all(len(S) == 4 for S in cycles)
    return good, cycles


def rooted_minor_census(A, stop_after=None):
    n = len(A)
    aug = augmented_columns(A)
    root = n
    found = []
    # A seven-element rooted minor consists of root + six original elements.
    for keep6 in combinations(range(n), 6):
        keep = list(keep6) + [root]
        removed = [i for i in range(n) if i not in keep6]
        for bits in range(1 << len(removed)):
            contract = [removed[t] for t in range(len(removed)) if (bits >> t) & 1]
            delete = [i for i in removed if i not in contract]
            good, cycles = f7star_minor_fingerprint(aug, keep, contract)
            if good:
                found.append({
                    "keep": tuple(keep6),
                    "contract": tuple(contract),
                    "delete": tuple(delete),
                    "cycles": cycles,
                })
                if stop_after is not None and len(found) >= stop_after:
                    return found
    return found


def fano_control():
    blocks = [
        (0,1,2), (0,3,4), (0,5,6),
        (1,3,5), (1,4,6), (2,3,6), (2,4,5),
    ]
    check_linear_cubic(blocks, 7)
    A = A_from_colblocks(blocks, 7)
    aug = augmented_columns(A)
    root = 7
    deletion_witnesses = []
    for j in range(7):
        keep = [i for i in range(8) if i != j]
        good, cycles = f7star_minor_fingerprint(aug, keep, [])
        if good:
            deletion_witnesses.append(j)
    assert deletion_witnesses == list(range(7))
    assert exactone_witnesses(A) == []
    return {"rooted_F7star_deletion_witnesses": deletion_witnesses}


def affine9_control():
    pts = [(x,y) for x in range(3) for y in range(3)]
    blocks = []
    for c in range(3):
        blocks.append(tuple(i for i,(x,y) in enumerate(pts) if x == c))
    for c in range(3):
        blocks.append(tuple(i for i,(x,y) in enumerate(pts) if y == c))
    for c in range(3):
        blocks.append(tuple(i for i,(x,y) in enumerate(pts) if (y-x) % 3 == c))
    check_linear_cubic(blocks, 9)
    A = A_from_colblocks(blocks, 9)
    w = exactone_witnesses(A)
    assert len(w) == 3
    minors = rooted_minor_census(A)
    assert minors == []
    return {"exactone_models": 3, "rooted_F7star_minors": 0, "scenarios": 672}


def sat12_control():
    blocks = [
        (0,1,2),
        (3,4,5),
        (6,7,8),
        (9,10,11),
        (10,1,8),
        (11,2,3),
        (3,1,6),
        (10,4,0),
        (8,4,11),
        (9,5,6),
        (2,9,7),
        (7,5,0),
    ]
    check_linear_cubic(blocks, 12)
    A = A_from_colblocks(blocks, 12)
    w = exactone_witnesses(A)
    supports = [tuple(i for i in range(12) if (mask >> i) & 1) for mask in w]
    assert supports == [(0,1,2,3)]

    minors = rooted_minor_census(A)
    assert len(minors) == 144

    target = next(m for m in minors
                  if m["keep"] == (1,2,3,4,5,7)
                  and m["contract"] == (0,6,10,11)
                  and m["delete"] == (8,9))
    expected_cycles = {
        (2,3,4,5),
        (1,2,4,7),
        (1,3,5,7),
        (1,2,3,12),
        (1,4,5,12),
        (3,4,7,12),
        (2,5,7,12),
    }
    assert {tuple(S) for S in target["cycles"]} == expected_cycles
    return {
        "exactone_models": 1,
        "unique_witness": [0,1,2,3],
        "rooted_F7star_minors": len(minors),
        "explicit_minor": {
            "keep_original": list(target["keep"]),
            "contract": list(target["contract"]),
            "delete": list(target["delete"]),
            "cycle_weights": [len(S) for S in target["cycles"]],
        },
    }


def main():
    out = {
        "status": "PASS_ROOTED_F7STAR_SOURCE_CONTROLS",
        "scientific_ceiling": "FINITE_EXACT_CONTROLS_ONLY__NO_D1_PROMOTION__P_VS_NP_OPEN",
        "FANO_7_3": fano_control(),
        "AFFINE_3X3": affine9_control(),
        "SAT_12_3": sat12_control(),
        "conclusion": "rooted F7* is source-generated and its presence is not an UNSAT certificate",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
