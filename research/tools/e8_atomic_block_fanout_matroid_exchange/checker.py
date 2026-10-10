from itertools import product


def det_mod(mat, p):
    a = [row[:] for row in mat]
    n = len(a)
    out = 1
    for c in range(n):
        pivot = next((r for r in range(c, n) if a[r][c] % p), None)
        if pivot is None:
            return 0
        if pivot != c:
            a[c], a[pivot] = a[pivot], a[c]
            out = (-out) % p
        pv = a[c][c] % p
        out = (out * pv) % p
        inv = pow(pv, -1, p)
        for r in range(c + 1, n):
            if a[r][c] % p:
                f = a[r][c] * inv % p
                for j in range(c, n):
                    a[r][j] = (a[r][j] - f * a[c][j]) % p
    return out % p


def columns_to_matrix(cols, chosen):
    r = len(cols[0])
    return [[cols[j][i] for j in chosen] for i in range(r)]


def exhaustive_r2(p):
    # Normalize B0 to identity. Enumerate every possible B1 over GF(p).
    r = 2
    b0 = [(1, 0), (0, 1)]
    checked = 0
    for vals in product(range(p), repeat=4):
        b1 = [(vals[0], vals[2]), (vals[1], vals[3])]
        cols = b0 + b1
        if det_mod(columns_to_matrix(cols, [2, 3]), p) == 0:
            continue
        checked += 1
        # Basis exchange predicts a hybrid basis replacing each B0 column.
        for e in range(r):
            hybrids = []
            for f in range(r):
                chosen = list(range(r))
                chosen[e] = r + f
                hybrids.append(det_mod(columns_to_matrix(cols, chosen), p) != 0)
            assert any(hybrids), (p, vals, e)
    assert checked > 0
    print(f"GF({p}) r=2: {checked} invertible B1 controls, exchange=PASS")


def random_structured_r3(p):
    # Deterministic sweep of invertible upper/lower-ish coordinate matrices.
    b0 = [(1,0,0), (0,1,0), (0,0,1)]
    cases = [
        [(1,0,0),(0,1,0),(0,0,1)],
        [(1,1,0),(0,1,1),(1,0,1)],
        [(1,1,1),(1,2%p,0),(0,1,1)],
    ]
    for b1 in cases:
        cols = b0 + b1
        if det_mod(columns_to_matrix(cols, [3,4,5]), p) == 0:
            continue
        for e in range(3):
            assert any(
                det_mod(columns_to_matrix(cols, [j if j != e else 3+f for j in range(3)]), p) != 0
                for f in range(3)
            )
    print(f"GF({p}) r=3 structured controls: exchange=PASS")


def main():
    for p in (2, 3, 5, 7):
        exhaustive_r2(p)
        random_structured_r3(p)
    print("PASS: finite replay agrees with basis-exchange fanout barrier")


if __name__ == '__main__':
    main()
