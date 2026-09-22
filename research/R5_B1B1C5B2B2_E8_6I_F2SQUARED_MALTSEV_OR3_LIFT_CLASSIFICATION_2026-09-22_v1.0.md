# R5 E8 6I — F2^2 Mal'tsev OR3 Lift Classification

Date: 2026-09-22

Authority: `PROVED_FIXED_CARRIER_CLASSIFICATION__SECOND_POLYNOMIAL_LIFECYCLE_CONTROL__NO_D1_PROMOTION`

## 1. Source-bound algorithm donor

Andrei Bulatov and Víctor Dalmau,
*A Simple Algorithm for Mal'tsev Constraints*,
SIAM Journal on Computing 36(1), 16–27 (2006).

DOI:

https://doi.org/10.1137/050628957

The source proves polynomial-time solvability for finite-domain CSPs whose constraint relations are preserved by a Mal'tsev operation.

The present artifact uses only the fixed affine Mal'tsev algebra:

```text
A4 = F2^2
m(x,y,z)=x XOR y XOR z.
```

Every nonempty subalgebra of:

```text
A4^3
=
F2^6
```

is an affine subspace / coset.

## 2. Exact finite classification

Checker:

`research/tools/r5_e8_6i_f2square_maltsev_or3_lift_checker.py`

Frozen receipt:

`research/R5_B1B1C5B2B2_E8_6I_F2SQUARED_MALTSEV_OR3_LIFT_CLASSIFICATION_2026-09-22_v1.0.json`

The checker enumerates exactly:

```text
linear subspaces of F2^6
=
2825

affine subspaces of F2^6
=
26387.
```

A surjective decoder:

```text
pi:F2^2->{0,1}
```

has a 1-fibre of size:

```text
1, 2, or 3.
```

There are respectively:

```text
4, 6, 4
```

concrete decoders of these three types.

## 3. Symmetry reduction is exact

The affine permutation group:

```text
AGL(2,2)
```

has exactly:

```text
24
```

elements.

Since the carrier has four points, this action is the full symmetric group:

```text
AGL(2,2)
cong
S4.
```

Therefore all Boolean decoders having the same 1-fibre cardinality are equivalent under carrier automorphisms.

Applying independent affine automorphisms to the three coordinates maps affine subspaces of `A4^3` to affine subspaces.

Hence exact OR3 liftability depends only on:

```text
(w1,w2,w3)

where

wj=|pi_j^{-1}(1)|.
```

It is therefore sufficient, and exact, to enumerate the:

```text
3^3=27
```

weight triples.

## 4. Exact positive OR3 theorem

Let:

```text
OR3
=
{0,1}^3 \ {000}.
```

For arbitrary surjective decoders:

```text
pi_1,pi_2,pi_3:F2^2->{0,1},
```

there exists an affine subspace:

```text
S <= A4^3
```

with exact decoder image:

```text
(pi_1 x pi_2 x pi_3)(S)
=
OR3
```

if and only if:

```text
at least two of

|pi_1^{-1}(1)|,
|pi_2^{-1}(1)|,
|pi_3^{-1}(1)|

are equal to 3.
```

The exact good weight patterns are:

```text
133
233
313
323
331
332
333.
```

Among all:

```text
14^3=2744
```

concrete surjective decoder triples, exactly:

```text
544
```

admit an exact positive-OR3 affine lift.

## 5. Signed clause form

For a negated literal, replace the decoder by its Boolean complement.

Thus a decoder of weight:

```text
w
```

has sign-adjusted weight:

```text
4-w
```

under a negated literal.

Define the three coarse decoder states:

```text
P:
weight 3
active only for a positive literal;

N:
weight 1
active only for a negative literal;

Z:
weight 2
active for neither sign.
```

Then a signed 3-clause has an exact affine lift iff:

```text
at least two of its three literals
are active under the variable coarse states.
```

This is again an exact threshold-two rule.

## 6. Prototype discovery is polynomial

Introduce two Boolean indicators per SAT variable:

```text
P_x
N_x
```

with the 2-CNF mutex:

```text
NOT P_x OR NOT N_x.
```

The neutral state `Z` is represented by:

```text
P_x=0
N_x=0.
```

For a positive literal `x`, its activity atom is `P_x`.

For a negative literal `NOT x`, its activity atom is `N_x`.

For each 3-clause with activity atoms:

```text
a,b,c,
```

the threshold-two condition is:

```text
(a OR b)
AND
(a OR c)
AND
(b OR c).
```

Therefore the complete decoder/prototype discovery problem is ordinary 2-SAT.

After finding the coarse state, choose any fixed canonical concrete decoder from its weight class. The symmetry theorem guarantees that the frozen local lift table applies.

Thus:

```text
T_prototype_discovery
=
POLYNOMIAL.
```

## 7. Lifted solve

Each selected lifted relation is an affine subspace of a power of `F2^2` and is preserved by the common Mal'tsev operation.

By the source-bound Mal'tsev CSP algorithm:

```text
T_lifted_solve
=
POLYNOMIAL.
```

Boolean reconstruction is coordinate-wise through the selected decoder.

Hence this carrier gives another complete polynomial lifecycle on its admitted subclass:

```text
2-SAT prototype discovery
+
exact affine local lifts
+
Mal'tsev polynomial solve
+
exact decode
=
POLYNOMIAL.
```

## 8. Coverage remains strict

Use the standard witness:

```text
(x OR y OR z)
AND
(NOT x OR NOT y OR NOT z).
```

The original formula is satisfiable.

An F2^2 coarse prototype would require simultaneously:

```text
at least two variables in state P
```

and:

```text
at least two variables in state N.
```

But every variable can be at most one of:

```text
P,N,Z.
```

So no coarse prototype exists.

Therefore:

```text
F2^2_MALTSEV_LIFT
=
STRICT_SUBCLASS

UNIVERSAL_3SAT_COVERAGE
=
FAIL.
```

## 9. Scientific meaning

A3-SBM and pure F2^2-Mal'tsev are different tractability mechanisms:

```text
A3:
semilattice quotient
+
Mal'tsev residual block

F2^2:
pure affine Mal'tsev carrier.
```

Yet both produce the same exact coarse threshold:

```text
2_OF_3.
```

Therefore the threshold-two phenomenon is not unique to the particular A3 block construction.

This result does **not** prove a general lower bound for all Mal'tsev lifts.

It proves only:

```text
the natural fixed pure affine carrier
F2^2
does not bridge
2_OF_3 -> 1_OF_3.
```

## 10. Next synthesis target

The exact Boolean identity:

```text
OR3(a,b,c)

=

MAJ(a,b,c)
OR
MAJ(a,NOT b,c)
OR
MAJ(a,b,NOT c)
```

shows that ordinary OR3 is the union of three threshold-two sheets.

Therefore the next composition question is no longer:

```text
can one local threshold-two lift equal OR3?
```

but:

```text
can three exact polynomial threshold-two lifts
be composed algebraically
without exposing a clause-wise semantic-choice variable
whose global discovery is again SAT?
```

That is the next exact interface problem.

## Claim ceiling

```text
P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED

F2^2 MALTSEV FIXED CARRIER
=
EXACTLY CLASSIFIED

UNIVERSAL COVERAGE
=
FAIL

GENERAL NONLOCAL / MULTI-SHEET COMPOSITION
=
OPEN
```
