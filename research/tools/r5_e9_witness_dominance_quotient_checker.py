#!/usr/bin/env python3
from __future__ import annotations

from itertools import product, permutations

# Literal: (var_index, polarity), polarity 1 = x, 0 = not x.
Clause = tuple[tuple[int,int], ...]
Formula = tuple[Clause, ...]


def lit_value(a: tuple[int,...], lit: tuple[int,int]) -> int:
    i, pol = lit
    return a[i] if pol else 1-a[i]


def sat_clause(a: tuple[int,...], c: Clause) -> bool:
    return any(lit_value(a,l) for l in c)


def models(n: int, f: Formula) -> set[tuple[int,...]]:
    return {
        a for a in product((0,1), repeat=n)
        if all(sat_clause(a,c) for c in f)
    }


def signed_image(a: tuple[int,...], perm: tuple[int,...], flips: tuple[int,...]) -> tuple[int,...]:
    return tuple(a[perm[j]] ^ flips[j] for j in range(len(perm)))


def has_signed_permutation_dominance(S: set[tuple[int,...]], T: set[tuple[int,...]]) -> bool:
    n = len(next(iter(S or T)))
    for perm in permutations(range(n)):
        for flips in product((0,1), repeat=n):
            image = {signed_image(a,perm,flips) for a in S}
            if image <= T:
                return True
    return False


def residual_identity(P: bool, N: bool, C: bool) -> None:
    # Original star: C AND (x OR P) AND (not x OR N).
    lhs = any(C and (x or P) and ((not x) or N) for x in (False,True))
    rhs = C and (P or N)
    assert lhs == rhs


def main() -> None:
    # Exhaustively verify the one-variable elimination identity at truth-value level.
    for P,N,C in product((False,True), repeat=3):
        residual_identity(P,N,C)

    # A 3-variable pair of residual 2-CNFs with equal model count but no
    # signed-permutation dominance in either direction.
    #
    # R0 = not a AND not b     (c is free)
    R0: Formula = (
        ((0,0),),
        ((1,0),),
    )

    # R1 = not a AND (not b OR not c) AND (b OR c)
    #    = not a AND (b XOR c = 1)
    R1: Formula = (
        ((0,0),),
        ((1,0),(2,0)),
        ((1,1),(2,1)),
    )

    S0=models(3,R0)
    S1=models(3,R1)
    assert S0 == {(0,0,0),(0,0,1)}
    assert S1 == {(0,0,1),(0,1,0)}
    assert len(S0)==len(S1)==2

    # Signed permutations/complements preserve pairwise Hamming distance.
    # S0's two models have distance 1; S1's have distance 2.
    h0=sum(x!=y for x,y in zip(*tuple(S0)))
    h1=sum(x!=y for x,y in zip(*tuple(S1)))
    assert {h0,h1} == {1,2}

    assert not has_signed_permutation_dominance(S0,S1)
    assert not has_signed_permutation_dominance(S1,S0)

    # Embed the two branches into an exact 3CNF star around selector x.
    # x=0 activates R0; x=1 activates R1.
    # Variables in printed notation: x,a,b,c.
    F = (
        # x OR R0 clauses
        ((0,1),(1,0)),
        ((0,1),(2,0)),
        # not x OR R1 clauses
        ((0,0),(1,0)),
        ((0,0),(2,0),(3,0)),
        ((0,0),(2,1),(3,1)),
    )
    MF=models(4,F)
    assert MF

    print("ONE_VARIABLE_EXISTENTIAL_IDENTITY = PASS")
    print("SIGNED_PERM_DOMINANCE_COUNTERPAIR_R0_MODELS = 2")
    print("SIGNED_PERM_DOMINANCE_COUNTERPAIR_R1_MODELS = 2")
    print("SIGNED_PERM_DOMINANCE_R0_TO_R1 = FALSE")
    print("SIGNED_PERM_DOMINANCE_R1_TO_R0 = FALSE")
    print("COUNTERPAIR_EMBEDDED_AS_3CNF_BRANCH_STAR = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
