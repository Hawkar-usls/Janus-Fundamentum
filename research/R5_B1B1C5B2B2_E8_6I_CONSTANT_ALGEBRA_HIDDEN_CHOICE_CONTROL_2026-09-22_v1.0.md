# R5 E8 6I — Constant-Algebra Hidden-Choice Control

Date: 2026-09-22

Authority: `SOURCE_BOUND_DERIVED_CONTROL__NO_D1_PROMOTION__NO_SUCCESSOR_AUTHORIZATION`

## Source-bound parent

Rustem Takhanov, *On the induced problem for fixed-template CSPs*, arXiv:1708.08292v3.

The source defines, for a fixed template `Gamma` and a finite family of algebras `B` on the same domain, an induced template `Gamma^B`.  A variable-to-algebra assignment is admissible exactly when every original constraint relation is a subalgebra of the product of the algebras assigned to its variables.  The source also proves tractability of the input-prototype stage when all algebras in `B` are tractable.

This control isolates the discovery cost.

## Frozen Boolean constant family

Let

```text
B_const
=
{ A_0, A_1 }.
```

Both algebras have the same signature consisting of one unary operation `c`.

For `b in {0,1}` define

```text
c^{A_b}(x) = b
for both x=0,1.
```

Every relation preserved by `A_b` is `b`-valid, so every CSP over a fixed language preserved by `A_b` has the all-`b` assignment.  Thus each `A_b` is a tractable algebra in the relevant source sense.

## Theorem — induced template is exactly the original Boolean template

Let `rho subseteq {0,1}^k` be any Boolean relation.

By Takhanov's induced-template definition, an algebra-label tuple

```text
(A_{b1}, ..., A_{bk})
```

belongs to the induced relation `rho^{B_const}` iff `rho` is preserved by the mixed coordinate-wise operation

```text
(c^{A_{b1}}, ..., c^{A_{bk}}).
```

For every input tuple of `rho`, that mixed operation returns the same fixed tuple

```text
(b1,...,bk).
```

Therefore

```text
(A_{b1},...,A_{bk}) in rho^{B_const}
iff
(b1,...,bk) in rho.
```

Hence the bijection

```text
0 <-> A_0
1 <-> A_1
```

is a relation-by-relation isomorphism

```text
Gamma
cong
Gamma^{B_const}
```

for every Boolean template `Gamma`.

Consequently

```text
CSP(Gamma^{B_const})
=
CSP(Gamma)
up to label renaming.
```

For the full signed 3-clause template this means

```text
PROTOTYPE COVERAGE
=
EXACT / UNIVERSAL

BUT

PROTOTYPE DISCOVERY
=
ORIGINAL 3-SAT
UP TO ISOMORPHISM.
```

## Meaning

This is an exact hidden-choice control.

Adding enough variable-specific algebras to encode the desired Boolean value of every variable makes the induced-algebra certificate universal, but it does not create algorithmic progress: finding the algebra labels is exactly the original semantic-choice problem.

Therefore any 6I successor candidate must establish both:

```text
COVERAGE
+
POLYNOMIAL PROTOTYPE DISCOVERY
```

and may not count a certificate family that merely renames satisfying assignments.

## Relation to 6H anti-loop laws

This control is a direct realization of:

```text
POLY PP DESCRIPTION / AUXILIARIES
!=
POLY SEMANTIC-CHOICE ELIMINATION.
```

It also sharpens the 6I frontier:

```text
TOO RIGID B
=> coverage failure

TOO EXPRESSIVE / VALUE-CODING B
=> hidden SAT in prototype discovery
```

The missing object is a source-bound algebra family between these extremes.

## Claim ceiling

```text
P_VS_NP = OPEN
D1 = EMPTY
SUCCESSOR_ALGORITHM = LOCKED
GENERAL INDUCED-ALGEBRA ROUTE = OPEN
B_const VALUE-CODING SHORTCUT = REJECTED
```
