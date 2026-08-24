#!/usr/bin/env python3
"""Provider replay for C025-E2R naive class-count barrier.

This is a falsifier for naive semantic/flat-case extension-count invariants.
It does not prove a lower bound for unrestricted ER3.
"""
from itertools import product
from math import ceil, log2


def signature_ceiling(n: int, k: int) -> int:
    return min(1 << n, 1 << k)


def class_count_lower_bound(m: int) -> int:
    return ceil(log2(m)) if m > 1 else 0


def parity(values):
    out = False
    for value in values:
        out ^= value
    return out


def xor_via_three_and_gates(y: bool, x: bool) -> bool:
    t1 = y and x
    t2 = (not y) and (not x)
    return (not t1) and (not t2)


def parity_via_b2(values):
    y = values[0]
    gates = 0
    for x in values[1:]:
        y = xor_via_three_and_gates(y, x)
        gates += 3
    return y, gates


def clause_is_implicate_of_parity_one(n: int, clause: tuple[int, ...]) -> bool:
    if any(-lit in clause for lit in clause):
        return True
    for bits in product([False, True], repeat=n):
        if not parity(bits):
            continue
        if not any((bits[abs(lit)-1] if lit > 0 else not bits[abs(lit)-1]) for lit in clause):
            return False
    return True


def verify_no_short_implicates(n: int) -> None:
    for signs in product([-1, 0, 1], repeat=n):
        clause = tuple(sign * (i + 1) for i, sign in enumerate(signs) if sign)
        if not clause or len(clause) >= n:
            continue
        assert not clause_is_implicate_of_parity_one(n, clause), (n, clause)


def main() -> None:
    for n in range(1, 13):
        assert class_count_lower_bound(1 << n) == n
        for k in range(n + 4):
            assert signature_ceiling(n, k) <= (1 << n)
            assert signature_ceiling(n, k) <= (1 << k)

    for n in range(1, 10):
        for bits in product([False, True], repeat=n):
            got, gates = parity_via_b2(bits)
            assert got == parity(bits)
            assert gates == 3 * (n - 1)

    for n in range(2, 7):
        verify_no_short_implicates(n)

    n = 12
    print("C025_E2R_SEMANTIC_SIGNATURE_CEILING = PASS")
    print("C025_E2R_CLASS_COUNT_SUPERPOLY_METHOD = REFUTED")
    print("C025_E2R_PARITY_B2_COMPRESSION = PASS")
    print("C025_E2R_FLAT_CASE_COUNT_INVARIANT = REFUTED")
    print(f"fixture_n = {n}")
    print(f"fixture_extension_gates = {3*(n-1)}")
    print(f"fixture_flat_cnf_or_dnf_cases = {1 << (n-1)}")
    print("claim_boundary = naive invariant falsification only; unrestricted ER3 K(F) remains open")


if __name__ == "__main__":
    main()
