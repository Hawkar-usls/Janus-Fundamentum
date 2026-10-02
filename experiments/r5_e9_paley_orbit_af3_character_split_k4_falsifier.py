#!/usr/bin/env python3
"""Exact regression for the Paley-orbit AF3 consistency split and q=331 K4 falsifier."""

from itertools import combinations


def orbit_minus2(q):
    r = (-2) % q
    O = []
    seen = set()
    x = 1
    while x not in seen:
        seen.add(x)
        O.append(x)
        x = (x * r) % q
    assert x == 1
    return O


def character_particular(q, O):
    assert len(O) % 3 == 0
    r0 = {s: k % 3 for k, s in enumerate(O)}
    r = (-2) % q
    for s in O:
        assert (2 * r0[s] + r0[(r * s) % q]) % 3 == 1
    return r0


def k4s_containing_zero(q, O):
    S = set(O) | {(-s) % q for s in O}
    nbr = sorted(S)
    checked = 0
    found = []
    for a, b, c in combinations(nbr, 3):
        checked += 1
        if ((b - a) % q in S and
            (c - a) % q in S and
            (c - b) % q in S):
            found.append((0, a, b, c))
    return len(S), checked, found


def main():
    # Frozen first-family controls from the existing Paley-orbit theorem plus
    # additional AF3-consistent members used to stress the character branch.
    controls = {
        11: 5,
        19: 9,
        43: 7,
        59: 29,
        67: 33,
        139: 69,
        163: 81,
        211: 105,
        307: 51,
        331: 15,
    }

    consistent = []
    inconsistent = []
    for q, expected_L in controls.items():
        assert q % 8 == 3
        O = orbit_minus2(q)
        L = len(O)
        assert L == expected_L

        # Necessity from the all-ones left-kernel obstruction:
        # if A z = 1 then q*L must vanish mod 3.
        if L % 3:
            assert (q * L) % 3 != 0
            inconsistent.append((q, L))
        else:
            assert (q * L) % 3 == 0
            character_particular(q, O)
            consistent.append((q, L))

    assert (19, 9) in consistent
    assert (331, 15) in consistent
    assert (11, 5) in inconsistent
    assert (43, 7) in inconsistent

    # Positive control: Paley19 uses the full QR orbit and has many support K4s.
    O19 = orbit_minus2(19)
    S19, checked19, K19 = k4s_containing_zero(19, O19)
    assert len(O19) == 9 and S19 == 18
    assert checked19 == 816
    assert len(K19) > 0

    # Falsifier: q=331 is AF3-consistent (L=15) but its support Cayley graph
    # has no K4. Translation invariance makes this 4060-triple test complete.
    O331 = orbit_minus2(331)
    assert len(O331) == 15 and len(O331) % 3 == 0
    character_particular(331, O331)
    S331, checked331, K331 = k4s_containing_zero(331, O331)
    assert S331 == 30
    assert checked331 == 4060
    assert len(K331) == 0

    print("PASS_PALEY_ORBIT_AF3_CHARACTER_SPLIT_AND_K4_FALSIFIER")
    print("consistent_controls=", consistent)
    print("inconsistent_controls=", inconsistent)
    print("q19_support_size=18 k4_containing_zero=", len(K19))
    print("q331_L=15 support_size=30 k4_triples_checked=4060 k4_containing_zero=0")
    print("UNIVERSAL_GAIN_K4_MOTIF=FALSE")
    print("NEXT=CHARACTER_COMPATIBLE_4CRITICAL_GAIN_OBSTRUCTIONS")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
