#!/usr/bin/env python3
"""Finite audit for the port-dependent matchgate parity firewall.

The theorem in the companion note is over C and is proved algebraically.
This checker does NOT replace that proof.  It exhaustively audits the local
equations over GF(5) and GF(7), then verifies the parameter-independent support
obstruction for the ExactOne_3 clause tensor.

Holant convention:
  variable tensor E = |000> + |111>;
  clause tensor   W = |001> + |010> + |100>.

For a separate invertible basis T_e on every wire, define
M_e=T_e^{-1} Z T_e.  Matchgate parity would require E to be an eigenvector of
M_1 tensor M_2 tensor M_3, and W to be an eigenvector of
M_1^T tensor M_2^T tensor M_3^T.

The GHZ stabilizer lemma plus odd arity forces every M_e at every equality
node to be anti-diagonal.  Since every wire has exactly one equality endpoint,
all wire involutions are anti-diagonal.  Their transposes complement all three
bits, mapping the weight-one support of W to disjoint weight-two support.
Contradiction.

This excludes direct invertible port-dependent 2x2 holographic matchgate
bases.  It does not exclude gadget-expanded/nonlocal algorithms.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

from itertools import product


EQUALITY3 = (1, 0, 0, 0, 0, 0, 0, 1)
EXACTONE3 = (0, 1, 1, 0, 1, 0, 0, 0)


def mat_vec(matrix, bit):
    """Column bit of a 2x2 matrix."""
    return (matrix[0][bit], matrix[1][bit])


def tensor_action(matrices, vector, prime):
    out = [0] * 8
    for source, amplitude in enumerate(vector):
        if amplitude % prime == 0:
            continue
        source_bits = tuple((source >> i) & 1 for i in range(3))
        for target_bits in product((0, 1), repeat=3):
            coefficient = amplitude
            for i in range(3):
                coefficient *= matrices[i][target_bits[i]][source_bits[i]]
            target = sum(target_bits[i] << i for i in range(3))
            out[target] = (out[target] + coefficient) % prime
    return tuple(out)


def eigenvalue(vector, image, prime):
    pivot = next((i for i, value in enumerate(vector) if value % prime), None)
    assert pivot is not None
    scale = image[pivot] * pow(vector[pivot], -1, prime) % prime
    if all(image[i] % prime == scale * vector[i] % prime for i in range(8)):
        return scale
    return None


def traceless_involutions(prime):
    """All [[a,b],[c,-a]] with M^2=I over GF(prime)."""
    out = []
    for a, b, c in product(range(prime), repeat=3):
        if (a * a + b * c) % prime != 1:
            continue
        matrix = ((a, b), (c, (-a) % prime))
        out.append(matrix)
    return tuple(out)


def transpose(matrix):
    return ((matrix[0][0], matrix[1][0]), (matrix[0][1], matrix[1][1]))


def is_antidiagonal(matrix, prime):
    return matrix[0][0] % prime == 0 and matrix[1][1] % prime == 0


def finite_field_audit(prime):
    involutions = traceless_involutions(prime)
    equality_stabilizers = 0
    for triple in product(involutions, repeat=3):
        image = tensor_action(triple, EQUALITY3, prime)
        scale = eigenvalue(EQUALITY3, image, prime)
        if scale is None:
            continue
        assert scale != 0
        equality_stabilizers += 1
        assert all(is_antidiagonal(matrix, prime) for matrix in triple)

    anti = tuple(matrix for matrix in involutions if is_antidiagonal(matrix, prime))
    assert anti
    for triple in product(anti, repeat=3):
        clause_image = tensor_action(
            tuple(transpose(matrix) for matrix in triple),
            EXACTONE3,
            prime,
        )
        assert eigenvalue(EXACTONE3, clause_image, prime) is None

    # For an anti-diagonal involution [[0,b],[b^-1,0]], EQUALITY3
    # is an eigenvector iff (b1*b2*b3)^2=1.  Over an odd prime field
    # this gives two possible products and (p-1)^2 triples per product.
    expected_equality_stabilizers = 2 * (prime - 1) ** 2
    assert equality_stabilizers == expected_equality_stabilizers
    return {
        "prime": prime,
        "involutions": len(involutions),
        "equality_stabilizer_triples": equality_stabilizers,
        "anti_triples": len(anti) ** 3,
    }


def support_audit():
    support = {i for i, value in enumerate(EXACTONE3) if value}
    complement = {i ^ 0b111 for i in support}
    assert support == {0b001, 0b010, 0b100}
    assert complement == {0b110, 0b101, 0b011}
    assert support.isdisjoint(complement)
    return support, complement


def main():
    support, complement = support_audit()
    print(f"EXACTONE3 support={sorted(support)} complement={sorted(complement)}")
    for prime in (5, 7):
        result = finite_field_audit(prime)
        print(
            f"GF({prime}): involutions={result['involutions']} "
            f"equality stabilizer triples={result['equality_stabilizer_triples']} "
            "all anti-diagonal; clause parity impossible PASS"
        )
    print("PORT_DEPENDENT_LOCAL_MATCHGATE_PARITY_ROUTE = FAILED")
    print("GADGET_EXPANDED_OR_NONLOCAL_ROUTE = NOT_DECIDED")
    print("UNIVERSAL_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
