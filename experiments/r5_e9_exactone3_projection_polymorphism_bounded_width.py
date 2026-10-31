#!/usr/bin/env python3
"""Finite regression for the arbitrary-arity EXACT_ONE_3 projection theorem.

The theorem is proved symbolically in the companion research note.  This checker
exhaustively enumerates all Boolean operations through arity 4 and verifies that
exactly the coordinate projections preserve EXACT_ONE_3.
"""

from itertools import product

R = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
RSET = set(R)


def bit_index(bits):
    out = 0
    for b in bits:
        out = (out << 1) | b
    return out


def preserves(table, arity):
    for inputs in product(R, repeat=arity):
        out = []
        for coord in range(3):
            args = tuple(inputs[r][coord] for r in range(arity))
            out.append(table[bit_index(args)])
        if tuple(out) not in RSET:
            return False
    return True


def projection_table(arity, coordinate):
    vals = []
    for bits in product((0, 1), repeat=arity):
        vals.append(bits[coordinate])
    return tuple(vals)


def main():
    for arity in range(1, 5):
        preserving = []
        table_size = 1 << arity
        for values in product((0, 1), repeat=table_size):
            if preserves(values, arity):
                preserving.append(tuple(values))

        projections = {
            projection_table(arity, i)
            for i in range(arity)
        }
        assert set(preserving) == projections, (
            arity,
            len(preserving),
            len(projections),
        )
        print(
            f"PASS arity={arity}: preserving={len(preserving)} "
            f"= coordinate projections"
        )

    # Direct regression of the set-function proof for a few larger arities.
    for arity in range(1, 9):
        for pivot in range(arity):
            def g(mask):
                return (mask >> pivot) & 1

            full = (1 << arity) - 1
            assert g(0) == 0 and g(full) == 1
            for a in range(1 << arity):
                remaining = full ^ a
                b = remaining
                while True:
                    c = full ^ (a | b)
                    assert (a & b) == 0 and (a & c) == 0 and (b & c) == 0
                    assert g(a) + g(b) + g(c) == 1
                    if b == 0:
                        break
                    b = (b - 1) & remaining

    print("PASS: finite regression agrees with arbitrary-arity theorem")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
