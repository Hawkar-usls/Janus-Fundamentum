# C041 — Affine-Coordinate 3-SAT Identity

**Status:** `DECISIVE OBSTRUCTION / P_VS_NP=OPEN`

## Statement

Take an arbitrary source 3-CNF `F(lambda_1,...,lambda_n)`. Apply the C023 `{NAND3,NEQ}` embedding:

```text
x_i XOR c_i = 1
source clause (l1 OR l2 OR l3)
-> Horn NAND3 clause over its three falsity indicators
```

Use the canonical affine parameterization

```text
x_i = lambda_i
c_i = 1 XOR lambda_i.
```

Then exact substitution of these affine coordinates into every Horn NAND3 clause returns the original source clause **syntactically**, with the same literal polarities and supports. Hence the full coordinate formula is exactly `F`.

## Proof

For a positive source literal `x_i`, its falsity indicator is `c_i`; the Horn clause contains `not c_i`. Under `c_i=1 XOR lambda_i`, this is true exactly when `lambda_i=1`, so it translates back to the positive literal `lambda_i`.

For a negative source literal `not x_i`, its falsity indicator is `x_i`; the Horn clause contains `not x_i`. Under `x_i=lambda_i`, this translates back to `not lambda_i`.

The translation is literal-by-literal and clause-by-clause. Therefore it preserves clause count, clause width, literal polarity, variable supports, primal adjacency and satisfiability.

## Consequence for C041

Affine-coordinate substitution by itself is not a simplifying mechanism. On the hard C023 image it merely changes notation and reconstructs arbitrary 3-SAT over the free coordinates.

A valid C041 advance must therefore discover and certify an additional tractable property of the coordinate predicates—such as bounded coordinate interaction width, nested supports, an acyclic factor product, a decomposable symbolic cover, or another replayable structure. When no such certificate is found within a fixed polynomial budget, the correct result is `OPEN`.

## Frozen audit

```bash
python experiments/direct/janus_c041_affine_coordinate_3sat_identity.py
```

The deterministic audit checks 600 random 3-CNFs on up to nine variables, 80,992 assignments, exact syntactic round trips, semantic equivalence, and primal-edge preservation. A 24-variable pressure fixture confirms linear size preservation.

Finite tests validate the implementation. The universal identity follows from the literal-by-literal proof above.

## Claim boundary

This result blocks only the naive route

```text
affine parameterization -> substitute -> assume simpler coordinate formula.
```

It does not rule out richer semantic compression, structured compilation, portfolio-guided coordinate decompositions, or a future polynomial SAT algorithm. It does not prove `P!=NP`.

```text
P_VS_NP=OPEN
```
