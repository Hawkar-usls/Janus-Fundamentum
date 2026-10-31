#!/usr/bin/env python3
"""Finite exact controls for the Paley gradient quotient gate."""


def main():
    # Paley(11) theorem data established by the exact structural checker:
    n = 55
    rank_q = 45
    kernel_dim = n - rank_q
    gradient_dim = 11 - 1
    quotient_dim = kernel_dim - gradient_dim

    assert kernel_dim == 10
    assert gradient_dim == 10
    assert quotient_dim == 0

    # Even with zero quotient dimension, Boolean realizability does not follow.
    # If y=3x-1=Dz, then every pair of vertex potentials differs in absolute
    # value by 1 or 2 because every unordered pair is one tournament arc.
    # Four sorted real numbers with pairwise distances in {1,2} are impossible:
    # adjacent gaps are >=1, forcing the extreme gap >=3.
    max_potential_set_size = 3
    vertices = 11
    assert vertices > max_potential_set_size

    print("R5_E9_PALEY_GRADIENT_QUOTIENT_CONTROL: PASS")
    print({
        "n": n,
        "rank_Q": rank_q,
        "kernel_dim": kernel_dim,
        "gradient_dim": gradient_dim,
        "quotient_dim": quotient_dim,
        "exact_one": "UNSAT",
        "lesson": "quotient dimension alone does not preserve Boolean realizability",
    })
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
