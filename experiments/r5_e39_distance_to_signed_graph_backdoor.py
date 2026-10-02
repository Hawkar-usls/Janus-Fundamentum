#!/usr/bin/env python3
"""Finite exact controls for R5 E39.

Checks, by exhaustive enumeration, the branch identity behind the
Distance-to-Signed-Graphic theorem.

We build an integer representation R with three signed-graphic columns and one
three-support exceptional column.  R1 is divisible by three.  For each Boolean
assignment of the exceptional coordinate, we compare:

  R_G x_G = b - R_E a

against the ordinary-degree equations produced by the R5 E37 signed-edge gadgets.

This is a finite control of the reduction, not a hardness proof.
P_VS_NP remains OPEN.
"""

from itertools import product


# Rows / signed-graph vertices are 0,1,2.
# Good columns:
#   g0 = (+,+) on 0,1
#   g1 = (+,-) on 1,2
#   g2 = (-,-) on 0,2
GOOD = [
    [1, 1, 0],
    [0, 1, -1],
    [-1, 0, -1],
]

# Exceptional column: support three, arbitrary integer coefficients.
EXC = [3, 1, -1]


def matvec_cols(cols, x):
    m = len(cols[0]) if cols else 3
    out = [0] * m
    for j, bit in enumerate(x):
        if bit:
            for i in range(m):
                out[i] += cols[j][i]
    return out


def colsum(cols):
    m = len(cols[0]) if cols else 3
    return [sum(c[i] for c in cols) for i in range(m)]


def signed_types(cols):
    out = []
    for c in cols:
        nz = [(i, v) for i, v in enumerate(c) if v]
        assert len(nz) == 2
        assert all(v in (-1, 1) for _, v in nz)
        out.append(nz)
    return out


def transformed_degrees(x_good):
    """Return ordinary endpoint degrees induced by the E37 state map.

    Selector-vertex degree-one constraints for mixed edges are automatic in this
    state-map view: for a mixed edge, exactly one of its two selector edges is
    selected.  We also return selector degrees to verify they are all one.
    """
    types = signed_types(GOOD)
    deg = [0, 0, 0]
    selector_degrees = []

    for bit, nz in zip(x_good, types):
        (u, su), (v, sv) = nz
        if (su, sv) == (1, 1):
            if bit:
                deg[u] += 1
                deg[v] += 1
        elif (su, sv) == (-1, -1):
            z = 1 - bit
            if z:
                deg[u] += 1
                deg[v] += 1
        else:
            # Mixed signs: selector chooses positive endpoint iff x=1,
            # negative endpoint iff x=0.
            pos = u if su == 1 else v
            neg = v if sv == -1 else u
            if bit:
                deg[pos] += 1
            else:
                deg[neg] += 1
            selector_degrees.append(1)

    return deg, selector_degrees


def main():
    R = GOOD + [EXC]
    r1 = colsum(R)
    assert all(v % 3 == 0 for v in r1), r1
    b = [v // 3 for v in r1]

    dminus = [0, 0, 0]
    for nz in signed_types(GOOD):
        for i, s in nz:
            if s == -1:
                dminus[i] += 1

    total_residual_solutions = 0

    for a in (0, 1):
        h = [b[i] - EXC[i] * a for i in range(3)]
        f = [h[i] + dminus[i] for i in range(3)]

        residual = []
        factor_states = []

        for xg in product((0, 1), repeat=len(GOOD)):
            lhs = matvec_cols(GOOD, xg)
            residual_ok = lhs == h

            deg, selector_degrees = transformed_degrees(xg)
            factor_ok = deg == f and all(d == 1 for d in selector_degrees)

            # Core E39/E37 identity.
            assert residual_ok == factor_ok, (a, xg, lhs, h, deg, f)

            # Stronger per-state degree identity:
            # deg(v) = (R_G x)_v + d^-(v).
            assert deg == [lhs[i] + dminus[i] for i in range(3)]

            if residual_ok:
                residual.append(xg)
            if factor_ok:
                factor_states.append(xg)

        assert residual == factor_states
        total_residual_solutions += len(residual)
        print(
            f"branch exceptional={a}: h={h}, f={f}, "
            f"residual_solutions={len(residual)}"
        )

    # Direct centered enumeration over all four original Boolean variables.
    direct = []
    for x in product((0, 1), repeat=4):
        y = [3 * bit - 1 for bit in x]
        val = [sum(R[j][i] * y[j] for j in range(4)) for i in range(3)]
        if val == [0, 0, 0]:
            direct.append(x)

    assert len(direct) == total_residual_solutions

    print("R5 E39 distance-to-signed-graph finite control: PASS")
    print(f"R1={r1}, b={b}, dminus={dminus}, direct_witnesses={len(direct)}")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
