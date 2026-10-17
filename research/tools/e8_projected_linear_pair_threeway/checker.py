from itertools import combinations, product


def rank_mod2(A):
    A = [row[:] for row in A]
    if not A:
        return 0
    nrow = len(A)
    ncol = len(A[0])
    r = 0
    for c in range(ncol):
        p = next((i for i in range(r, nrow) if A[i][c] & 1), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(nrow):
            if i != r and (A[i][c] & 1):
                A[i] = [x ^ y for x, y in zip(A[i], A[r])]
        r += 1
        if r == nrow:
            break
    return r


def nonsingular_principal_sets(labels, pairs):
    idx = {x: i for i, x in enumerate(labels)}
    M = [[0] * len(labels) for _ in labels]
    for x, y in pairs:
        i, j = idx[x], idx[y]
        M[i][j] = M[j][i] = 1
    out = set()
    for mask in range(1 << len(labels)):
        S = tuple(labels[i] for i in range(len(labels)) if (mask >> i) & 1)
        I = [idx[x] for x in S]
        sub = [[M[i][j] for j in I] for i in I]
        if rank_mod2(sub) == len(I):
            out.add(frozenset(S))
    return out


def project_hidden(feasible, hidden):
    visible = set()
    for F in feasible:
        visible.add(frozenset(x for x in F if x != hidden))
    return visible


def symmetric_exchange_holds(fam):
    fam = set(fam)
    for X in fam:
        for Y in fam:
            diff = X ^ Y
            for u in diff:
                ok = False
                for v in diff:
                    toggle = {u} if v == u else {u, v}
                    if frozenset(set(X) ^ toggle) in fam:
                        ok = True
                        break
                if not ok:
                    return False, (X, Y, u)
    return True, None


def main():
    labels = ["a", "b", "c", "h"]
    LA = nonsingular_principal_sets(labels, [("a", "c"), ("b", "h")])
    LB = nonsingular_principal_sets(labels, [("a", "h"), ("b", "c")])
    A = project_hidden(LA, "h")
    B = project_hidden(LB, "h")

    expected_A = {frozenset(), frozenset(["b"]), frozenset(["a", "c"]), frozenset(["a", "b", "c"])}
    expected_B = {frozenset(), frozenset(["a"]), frozenset(["b", "c"]), frozenset(["a", "b", "c"])}
    all_or_none = {frozenset(), frozenset(["a", "b", "c"])}

    assert A == expected_A, (A, expected_A)
    assert B == expected_B, (B, expected_B)
    assert A & B == all_or_none

    # Independent semantic check: A iff a=c; B iff b=c.
    for bits in product((0, 1), repeat=3):
        S = frozenset(labels[i] for i, b in enumerate(bits) if b)
        assert (S in A) == (bits[0] == bits[2])
        assert (S in B) == (bits[1] == bits[2])
        assert (S in (A & B)) == (bits[0] == bits[1] == bits[2])

    # Tiny global absorption counterexample.
    # A-side variable equality: edge0=edge2; edge1,edge3 free.
    # Clause constraints: {2,3} nonempty and {0,1} nonempty.
    fam = set()
    for bits in product((0, 1), repeat=4):
        if bits[0] != bits[2]:
            continue
        if not (bits[2] or bits[3]):
            continue
        if not (bits[0] or bits[1]):
            continue
        fam.add(frozenset(i for i, b in enumerate(bits) if b))

    expected_fam = {
        frozenset([1, 3]),
        frozenset([0, 2]),
        frozenset([0, 2, 3]),
        frozenset([0, 1, 2]),
        frozenset([0, 1, 2, 3]),
    }
    assert fam == expected_fam

    ok, witness = symmetric_exchange_holds(fam)
    assert not ok
    X, Y, u = witness

    # Freeze the intended explicit witness as well.
    X0, Y0, u0 = frozenset([1, 3]), frozenset([0, 2]), 1
    diff = X0 ^ Y0
    assert all(
        frozenset(set(X0) ^ ({u0} if v == u0 else {u0, v})) not in fam
        for v in diff
    )

    print("PASS: A and B are explicit GF(2) projected-linear relations")
    print("PASS: A intersection B is exactly ALL_OR_NONE3")
    print("PASS: A plus two nonempty clause constraints violates symmetric exchange")
    print(f"found_exchange_failure=X{sorted(X)} Y{sorted(Y)} u={u}")


if __name__ == "__main__":
    main()
