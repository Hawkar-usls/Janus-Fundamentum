#!/usr/bin/env python3
"""R5 E59 exact controls: every binary kernel word has a canonical 4-block form.

Let A=I+P+Q over F_2 and k in ker(A).  With K=supp(k), write PK=supp(Pk),
QK=supp(Qk).  At every coordinate the membership triple in (K,PK,QK) has
even parity, hence is one of

    000, 110, 101, 011.

Define disjoint blocks

    D = 000,
    A = 110 = K ∩ PK,
    B = 101 = K ∩ QK,
    C = 011 = PK ∩ QK.

Then

    V  = A ⊔ B ⊔ C ⊔ D,
    K  = A ⊔ B,
    PK = A ⊔ C,
    QK = B ⊔ C.

Because P,Q preserve cardinality, |A|=|B|=|C|=:m. Therefore

    |K| = 2m,
    |D| = n-3m = n - 3|K|/2.

Thus the E58 weight cap |K|<=2n/3 is exactly D>=0, and Exact-One is exactly
D=empty. At D=empty, x=1+k has support C and

    P(C)=B, Q(C)=A,

so V=C ⊔ P(C) ⊔ Q(C).
"""
import itertools


def build_A(p, q):
    n = len(p)
    assert len(q) == n
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        cols = (i, p[i], q[i])
        assert len(set(cols)) == 3
        for j in cols:
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def matvec_mod2(A, x):
    return [sum(a*b for a,b in zip(row,x)) & 1 for row in A]


def support(bits):
    return {i for i,b in enumerate(bits) if b}


def perm_action_on_vector(p, x):
    """Permutation-matrix action: output at p[i] receives x[i]."""
    y = [0] * len(x)
    for i,j in enumerate(p):
        y[j] = x[i]
    return y


def perm_action_on_set(p, S):
    return {p[i] for i in S}


def classify_blocks(p, q, k):
    n = len(k)
    K = support(k)
    PK = perm_action_on_set(p, K)
    QK = perm_action_on_set(q, K)

    A = K & PK
    B = K & QK
    C = PK & QK
    D = set(range(n)) - (K | PK | QK)

    # Kernel parity forbids 111 and all odd one-hot patterns.
    assert not (K & PK & QK)
    for v in range(n):
        triple = (v in K, v in PK, v in QK)
        assert (sum(triple) % 2) == 0
        assert triple in {
            (False, False, False),
            (True, True, False),
            (True, False, True),
            (False, True, True),
        }

    assert A.isdisjoint(B)
    assert A.isdisjoint(C)
    assert A.isdisjoint(D)
    assert B.isdisjoint(C)
    assert B.isdisjoint(D)
    assert C.isdisjoint(D)
    assert A | B | C | D == set(range(n))

    assert K == A | B
    assert PK == A | C
    assert QK == B | C

    assert len(A) == len(B) == len(C)
    assert len(K) == 2 * len(A)
    assert len(D) == n - 3 * len(A)
    assert 2 * len(D) == 2*n - 3*len(K)

    return A,B,C,D


def check_fixture(name, p, q, expect_exact, expect_kmax, expect_min_D):
    A = build_A(p, q)
    n = len(A)
    kernel = []

    for k_tuple in itertools.product((0,1), repeat=n):
        k = list(k_tuple)
        if matvec_mod2(A, k) != [0] * n:
            continue

        blocks = classify_blocks(p, q, k)
        Ablk,Bblk,Cblk,Dblk = blocks
        w = sum(k)
        kernel.append((w, len(Dblk), k_tuple, blocks))

        # Complement is the E56 parity-coset point.
        x = [1-b for b in k]
        y = [sum(a*b for a,b in zip(row,x)) for row in A]
        assert all(v in (1,3) for v in y)
        assert sum(v == 3 for v in y) == len(Dblk)

        if not Dblk:
            # At the cap, complement support is exactly C, and the other
            # two exact-cover images are B and A.
            S = support(x)
            assert S == Cblk
            assert perm_action_on_set(p, S) == Bblk
            assert perm_action_on_set(q, S) == Ablk
            assert S.isdisjoint(perm_action_on_set(p,S))
            assert S.isdisjoint(perm_action_on_set(q,S))
            assert perm_action_on_set(p,S).isdisjoint(perm_action_on_set(q,S))
            assert S | perm_action_on_set(p,S) | perm_action_on_set(q,S) == set(range(n))
            assert y == [1] * n

    kmax = max(w for w,_,_,_ in kernel)
    min_D = min(d for _,d,_,_ in kernel)
    has_exact = any(d == 0 for _,d,_,_ in kernel)

    assert kmax == expect_kmax
    assert min_D == expect_min_D
    assert has_exact == expect_exact
    assert 2 * min_D == 2*n - 3*kmax

    print(f"{name}: n={n} kernel={len(kernel)} kmax={kmax} min_D={min_D} exact={has_exact}")


def main():
    check_fixture(
        "SAT9",
        [2,6,7,4,5,8,1,3,0],
        [5,8,1,6,3,2,0,4,7],
        True,
        6,
        0,
    )
    check_fixture(
        "UNSAT9",
        [4,0,6,7,8,1,5,2,3],
        [8,7,1,6,3,0,4,5,2],
        False,
        4,
        3,
    )
    print("R5 E59 kernel four-block normal form: PASS")


if __name__ == "__main__":
    main()
