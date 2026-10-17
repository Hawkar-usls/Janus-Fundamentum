from itertools import product


def det_mod2(A):
    A = [row[:] for row in A]
    n = len(A)
    r = 0
    for c in range(n):
        p = next((i for i in range(r, n) if A[i][c] & 1), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(n):
            if i != r and (A[i][c] & 1):
                A[i] = [x ^ y for x, y in zip(A[i], A[r])]
        r += 1
    return 1 if r == n else 0


def sat_eval(formula, a):
    for clause in formula:
        ok = False
        for lit in clause:
            v = a[abs(lit)]
            ok |= bool(v if lit > 0 else 1 - v)
        if not ok:
            return False
    return True


def clause_block(clause, a):
    fs = []
    for lit in clause:
        v = a[abs(lit)]
        fs.append((1 ^ v) if lit > 0 else v)
    f1, f2, f3 = fs
    return [[1, f1, 0], [0, 1, f2], [f3, 0, 1]]


def blockdiag(blocks):
    n = sum(len(b) for b in blocks)
    M = [[0] * n for _ in range(n)]
    s = 0
    for B in blocks:
        k = len(B)
        for i in range(k):
            for j in range(k):
                M[s+i][s+j] = B[i][j] & 1
        s += k
    return M


def matrix_for(formula, a):
    return blockdiag([clause_block(c, a) for c in formula])


def brute_check(formula):
    vars_ = sorted({abs(l) for c in formula for l in c})
    any_sat = False
    any_nonsing = False
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        s = sat_eval(formula, a)
        d = det_mod2(matrix_for(formula, a))
        assert d == int(s), (formula, a, s, d)
        any_sat |= s
        any_nonsing |= bool(d)
    assert any_sat == any_nonsing
    print(f'clauses={len(formula)} vars={len(vars_)} SAT={int(any_sat)} NONSING={int(any_nonsing)} PASS')


def main():
    controls = [
        [(1, 2, 3)],
        [(1, 2, 3), (-1, 2, -3)],
        [(1, -2, 3), (1, 2, 4), (-2, 3, 4)],
        [(1, 2, 3), (-1, 2, 3), (1, -2, 3), (1, 2, -3),
         (-1, -2, 3), (-1, 2, -3), (1, -2, -3), (-1, -2, -3)],
    ]
    for f in controls:
        brute_check(f)
    print('PASS: over GF(2), the clause-block affine determinant is exactly the 3-CNF satisfaction indicator')


if __name__ == '__main__':
    main()
