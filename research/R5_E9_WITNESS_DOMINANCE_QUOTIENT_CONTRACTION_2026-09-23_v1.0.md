# R5 E9 — Witness-Dominance Quotient Contraction

Date: 2026-09-23

Authority:
`JANUS_DERIVED_EXACT_PARTIAL_CONTRACTION_META_THEOREM__STRICT_POTENTIAL_DROP__NO_UNIVERSAL_EXISTENCE_CLAIM__NO_D1_PROMOTION`

Checker:

`research/tools/r5_e9_witness_dominance_quotient_checker.py`

Parent:

`R5_E9_NONLOCAL_RANK1_JOINT_CONTRACTION_PIVOT_GATE_V1`

## 1. Motivation

Exact quotienting does not need to preserve all models, model counts, or even both
Shannon branches.

For SAT decision/search it is sufficient to preserve:

```text
existence of a witness
+
polynomial reconstruction.
```

This note formalizes the weakest useful one-variable contraction found so far:
**one-way witness dominance**.

It is strictly weaker than semantic equivalence of two residuals.

## 2. Exact one-variable quotient identity

Write an arbitrary CNF around one variable x as

```text
F(x,Y)
=
C(Y)
AND
AND_i (x OR A_i(Y))
AND
AND_j (NOT x OR B_j(Y)),
```

where C contains no x.

Define the two residuals

```text
R_0(Y)
=
C(Y) AND AND_i A_i(Y)

R_1(Y)
=
C(Y) AND AND_j B_j(Y).
```

Then

```text
exists x F(x,Y)
iff
R_0(Y) OR R_1(Y).
```

Proof: if x=0 every positive x-clause requires A_i and every negative x-clause
is automatically true; if x=1 the roles reverse.

This is the exact Davis-Putnam/Shannon semantic split written without
materializing pairwise resolvents.

## 3. Why the naive extension does not compress choice

Introduce Boolean abbreviations

```text
P := R_0(Y)
N := R_1(Y).
```

Then the quotient is P OR N.

If one encodes this disjunction by a fresh choice bit s,

```text
exists s [
  (s OR P)
  AND
  (NOT s OR N)
],
```

then s=0 selects P and s=1 selects N.

So the naive quotient-extension merely replaces x by another selector bit.

There is no strict progress in choice dimension.

The missing ingredient is a theorem that lets us **delete one branch entirely**.

## 4. Witness dominance

### Definition

Say

```text
R_0 <=_w R_1
```

when there is a polynomially checkable certificate proving the existence of a
polynomial-time map

```text
mu : Mod(R_0) -> Mod(R_1).
```

Only one direction is required.

The map need not be injective or surjective and may destroy multiplicity.

### Theorem WDQ-1

If

```text
R_0 <=_w R_1,
```

then

```text
SAT(F)
iff
SAT(R_1).
```

#### Proof

If R_1 is satisfiable, set x=1. The resulting assignment satisfies F.

Conversely, if F is satisfiable, either its x=1 branch already gives a model of
R_1, or x=0 gives a model y of R_0. By the dominance certificate, mu(y) is a
model of R_1.

Thus R_1 is satisfiable.

QED.

Witness reconstruction from the contracted instance is trivial: any model of
R_1 lifts to a model of F by setting x=1.

The symmetric theorem holds for R_1 <=_w R_0.

## 5. Exact contraction operator

Define

```text
WITNESS_DOMINANCE_CONTRACT(F,x,certificate).
```

If the certificate proves R_0 <=_w R_1, output R_1.
If it proves R_1 <=_w R_0, output R_0.
Otherwise return NO_MOVE.

For every successful contraction:

```text
SAT preserved exactly
witness lift = polynomial
number of live variables drops by 1
formula size does not increase.
```

Hence the lexicographic potential

```text
Phi(F)
=
(
 number of live Boolean variables,
 total literal occurrences
)
```

strictly decreases.

Any sequence of successful contractions has length at most the original number
of variables.

This is a genuine multiplicity-destroying quotient:
the dominated branch is not stored, enumerated, or represented by a new
selector.

## 6. A polynomial certificate family

One concrete proof-carrying family is
**signed-literal-permutation subsumption dominance**.

A certificate contains a signed permutation pi of the residual variables.

For every target clause D of R_1 the verifier supplies a source clause C of
R_0 such that

