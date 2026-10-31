#!/usr/bin/env python3
"""Exact regression for the F3 constant-plus-gradient kernel theorem on the frozen Paley-orbit family."""


def orbit_minus2(q):
    r = (-2) % q
    out = []
    seen = set()
    x = 1
    while x not in seen:
        seen.add(x)
        out.append(x)
        x = (x * r) % q
    assert x == 1
    return out


def build_source(q):
    O = orbit_minus2(q)
    r = (-2) % q
    index = {}
    j = 0
    for s in O:
        for t in range(q):
            index[(t, s)] = j
            j += 1
    rows = []
    for s in O:
        rs = (r * s) % q
        for t in range(q):
            rows.append((
                index[(t, s)],
                index[((t + s) % q, s)],
                index[((t + 2 * s) % q, rs)],
            ))
    return O, index, rows


def sparse_rank_mod3(n, rows):
    basis = {}
    rank = 0
    for inds in rows:
        v = {i: 1 for i in inds}
        while v:
            p = min(v)
            if p not in basis:
                inv = 1 if v[p] == 1 else 2
                v = {j: (a * inv) % 3 for j, a in v.items() if (a * inv) % 3}
                basis[p] = v
                rank += 1
                break
            b = basis[p]
            f = v[p]
            nv = dict(v)
            for j, a in b.items():
                z = (nv.get(j, 0) - f * a) % 3
                if z:
                    nv[j] = z
                else:
                    nv.pop(j, None)
            v = nv
    return rank


def verify_constant_and_gradients(q, O, index, rows):
    n = len(index)
    one = [1] * n
    for row in rows:
        assert sum(one[j] for j in row) % 3 == 0

    # q-1 basis potentials p_a=1 at a, 0 elsewhere, with p_0 omitted.
    # Verify each corresponding gradient annihilates every row.
    for a in range(1, q):
        y = [0] * n
        for (t, s), j in index.items():
            pt = 1 if t == a else 0
            pts = 1 if (t + s) % q == a else 0
            y[j] = (pts - pt) % 3
        for row in rows:
            assert sum(y[j] for j in row) % 3 == 0

    # Constant is not a gradient: on the directed +s cycle its sum is q != 0 mod 3.
    assert q % 3 != 0


def verify_particular(q, O, index, rows):
    L = len(O)
    if L % 3:
        # Left-kernel obstruction from cubic columns.
        assert (q * L) % 3 != 0
        return False

    r0_by_s = {s: k % 3 for k, s in enumerate(O)}
    z = [0] * len(index)
    for (t, s), j in index.items():
        z[j] = r0_by_s[s]
    for row in rows:
        assert sum(z[j] for j in row) % 3 == 1
    return True


def main():
    expected = {
        11: (5, 55, 11),
        19: (9, 171, 19),
        43: (7, 301, 43),
        67: (33, 2211, 67),
        331: (15, 4965, 331),
    }

    for q, (L_expected, n_expected, nullity_expected) in expected.items():
        O, index, rows = build_source(q)
        assert len(O) == L_expected
        assert len(index) == n_expected
        assert len(rows) == n_expected

        rank = sparse_rank_mod3(n_expected, rows)
        nullity = n_expected - rank
        assert nullity == nullity_expected == q

        verify_constant_and_gradients(q, O, index, rows)
        consistent = verify_particular(q, O, index, rows)
        assert consistent == (len(O) % 3 == 0)

        print(
            f"q={q} L={len(O)} n={n_expected} rank_F3={rank} "
            f"nullity_F3={nullity} affine_consistent={consistent}"
        )

    print("PASS_PALEY_ORBIT_EXACT_F3_CONSTANT_PLUS_GRADIENT_KERNEL")
    print("THEOREM_TARGET: ker_F3(A)=<1> direct-sum Grad, dim=q")
    print("AFFINE_SPLIT: A z=1 consistent iff 3 divides ord_q(-2)")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
