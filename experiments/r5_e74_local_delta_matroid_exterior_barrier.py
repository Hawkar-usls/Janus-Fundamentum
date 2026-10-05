#!/usr/bin/env python3
"""R5 E74: local projected-linear / matching-gadget barrier.

The E73 hard atom on the variable side is Equality_3 = {000,111}.  A projected
linear delta-matroid is, in particular, a delta-matroid.  This checker freezes
that the source-aligned E12 boundary relations fail the symmetric-exchange
axiom at three nested local scales:

  1. one Equality_3 star;
  2. the E63 strong-C5 four-port relation P5;
  3. the complete E53 one-gadget six-port quotient, which is
     Equality_3 x Equality_3.

By contrast ExactOne_3 is the basis family of U_{1,3} and is a delta-matroid.
Thus the local obstruction is exactly on the all-or-none variable side.

Twisting/coordinate complementation cannot repair the failure: delta-matroid
status is twist invariant, and the checker also exhausts all twists of the
small frozen relations directly.

Scientific ceiling: this rules out a LOCAL support-preserving compilation of
these interfaces into projected linear delta-matroids / ordinary matching
signatures.  It does not rule out global weighted cancellation coupling several
E12 gadgets.  P_VS_NP remains OPEN.
"""

from r5_e53_e12_boolean_boundary_quotient import local_states
from r5_e63_e12_nonaffine_c5_packing_raw_parameter_firewall import P5


def tuple_mask(bits):
    return sum((int(b) & 1) << i for i, b in enumerate(bits))


def symmetric_exchange_failure(family, n):
    """Return one failed (X,Y,e,attempts), or None if the delta axiom holds."""
    F = set(family)
    assert F
    for X in F:
        for Y in F:
            diff = X ^ Y
            for e in range(n):
                if not ((diff >> e) & 1):
                    continue
                attempts = []
                repaired = False
                for f in range(n):
                    if not ((diff >> f) & 1):
                        continue
                    if e == f:
                        Z = X ^ (1 << e)
                    else:
                        Z = X ^ (1 << e) ^ (1 << f)
                    attempts.append((f, Z))
                    if Z in F:
                        repaired = True
                        break
                if not repaired:
                    return X, Y, e, tuple(attempts)
    return None


def is_delta_matroid(family, n):
    return symmetric_exchange_failure(family, n) is None


def twist(family, mask):
    return {F ^ mask for F in family}


def all_twists_same_delta_status(family, n, expected):
    for T in range(1 << n):
        assert is_delta_matroid(twist(family, T), n) is expected


def bits(mask, n):
    return format(mask, f"0{n}b")[::-1]


def e53_boundary_family():
    # E53 proves the only quotient signatures are all four (a,b) in {0,1}^2,
    # where the three unprimed ports all equal a and the three primed ports all
    # equal b.  Reconstruct it from the checker rather than hard-coding it.
    sigs = {sig for sig, _chosen in local_states()}
    assert sigs == {(0, 0), (1, 0), (0, 1), (1, 1)}
    return {
        tuple_mask((a, a, a, b, b, b))
        for a, b in sigs
    }


def main():
    exact_one_3 = {1 << i for i in range(3)}
    equality_3 = {0, (1 << 3) - 1}
    p5 = {tuple_mask(t) for t in P5}
    e53 = e53_boundary_family()

    # Positive sanity: ExactOne_3 is the U_{1,3} basis family.
    assert is_delta_matroid(exact_one_3, 3)
    all_twists_same_delta_status(exact_one_3, 3, True)

    # Hard atom: {empty, full-3} fails symmetric exchange.
    w_eq = symmetric_exchange_failure(equality_3, 3)
    assert w_eq is not None
    X, Y, e, attempts = w_eq
    assert {X, Y} == {0, 7}
    assert all(Z not in equality_3 for _f, Z in attempts)
    all_twists_same_delta_status(equality_3, 3, False)

    # E63 strong-C5 boundary relation is also non-delta.
    assert len(p5) == 5
    w_p5 = symmetric_exchange_failure(p5, 4)
    assert w_p5 is not None
    all_twists_same_delta_status(p5, 4, False)

    # Complete one-gadget quotient is Eq3 x Eq3 and remains non-delta.
    expected_e53 = {
        tuple_mask((0, 0, 0, 0, 0, 0)),
        tuple_mask((1, 1, 1, 0, 0, 0)),
        tuple_mask((0, 0, 0, 1, 1, 1)),
        tuple_mask((1, 1, 1, 1, 1, 1)),
    }
    assert e53 == expected_e53
    w_e53 = symmetric_exchange_failure(e53, 6)
    assert w_e53 is not None
    all_twists_same_delta_status(e53, 6, False)

    print("R5 E74 local delta-matroid / exterior barrier: PASS")
    print("ExactOne_3: delta-matroid (U_1,3 basis family)")
    print(
        "Equality_3: NON-delta; witness=",
        (bits(w_eq[0], 3), bits(w_eq[1], 3), w_eq[2],
         [(f, bits(z, 3)) for f, z in w_eq[3]]),
    )
    print(
        "E63 P5: NON-delta; witness=",
        (bits(w_p5[0], 4), bits(w_p5[1], 4), w_p5[2],
         [(f, bits(z, 4)) for f, z in w_p5[3]]),
    )
    print(
        "E53 full gadget quotient Eq3xEq3: NON-delta; witness=",
        (bits(w_e53[0], 6), bits(w_e53[1], 6), w_e53[2],
         [(f, bits(z, 6)) for f, z in w_e53[3]]),
    )
    print("all coordinate twists checked: non-delta barriers persist")
    print("consequence: local support-preserving projected-linear/matching compilation is blocked")
    print("live escape: genuinely global weighted cancellation across multiple gadgets")
    print("scientific ceiling: P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
