# R5 E8 6I — Arbitrary-Arity Boolean B4 Functional-Graph Classification Theorem

Date: 2026-09-22

Authority: `PROVED_SCOPED_THEOREM__NO_D1_PROMOTION__NO_SUCCESSOR_AUTHORIZATION`

## 1. Statement

Let

```text
B4
=
{AND3, OR3, MAJ3, XOR3}
```

on the Boolean domain `D={0,1}`.

Let

```text
h : D^k -> D
```

be any Boolean function of arbitrary finite arity.

Assume there exist source labels

```text
f_1,...,f_k in B4
```

and an output label

```text
g in B4
```

such that the graph relation

```text
Graph(h)
=
{(x_1,...,x_k,h(x_1,...,x_k))}
```

is preserved by the mixed coordinate operation

```text
(f_1,...,f_k,g).
```

Equivalently, for all three input vectors `a,b,c in D^k`:

```text
h(
 f_1(a_1,b_1,c_1),
 ...,
 f_k(a_k,b_k,c_k)
)
=
g(h(a),h(b),h(c)).
```

Then `h` belongs to one of the following classes.

### Output label AND3

Either `h` is constant, or:

```text
h
=
AND of a nonempty set of signed input literals.
```

For every essential input:

```text
positive literal x_i
=> f_i = AND3

negative literal not x_i
=> f_i = OR3.
```

### Output label OR3

Either `h` is constant, or:

```text
h
=
OR of a nonempty set of signed input literals.
```

For every essential input:

```text
positive literal x_i
=> f_i = OR3

negative literal not x_i
=> f_i = AND3.
```

### Output label XOR3

Either `h` is constant, or:

```text
h(x)
=
c XOR
XOR_{i in S} x_i
```

for a nonempty set `S`.

Every essential source label is:

```text
XOR3.
```

### Output label MAJ3

Either `h` is constant, or `h` is essentially unary:

```text
h=x_i
or
h=not x_i
```

for one input coordinate, and the essential source label is:

```text
MAJ3.
```

Labels on inessential coordinates are unrestricted.

Therefore there is **no arbitrary-arity Boolean functional gate** whose B4-compatible graph creates a new algebra-type router outside:

```text
SIGNED CONJUNCTION
SIGNED DISJUNCTION
AFFINE PARITY
LITERAL / NEGATED LITERAL
CONSTANT.
```

## 2. Unary-section lemma

Suppose coordinate `i` is essential.

Fix every other coordinate to constants so that the resulting unary section of `h` is nonconstant.

Every nonconstant Boolean unary function is:

```text
id
or
not.
```

Because all B4 operations are idempotent, fixing coordinates to constants preserves the mixed-homomorphism identity.

Thus the unary section is a homomorphism from the source algebra `f_i` to the output algebra `g`.

Directly checking the four source/output operations gives:

### identity section

```text
AND -> AND
OR  -> OR
MAJ -> MAJ
XOR -> XOR
```

only.

### negated section

```text
AND -> OR
OR  -> AND
MAJ -> MAJ
XOR -> XOR
```

only.

Hence every essential coordinate is already forced into the output family, up to Boolean duality for AND/OR.

## 3. AND case

Assume `g=AND3`.

By the unary-section lemma, every essential coordinate has source label:

```text
AND3
or
OR3
```

depending on whether its effective literal is positive or negated.

Conjugate every `OR3` essential coordinate by Boolean complement.

After this coordinate change all essential source operations become `AND3`.

The conjugated function `q` satisfies:

```text
q(a AND b AND c)
=
q(a) AND q(b) AND q(c)
```

coordinatewise.

If `q(1,...,1)=0`, then setting two arguments to the all-one vector gives:

```text
q(x)
=
q(x) AND 0 AND 0
=
0
```

for every `x`, so `q` is constant.

Otherwise:

```text
q(1,...,1)=1.
```

Then:

```text
q(x AND y)
=
q(x AND y AND 1)
=
q(x) AND q(y).
```

Thus `q^{-1}(1)` is an upward-closed meet-closed filter of the finite Boolean lattice.

Every filter of a finite Boolean lattice is principal.

Therefore there exists a coordinate set `S` such that:

```text
q(x)=1
iff
x_i=1
for every i in S.
```

Hence:

```text
q
=
AND_{i in S} x_i.
```

Undoing coordinate conjugations yields a conjunction of signed literals.

## 4. OR case

