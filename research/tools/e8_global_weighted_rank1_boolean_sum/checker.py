from itertools import product
from fractions import Fraction


def det(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    n = len(a)
    out = Fraction(1)
    for c in range(n):
        pivot = next((r for r in range(c, n) if a[r][c] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != c:
            a[c], a[pivot] = a[pivot], a[c]
            out *= -1
        pv = a[c][c]
        out *= pv
        for j in range(c, n):
            a[c][j] /= pv
        for r in range(c + 1, n):
            f = a[r][c]
            if f:
                for j in range(c, n):
                    a[r][j] -= f * a[c][j]
    return out


def add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def outer(u, v, scale=1):
    return [[scale * u[i] * v[j] for j in range(len(v))] for i in range(len(u))]


def check_case(M, U, V, weights):
    m = len(M)
    n = len(weights)
    lhs = Fraction(0)
    for bits in product((0, 1), repeat=n):
        X = [row[:] for row in M]
        w = Fraction(1)
        for i, bit in enumerate(bits):
            if bit:
                X = add(X, outer(U[i], V[i]))
                w *= weights[i]
        lhs += w * det(X)

    N = m + n
    B = [[Fraction(0) for _ in range(N)] for _ in range(N)]
    for i in range(m):
        for j in range(m):
            B[i][j] = M[i][j]
    for k in range(n):
        for i in range(m):
            B[i][m+k] = U[k][i]
            B[m+k][i] = -weights[k] * V[k][i]
        B[m+k][m+k] = 1 + weights[k]
    rhs = det(B)
    assert lhs == rhs, (lhs, rhs)
    return lhs


def main():
    cases = [
        (
            [[2,1],[1,3]],
            [[1,0],[1,1],[0,1]],
            [[1,2],[2,-1],[1,1]],
            [1,1,1],
        ),
        (
            [[1,2,0],[0,1,1],[2,0,1]],
            [[1,0,0],[0,1,0],[0,0,1],[1,1,0]],
            [[1,1,0],[0,1,1],[1,0,1],[1,-1,2]],
            [-1,2,-2,3],
        ),
        (
            [[0,1],[1,0]],
            [[1,0],[0,1]],
            [[1,1],[1,-1]],
            [-1,-1],
        ),
    ]
    for i, case in enumerate(cases, 1):
        value = check_case(*case)
        print(f'case={i}: PASS value={value}')
    print('PASS: weighted 2^n Boolean rank-one update sum equals one augmented determinant')


if __name__ == '__main__':
    main()
