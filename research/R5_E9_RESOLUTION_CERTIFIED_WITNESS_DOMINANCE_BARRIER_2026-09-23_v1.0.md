# R5 E9 — Resolution-Certified Witness-Dominance Barrier

Date: 2026-09-23

Authority:
`JANUS_DERIVED_COMPOSITION_BARRIER + SOURCE_RESOLUTION_LOWER_BOUND__NO_P_NE_NP_ASSUMPTION__NO_D1_PROMOTION`

Parent:

`R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION_2026-09-23_v1.0`

Source lower bound:

Eli Ben-Sasson and Avi Wigderson,
*Short Proofs Are Narrow — Resolution Made Simple*,
JACM 48(2), 2001.

For Tseitin contradictions on constant-degree expander graphs they obtain
exponential Resolution size lower bounds.

## 1. Candidate certificate system

For one variable x write

```text
F
=
C
AND
AND_i (x OR A_i)
AND
AND_j (NOT x OR B_j).
```

The residuals are

```text
R_0 = C AND AND_i A_i
R_1 = C AND AND_j B_j.
```

Suppose we want to contract to R_1.

A **Resolution dominance certificate** supplies, for every non-common target
clause B_j, a Resolution derivation

```text
R_0 |-Res B_j.
```

Then every model of R_0 satisfies R_1, so the identity map on remaining
variables is a witness-dominance map.

By the WDQ theorem:

```text
SAT(F)
iff
SAT(R_1).
```

## 2. Proof-lifting lemma

### Lemma RDC-1

Every Resolution derivation

```text
R_0 |-Res D
```

can be lifted to a derivation

```text
F |-Res D
```

with only linear/additive overhead relative to the supplied derivation.

### Proof

Every non-common source clause A_i of R_0 occurs in F as

```text
x OR A_i.
```

Take the supplied Resolution proof of D from the A_i and common C clauses.

For every proof clause E derived from an A-side clause, carry the extra literal x:

```text
E
->
x OR E.
```

Resolution is stable under this common weakening: if the original proof resolves

```text
E OR z
and
G OR NOT z
```

to E OR G, then the lifted clauses

```text
x OR E OR z
and
x OR G OR NOT z
```

resolve to

```text
x OR E OR G.
```

Thus we derive

```text
x OR D.
```

For D=B_j the current formula F already contains

```text
NOT x OR B_j.
```

Resolve the two clauses on x:

```text
(x OR B_j),
(NOT x OR B_j)
|-Res
B_j.
```

Common C clauses require no lifting.

Hence every clause of the kept residual R_1 is Resolution-derivable from F.

QED.

The x=0 kept-branch case is symmetric.

## 3. Composition over many contractions

Suppose an UNSAT CNF F_0 is reduced by a sequence

```text
F_0
-> F_1
-> ...
-> F_t
```

where every step is a one-variable witness-dominance contraction certified by
Resolution as above.

By Lemma RDC-1:

```text
F_i |-Res every clause of F_{i+1}.
```

Therefore Resolution proofs compose across the contraction sequence.

If all variables are eventually eliminated, an unsatisfiable variable-free
terminal formula contains the empty clause and has a trivial refutation.

More generally any terminal class equipped with polynomial Resolution
refutations can be appended.

Hence a contraction sequence whose

- number of steps is polynomial,
- total certificate size is polynomial,
- intermediate formulas remain polynomial,

yields a polynomial-size Resolution refutation of the original UNSAT formula.

## 4. Source lower-bound contradiction

Take the standard Tseitin contradictions on constant-degree expander graphs.

Ben-Sasson and Wigderson prove exponential Resolution size for this family.

Therefore no algorithm can, for every such instance, eliminate the whole hard
core using only polynomial-total-size Resolution-certified witness-dominance
contractions and end in a trivially / polynomial-Resolution-refutable terminal.

This is unconditional.

It is a lower bound on this certificate system, not on SAT algorithms in
general.

## 5. Consequence for the new quotient lane

Useful:

```text
RESOLUTION-CERTIFIED BRANCH DOMINANCE
=
VALID EXACT CONTRACTION MODULE.
```

Not universal:

```text
POLY-TOTAL RESOLUTION DOMINANCE
AS THE ONLY UNIVERSAL QUOTIENT CURRENCY
=
BLOCKED.
```

Therefore a successful universal witness-dominance algorithm must at some point
use a certificate/lift mechanism that is not compilable into polynomial
Resolution in this way.

Possible surviving directions include:

- autarky/matching/LP certificates;
- algebraic witness maps;
- grouped quotient maps changing many residual variables at once;
- proof systems strictly outside the Resolution-lifting argument;
- representation-changing contractions whose certificates do not derive the
  kept residual clause-by-clause.

## 6. Relation to multiplicity destruction

This barrier does not undo the central insight.

Witness dominance is still strictly weaker than equivalence and can destroy
model multiplicity.

The result says only that **one obvious proof-carrying implementation** —
clause-by-clause Resolution implication — cannot be the whole universal answer.

## 7. Updated target

```text
WITNESS-DOMINANCE META-THEOREM
=
PASS

AUTARKY SUBSYSTEM
=
SOURCE-PROVED PARTIAL DONOR

SIGNED-PERMUTATION DOMINANCE
=
NOT UNIVERSAL

RESOLUTION-CERTIFIED DOMINANCE
=
NOT UNIVERSAL BY EXPONENTIAL RESOLUTION LOWER BOUNDS

SURVIVING TARGET
=
NON-RESOLUTION
GROUPED WITNESS MAP / QUOTIENT
WITH STRICT POTENTIAL DROP

D1
=
EMPTY

P_VS_NP
=
OPEN
```
