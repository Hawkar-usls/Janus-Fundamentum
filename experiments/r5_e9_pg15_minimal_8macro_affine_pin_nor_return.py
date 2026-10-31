#!/usr/bin/env python3
"""Exact PG15 AF3 macro-arity census and conditioned NOR-return checker."""

from itertools import combinations, product

P = 3
SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]


def source():
    return [[int(j + 1 in row) for j in range(15)] for row in SAT_ROWS]


def rref(M):
    A = [[x % P for x in row] for row in M]
    m = len(A); n = len(A[0]); piv = []; r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if A[i][c]), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, P)
        A[r] = [(x * inv) % P for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % P for j in range(n)]
        piv.append(c)
        r += 1
        if r == m:
            break
    return A, piv


def rank_rows(rows, ncols):
    if not rows:
        return 0
    _, piv = rref([list(row) for row in rows])
    return sum(c < ncols for c in piv)


def affine_dim(points):
    if not points:
        return -1
    base = points[0]
    diffs = [tuple((x - b) % P for x, b in zip(pt, base)) for pt in points[1:]]
    return rank_rows(diffs, len(base))


def nullspace_basis(rows, ncols):
    if not rows:
        return [tuple(1 if i == j else 0 for i in range(ncols)) for j in range(ncols)]
    R, piv_all = rref([list(row) for row in rows])
    piv = [c for c in piv_all if c < ncols]
    free = [c for c in range(ncols) if c not in piv]
    out = []
    for f in free:
        x = [0] * ncols
        x[f] = 1
        for i, c in enumerate(piv):
            x[c] = (-R[i][f]) % P
        out.append(tuple(x))
    return out


def enumerate_affine_solutions():
    A = source()
    RR, piv = rref([A[i] + [1] for i in range(15)])
    assert piv == list(range(11))
    free = [11, 12, 13, 14]
    sols = []
    params = []
    for vals in product(range(P), repeat=4):
        x = [0] * 15
        for j, v in zip(free, vals):
            x[j] = v
        for row, c in enumerate(piv):
            rhs = RR[row][15]
            s = sum(RR[row][j] * x[j] for j in free) % P
            x[c] = (rhs - s) % P
        assert all(sum(A[i][j] * x[j] for j in range(15)) % P == 1 for i in range(15))
        sols.append(tuple(x))
        params.append(tuple(vals))
    assert len(set(sols)) == 81
    return A, RR, free, params, sols


def main():
    A, RR, free, params, sols = enumerate_affine_solutions()

    assert len(free) == 4
    assert len(sols) == 3 ** 4

    nowhere_zero = [s for s in sols if all(v != 0 for v in s)]
    assert len(nowhere_zero) == 4

    arity_hist = {}
    compressing8 = []
    for k in range(9):
        hist = {}
        for S in combinations(range(15), k):
            pts = [params[i] for i, s in enumerate(sols) if all(s[j] != 0 for j in S)]
            d = affine_dim(pts)
            hist[d] = hist.get(d, 0) + 1
            if k == 8 and d == 3:
                compressing8.append((tuple(S), pts))
        arity_hist[k] = hist

    for k in range(8):
        assert arity_hist[k] == {4: 1 if k == 0 else __import__('math').comb(15, k)}
    assert arity_hist[8] == {4: 6427, 3: 8}

    core = {2,3,6,8,9,12,13}
    triggers = {0,1,4,5,7,10,11,14}
    expected = {tuple(sorted(core | {j})) for j in triggers}
    observed = {S for S, _ in compressing8}
    assert observed == expected

    # Derive the common forced affine equation from each 8-macro survivor set.
    common_normals = set()
    survivor_counts = set()
    for S, pts in compressing8:
        survivor_counts.add(len(pts))
        base = pts[0]
        diffs = [tuple((x - b) % P for x, b in zip(pt, base)) for pt in pts[1:]]
        ns = nullspace_basis(diffs, 4)
        assert len(ns) == 1
        n = ns[0]
        # Canonicalize the nonzero normal by making its last nonzero coordinate 1.
        last = max(i for i, x in enumerate(n) if x)
        inv = pow(n[last], -1, P)
        n = tuple((x * inv) % P for x in n)
        b = sum(n[i] * base[i] for i in range(4)) % P
        common_normals.add((n, b))
    assert survivor_counts == {5}
    assert common_normals == {((2,2,2,1), 0)}

    # In the RREF chart, r4 (zero-based index 3) is exactly
    # 1 + 2*t0 + 2*t1 + 2*t2 + t3.
    zero = params.index((0,0,0,0))
    const_r4 = sols[zero][3]
    coeff_r4 = []
    for e in range(4):
        u = [0,0,0,0]; u[e] = 1
        coeff_r4.append((sols[params.index(tuple(u))][3] - const_r4) % P)
    assert const_r4 == 1
    assert tuple(coeff_r4) == (2,2,2,1)
    for _, pts in compressing8:
        for t in pts:
            s = sols[params.index(t)]
            assert s[3] == 1

    # Seven-core plus one-trigger exact normal form.
    core_pts = [s for s in sols if all(s[j] != 0 for j in core)]
    assert len(core_pts) == 9
    exceptional = [s for s in core_pts if s[3] != 1]
    assert len(exceptional) == 1
    ex = exceptional[0]
    assert ex[3] == 2
    assert all(ex[j] == 0 for j in triggers)
    assert all(s[3] == 1 for s in core_pts if s is not ex)

    # Condition on the proved macro pin r4=1.
    pinned = [(params[i], s) for i, s in enumerate(sols) if s[3] == 1]
    assert len(pinned) == 27
    assert affine_dim([t for t, _ in pinned]) == 3
    for t, _ in pinned:
        assert t[3] == (t[0] + t[1] + t[2]) % P

    # The globally nowhere-zero residual becomes exactly a Boolean NOR graph.
    valid_bits = set()
    for t, s in pinned:
        if not all(v != 0 for v in s):
            continue
        u = t[:3]
        assert all(v in (1,2) for v in u)
        bits = tuple(v - 1 for v in u)
        valid_bits.add(bits)
    expected_nor = {(0,0,1),(0,1,0),(0,1,1),(1,0,0)}
    assert valid_bits == expected_nor
    assert all(b0 == int(not (b1 or b2)) for b0,b1,b2 in valid_bits)

    print("PASS_PG15_MINIMAL_8MACRO_AFFINE_PIN_NOR_RETURN")
    print("rank_F3_A=11 affine_dimension=4 affine_points=81 nowhere_zero_points=4")
    for k in range(9):
        print(f"arity_{k}_affine_dim_hist={arity_hist[k]}")
    print("minimal_affine_implication_arity=8")
    print("compressing_arity8_subsets=8")
    print("seven_core_zero_based=2,3,6,8,9,12,13")
    print("trigger_zero_based=0,1,4,5,7,10,11,14")
    print("common_forced_parameter_equation=2*t0+2*t1+2*t2+t3=0")
    print("common_source_pin_one_based=r4=1")
    print("conditioned_boolean_relation={(0,0,1),(0,1,0),(0,1,1),(1,0,0)}")
    print("conditioned_boolean_relation_name=NOR(b1,b2)->b0")
    print("NOR_SOURCE_PRESERVING_COMPOSITION=OPEN")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == '__main__':
    main()
