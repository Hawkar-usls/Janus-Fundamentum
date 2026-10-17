#!/usr/bin/env python3
"""Exact finite regression for the augmented-ternary branch-boundary DP.

The arbitrary-size recurrence is proved in the companion research note.
This checker deliberately uses tiny matrices and brute span enumeration so the
implementation is transparent and independent of external matroid libraries.
"""

from itertools import product

P = 3


def balanced_tree(indices):
    indices = tuple(indices)
    if len(indices) == 1:
        return (indices, None, None)
    mid = len(indices) // 2
    left = balanced_tree(indices[:mid])
    right = balanced_tree(indices[mid:])
    return (indices, left, right)


def span_set(H, indices):
    m = len(H)
    cols = [[H[i][j] % P for i in range(m)] for j in indices]
    out = set()
    for coeff in product(range(P), repeat=len(cols)):
        v = [0] * m
        for a, col in zip(coeff, cols):
            for i in range(m):
                v[i] = (v[i] + a * col[i]) % P
        out.add(tuple(v))
    return out


def log3_exact(size):
    d = 0
    z = 1
    while z < size:
        z *= 3
        d += 1
    assert z == size
    return d


def branch_dp(H):
    m = len(H)
    N = len(H[0])
    E = set(range(N))
    root = balanced_tree(range(N))
    max_interface = 0

    def visit(node):
        nonlocal max_interface
        indices, left, right = node
        S = set(indices)
        B = span_set(H, indices) & span_set(H, sorted(E - S))
        max_interface = max(max_interface, log3_exact(len(B)))

        if left is None:
            e = indices[0]
            col = tuple(H[i][e] % P for i in range(m))
            states = set()
            for a in (1, 2):
                v = tuple((a * x) % P for x in col)
                if v in B:
                    states.add(v)
            return states

        DL = visit(left)
        DR = visit(right)
        states = set()
        for a in DL:
            for b in DR:
                v = tuple((a[i] + b[i]) % P for i in range(m))
                if v in B:
                    states.add(v)
        return states

    root_states = visit(root)
    zero = tuple([0] * m)
    return zero in root_states, max_interface


def brute_full_support(H):
    m = len(H)
    N = len(H[0])
    for x in product((1, 2), repeat=N):
        if all(sum(H[i][j] * x[j] for j in range(N)) % 3 == 0
               for i in range(m)):
            return True
    return False


def augment(A):
    return [row + [2] for row in A]  # -1 == 2 mod 3


def exactone_brute(A):
    n = len(A[0])
    for x in product((0, 1), repeat=n):
        if all(sum(A[i][j] * x[j] for j in range(n)) == 1
               for i in range(len(A))):
            return True
    return False


def main():
    # SAT control: A=J3. Any one selected column is Exact-One.
    A_sat = [[1, 1, 1] for _ in range(3)]

    # UNSAT control: A=J4-I4. Every row/column has weight three, but no Boolean
    # vector satisfies Ax=1 over the integers.
    A_unsat = [
        [0, 1, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
    ]

    for name, A, expected in (
        ("J3_SAT", A_sat, True),
        ("J4_MINUS_I4_UNSAT", A_unsat, False),
    ):
        H = augment(A)
        dp_answer, width = branch_dp(H)
        brute_flow = brute_full_support(H)
        brute_exact = exactone_brute(A)

        assert dp_answer == brute_flow == brute_exact == expected
        assert width == 1

        print({
            "control": name,
            "exactone": expected,
            "full_support_flow": brute_flow,
            "branch_dp": dp_answer,
            "balanced_tree_interface_width": width,
        })

    # A few deterministic non-source matrices stress only the general merge
    # recurrence.  The DP must agree with exhaustive nonzero-kernel search.
    generic = [
        [[1, 0, 1], [0, 1, 1]],
        [[1, 1, 0, 1], [0, 1, 1, 1]],
        [[1, 0, 2, 1], [0, 1, 1, 2], [1, 1, 0, 0]],
    ]
    for idx, H in enumerate(generic):
        dp_answer, width = branch_dp(H)
        brute = brute_full_support(H)
        assert dp_answer == brute
        print({"generic_control": idx, "answer": dp_answer, "width": width})

    print("Augmented ternary branch-width full-support DP regression: PASS")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
