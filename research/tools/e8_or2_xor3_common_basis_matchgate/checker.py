#!/usr/bin/env python3
"""Symbolic regression for the E8 v4.2 OR2+XOR3 common-basis parity barrier."""

from itertools import product
import sympy as sp

A, B, C, D, t = sp.symbols("A B C D t")
T = sp.Matrix([[A, B], [C, D]])
DELTA = A * D - B * C


def transform(sig, arity):
    out = {}
    for y in product((0, 1), repeat=arity):
        expr = 0
        for x in product((0, 1), repeat=arity):
            val = sig.get(x, 0)
            if not val:
                continue
            term = sp.Integer(val)
            for j in range(arity):
                term *= T[y[j], x[j]]
            expr += term
        out[y] = sp.expand(expr)
    return out


def by_weight(out, arity):
    vals = []
    for w in range(arity + 1):
        reps = [sp.expand(v) for x, v in out.items() if sum(x) == w]
        assert reps
        first = reps[0]
        assert all(sp.expand(v - first) == 0 for v in reps)
        vals.append(sp.factor(first))
    return vals


def main():
    or2 = {x: 1 for x in product((0, 1), repeat=2) if any(x)}
    xor3 = {x: 1 for x in product((0, 1), repeat=3) if sum(x) % 2 == 1}

    ow = by_weight(transform(or2, 2), 2)
    xw = by_weight(transform(xor3, 3), 3)

    expected_o = [B * (2 * A + B), A * D + B * C + B * D, D * (2 * C + D)]
    expected_x = [
        B * (3 * A**2 + B**2),
        A**2 * D + 2 * A * B * C + B**2 * D,
        2 * A * C * D + B * C**2 + B * D**2,
        D * (3 * C**2 + D**2),
    ]
    assert all(sp.expand(u - v) == 0 for u, v in zip(ow, expected_o))
    assert all(sp.expand(u - v) == 0 for u, v in zip(xw, expected_x))

    # Saturate invertibility with t*det(T)-1=0. For each of the four parity
    # combinations, Groebner basis [1] proves the algebraic system has no
    # solution over characteristic zero (hence no invertible common basis).
    parity_cases = []
    for p_or in ("even", "odd"):
        eq_or = [ow[1]] if p_or == "even" else [ow[0], ow[2]]
        for p_xor in ("even", "odd"):
            eq_xor = [xw[1], xw[3]] if p_xor == "even" else [xw[0], xw[2]]
            equations = eq_or + eq_xor + [t * DELTA - 1]
            G = sp.groebner(equations, t, A, B, C, D, order="lex")
            assert any(g.as_expr() == 1 for g in G.polys), (p_or, p_xor, G)
            parity_cases.append((p_or, p_xor))

    assert len(parity_cases) == 4
    print("PASS: transformed OR2/XOR3 Hamming-weight formulas verified symbolically")
    print("PASS: all 4 OR2/XOR3 parity combinations are incompatible with det(T)!=0")
    print("PASS: no characteristic-zero common invertible basis reaches matchgate parity")


if __name__ == "__main__":
    main()