Dualize the AND proof.

Every essential coordinate is OR3 for a positive effective literal or AND3 for a negated effective literal.

After conjugation the function is a join-homomorphism of Boolean lattices and therefore a disjunction of a set of coordinates.

Undoing conjugation yields a disjunction of signed literals.

## 5. XOR case

Assume `g=XOR3`.

The unary-section lemma forces every essential source label to be XOR3.

Therefore:

```text
h(a XOR b XOR c)
=
h(a) XOR h(b) XOR h(c).
```

Let:

```text
c_0=h(0).
```

Set the third vector to zero:

```text
h(a XOR b)
=
h(a) XOR h(b) XOR c_0.
```

Define:

```text
q(x)=h(x) XOR c_0.
```

Then:

```text
q(a XOR b)
=
q(a) XOR q(b).
```

So `q` is a linear map from `GF(2)^k` to `GF(2)`.

Hence:

```text
q(x)
=
XOR_{i in S} x_i
```

for some set `S`.

Therefore:

```text
h(x)
=
c_0 XOR XOR_{i in S} x_i.
```

## 6. MAJ case

Assume `g=MAJ3`.

The unary-section lemma forces every essential source coordinate to use `MAJ3`.

Suppose `h` depends essentially on at least two coordinates.

Any Boolean function with at least two essential coordinates has a restriction obtained by fixing the other coordinates in which two selected coordinates remain essential.

Because MAJ3 is idempotent, this restriction remains a homomorphism:

```text
(D,MAJ3)^2
->
(D,MAJ3).
```

There are only sixteen binary Boolean functions.

Exact exhaustive checking shows that no essentially-binary Boolean function satisfies:

```text
h(
 MAJ(a_1,b_1,c_1),
 MAJ(a_2,b_2,c_2)
)
=
MAJ(h(a),h(b),h(c)).
```

The only nonconstant binary-table homomorphisms are essentially unary coordinate projections or their complements.

Contradiction.

Thus a nonconstant MAJ-output homomorphism depends on exactly one coordinate.

The unary-section lemma then gives:

```text
h=x_i
or
h=not x_i.
```

## 7. Independent finite replay

Exact checker:

`research/tools/r5_e8_6i_b4_ternary_functional_gate_classifier.py`

Frozen receipt:

`research/R5_B1B1C5B2B2_E8_6I_B4_TERNARY_FUNCTIONAL_GATE_CLASSIFICATION_2026-09-22_v1.0.json`

For every one of the 256 ternary Boolean truth tables and all 256 mixed B4 label quadruples, the checker exhaustively validates graph preservation.

Among functions depending essentially on all three inputs, exactly 18 admit any B4-compatible graph:

```text
8 signed conjunction/minterm functions
8 signed disjunction/maxterm functions
XOR3
XNOR3.
```

Each admits exactly one compatible B4 type tuple.

This replay is a finite control for the general proof; the arbitrary-arity theorem is not inferred from the 256-function experiment.

## 8. Consequence for extension-variable preprocessing

Any preprocessing that introduces Boolean auxiliary variables only through exact functional definitions whose graph must carry a B4 prototype cannot obtain an arbitrary Boolean gate by increasing the function arity.

The only possible functional definitions compatible with B4 are:

```text
signed conjunctions
signed disjunctions
affine parities
literals / negated literals
constants.
```

Therefore:

```text
HIGHER-ARITY BOOLEAN FUNCTIONAL GATES
DO NOT PROVIDE A NEW B4 TYPE-ROUTING ESCAPE.
```

This does not prove that every network of such gates is useless.

It proves that any useful network remains entirely inside the same AND/OR-dual and affine functional families and cannot obtain a new local algebra family by a hidden high-arity gate.

A successful weak relaxation must therefore use something outside pure Boolean functional extension graphs, such as:

```text
NONFUNCTIONAL AUXILIARY RELATIONS
A GENUINELY RICHER LIFTED DOMAIN
OR A NONLOCAL EXACT STRUCTURAL TRANSFORMATION.
```

## 9. Claim ceiling

```text
ARBITRARY-ARITY BOOLEAN B4 FUNCTIONAL GRAPH CLASS
=
CLASSIFIED

NEW UNIVERSAL SAT ALGORITHM
=
NO

GENERAL NONFUNCTIONAL / LIFTED RELATIONAL PREPROCESSING
=
OPEN

P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED
```