```text
pi(C) subseteq D.
```

Any assignment satisfying R_0 maps under pi to an assignment satisfying every
target clause D, hence to a model of R_1.

Verification is polynomial in the two residual descriptions.

Ordinary identity subsumption is the special case pi=id.

This family includes ordinary syntactic dominance and some exact symmetry /
renaming contractions without invoking semantic equivalence.

## 7. Explicit limit of the first certificate family

The checker supplies two residual 2-CNFs on variables a,b,c:

```text
R_0
=
NOT a
AND
NOT b

R_1
=
NOT a
AND
(NOT b OR NOT c)
AND
(b OR c).
```

Their model sets are

```text
Mod(R_0)
=
{000,001}

Mod(R_1)
=
{001,010}.
```

Both have cardinality two.

The two R_0 models have Hamming distance one.
The two R_1 models have Hamming distance two.

Signed variable permutations and complementation preserve Hamming distance.

Therefore no signed permutation maps Mod(R_0) into Mod(R_1), and none maps
Mod(R_1) into Mod(R_0).

Because the sets have equal cardinality, any signed-permutation inclusion would
have to be equality, so the obstruction is exact.

Embed these residuals into one 3CNF star:

```text
(x OR NOT a)
AND
(x OR NOT b)

AND
(NOT x OR NOT a)
AND
(NOT x OR NOT b OR NOT c)
AND
(NOT x OR b OR c).
```

Then:

```text
F[x=0] = R_0
F[x=1] = R_1.
```

So the signed-permutation certificate family is not universally available even
for one exact 3CNF variable star.

This does not block richer witness-dominance certificates.

## 8. Relation to Boundary Myhill-Nerode

Boundary Myhill-Nerode equivalence requires equality of extension relations in
order to preserve satisfiability under **all possible future contexts**.

Witness dominance here is deliberately weaker and whole-instance specific.

We require only

```text
SAT(R_0) => SAT(R_1)
```

with a proof-carrying witness map.

Therefore two residuals can be contracted even when their model sets and
boundary relations differ.

This is exactly the intended multiplicity-destroying direction.

## 9. Grouped generalization

For a block B of k variables there are residuals R_alpha for
alpha in {0,1}^k.

If one representative alpha* has certified witness dominance from every other
branch,

```text
for all alpha:
R_alpha <=_w R_alpha*,
```

then the entire block B can be deleted in one exact contraction:

```text
SAT(F)
iff
SAT(R_alpha*).
```

The potential drops by k and no selector remains.

A more general quotient with q>1 representatives may still compress choice,
but requires a separate cumulative-state theorem and is not promoted here.

## 10. Active universal subgate

Freeze:

```text
R5_E9
WITNESS_DOMINANCE_BLOCK_EXISTENCE_GATE_V1
```

Question:

For every nonterminal rigid JANUS overlay torso, can one polynomially find either

1. a nonempty variable block B and one representative branch alpha* together
   with polynomially verifiable dominance certificates
   R_alpha <=_w R_alpha* for every branch alpha; or

2. a direct normalization into an already proved polynomial terminal class?

Required firewalls:

- no SAT oracle to discover alpha*;
- no enumeration of 2^|B| branches unless |B| is independently O(log L) and
  total cumulative work is polynomial;
- certificates must be polynomially verifiable;
- output size may not increase superpolynomially;
- every contraction must strictly reduce an explicit polynomially bounded
  potential.

## 11. Status

```text
ONE-VARIABLE EXISTENTIAL QUOTIENT IDENTITY
=
PASS

NAIVE CHOICE-BIT EXTENSION
=
SELECTOR CONSERVATION / NO PROGRESS

WITNESS-DOMINANCE CONTRACTION
=
PASS EXACT PARTIAL ALGORITHM

STRICT VARIABLE-COUNT POTENTIAL DROP
=
PASS

SIGNED-PERMUTATION / SUBSUMPTION CERTIFICATE FAMILY
=
PASS POLY-VERIFIABLE

SIGNED-PERMUTATION UNIVERSAL EXISTENCE
=
FALSIFIED BY EXPLICIT 3CNF STAR

RICHER / GROUPED WITNESS DOMINANCE
=
OPEN <<< NEW ALGORITHMIC TARGET

D1
=
EMPTY

P_VS_NP
=
OPEN
```
