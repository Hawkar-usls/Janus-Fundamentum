#!/usr/bin/env python3
"""Finite exact regression for the augmented regular-matroid syndrome terminal.

The regular-matroid polynomial-time theorem is source/proof based.  This checker
replays the JANUS reductions exactly on two tiny regular controls:

  mu(A) = minimum F2 syndrome weight
        = minimum binary-matroid circuit weight through e_b,

and Exact-One iff mu(A)=n/3 for cubic square A.
"""
from __future__ import annotations

from itertools import combinations, product


def gf2_rank(cols: list[tuple[int, ...]], nrows: int) -> int:
    basis: dict[int, int] = {}
    for col in cols:
        v = sum((bit & 1) << i for i, bit in enumerate(col))
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
    return len(basis)


def mat_cols(A: list[list[int]]) -> list[tuple[int, ...]]:
    return [tuple(A[i][j] for i in range(len(A))) for j in range(len(A[0]))]


def ax_mod2(A: list[list[int]], x: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(a * z for a, z in zip(row, x)) & 1 for row in A)


def ax_int(A: list[list[int]], x: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(a * z for a, z in zip(row, x)) for row in A)


def parity_solutions(A: list[list[int]]) -> list[tuple[int, ...]]:
    n = len(A[0])
    one = (1,) * len(A)
    return [x for x in product((0, 1), repeat=n) if ax_mod2(A, x) == one]


def exact_one_solutions(A: list[list[int]]) -> list[tuple[int, ...]]:
    n = len(A[0])
    one = (1,) * len(A)
    return [x for x in product((0, 1), repeat=n) if ax_int(A, x) == one]


def circuits_through_b(A: list[list[int]]) -> list[tuple[int, ...]]:
    """Return circuits of [A|1] containing distinguished last column."""
    nrows = len(A)
    cols = mat_cols(A) + [(1,) * nrows]
    eb = len(cols) - 1
    out: list[tuple[int, ...]] = []

    for size in range(2, len(cols) + 1):
        for others in combinations(range(eb), size - 1):
            S = tuple(others) + (eb,)
            chosen = [cols[j] for j in S]
            if gf2_rank(chosen, nrows) == len(chosen):
                continue
            # Minimal dependence: every one-element deletion independent.
            if all(
                gf2_rank([cols[j] for j in S if j != drop], nrows) == len(S) - 1
                for drop in S
            ):
                out.append(S)
    return out


def verify_control(name: str, A: list[list[int]], expected_sat: bool, expected_mu: int) -> None:
    n = len(A)
    assert len(A[0]) == n
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    ps = parity_solutions(A)
    mu = min((sum(x) for x in ps), default=10**9)
    ex = exact_one_solutions(A)
    circs = circuits_through_b(A)
    mu_circuit = min((len(C) - 1 for C in circs), default=10**9)

    assert mu == expected_mu, (name, mu, expected_mu)
    assert mu_circuit == mu, (name, mu_circuit, mu)
    assert bool(ex) == expected_sat
    assert bool(ex) == (3 * mu == n)

    # Replay the incidence-count identity for every parity solution.
    for x in ps:
        row_counts = ax_int(A, x)
        assert all(c in (1, 3) for c in row_counts)
        t = sum(c == 3 for c in row_counts)
        assert 3 * sum(x) == n + 2 * t

    print(
        f"{name}: n={n} parity={len(ps)} exact={len(ex)} "
        f"mu={mu} min_circuit_through_b={mu_circuit} PASS"
    )


def main() -> None:
    # Rank-one regular matroid: all four augmented columns are parallel.
    J3 = [[1, 1, 1] for _ in range(3)]
    verify_control("J3_SAT_REGULAR", J3, True, 1)

    # [J4-I4 | 1] has four independent columns plus their sum, hence U_{4,5},
    # a corank-one regular matroid.  Its unique F2 syndrome solution is 1111.
    K4_comp = [[0 if i == j else 1 for j in range(4)] for i in range(4)]
    verify_control("J4_MINUS_I4_UNSAT_REGULAR", K4_comp, False, 4)

    print("Augmented regular-matroid syndrome finite regression: PASS")
    print("Scientific ceiling: terminal theorem is source/proof based; P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
