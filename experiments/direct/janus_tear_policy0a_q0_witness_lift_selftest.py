#!/usr/bin/env python3
"""Small exact self-test for Q0 canonical equivalence and witness lifting."""

from __future__ import annotations

from janus_tear_policy0a_masked_tseitin import canonical_cnf
from janus_tear_policy0a_q0_typed_anchor_gauge_probe import (
    apply_permutation,
    q0_canonicalize,
)


def satisfies(cnf, assignment: dict[int, bool]) -> bool:
    return all(
        any(
            assignment[abs(literal)] if literal > 0 else not assignment[abs(literal)]
            for literal in clause
        )
        for clause in cnf
    )


def main() -> None:
    f = canonical_cnf(
        [
            (1, 2, 3),
            (1, 2),
            (-1, 3),
            (-2,),
            (3,),
        ]
    )
    rename = {1: 7, 2: 4, 3: 9}
    g = apply_permutation(f, rename)

    qf = q0_canonicalize(f)
    qg = q0_canonicalize(g)
    assert qf.discrete
    assert qg.discrete
    assert qf.key == qg.key

    g_to_f = {
        g_old: {canon: f_old for f_old, canon in qf.old_to_canonical.items()}[canon]
        for g_old, canon in qg.old_to_canonical.items()
    }
    assert apply_permutation(g, g_to_f) == f

    witness_f = {1: False, 2: False, 3: True}
    assert satisfies(f, witness_f)

    canonical_witness = {
        canonical: witness_f[old]
        for old, canonical in qf.old_to_canonical.items()
    }
    witness_g = {
        old: canonical_witness[canonical]
        for old, canonical in qg.old_to_canonical.items()
    }
    assert satisfies(g, witness_g)

    print("Q0_EXACT_CANONICAL_EQUIVALENCE = PASS")
    print("Q0_EXPLICIT_PERMUTATION_REPLAY = PASS")
    print("Q0_SAT_WITNESS_LIFT_SKELETON = PASS")
    print("claim_boundary = witness-map self-test only; unrestricted solver witness recovery not yet wired")


if __name__ == "__main__":
    main()
