# R5 E9 — Autarky as a Source-Proved Witness-Dominance Contraction Donor

Date: 2026-09-23

Authority:
`SOURCE_BOUND_DONOR_COMPOSED_WITH_JANUS_WITNESS_DOMINANCE__NO_NOVELTY_CLAIM_FOR_AUTARKIES__NO_D1_PROMOTION`

Parent:

`R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION_2026-09-23_v1.0`

## 1. JANUS interpretation

A SAT autarky is a partial assignment phi on a variable set B such that every
clause touched by B is already satisfied by phi.

Let T be the touched clauses and U the untouched clauses.

Because no variable of B occurs in U,

```text
F
=
T AND U
```

and phi satisfies T independently of the values of variables outside B.

Therefore

```text
SAT(F)
iff
SAT(U).
```

Every witness of U lifts by adjoining phi.

Thus an autarky is exactly a grouped witness-dominance contraction with one
representative internal branch.

It destroys all other assignments to B and keeps only one certified branch.

## 2. Exact contraction properties

For every nonempty autarky:

- touched clauses are deleted;
- assigned variables can be removed after ordinary simplification;
- SAT is preserved in both directions;
- witness reconstruction is explicit;
- formula size decreases;
- no selector is introduced.

Hence autarky reduction satisfies the JANUS quotient contract.

## 3. Source-proved polynomial subclasses

Kullmann's autarky/lean-clause-set theory provides restricted autarky systems
with polynomial reduction algorithms.

### Linear autarkies

Kullmann, *Investigations on autark assignments*, Discrete Applied Mathematics
107 (2001), develops linear autarkies and states that the largest linearly lean
sub-clause-set / largest linear-autark subset decomposition is polynomially
computable using linear programming.

### Matching autarkies

Kullmann, *Lean clause-sets: generalizations of minimally unsatisfiable
clause-sets*, Discrete Applied Mathematics 130 (2003), develops matching
autarkies and matching-lean kernels.

The later Kullmann-Zhao account of matching-lean clause-sets records that every
clause-set has a largest matching-lean kernel, computable in polynomial time,
e.g. by matching-autarky reduction.

Thus:

```text
ARBITRARY CNF
  ->
MATCHING / LINEAR AUTARKY REDUCTION
  ->
LEANER CNF
```

is an exact source-backed polynomial contraction module.

## 4. Why this does not solve the active gate

General nontrivial autarky existence is NP-complete.

Therefore:

```text
"find any possible autarky"
```

cannot simply be used as a free polynomial oracle.

Furthermore formulas can be matching-lean / linearly lean while still being
nontrivial SAT instances.

So the source donor gives a genuine reduction rule, not a universal solver.

## 5. Why witness dominance is strictly broader

Autarky contraction requires the selected assignment on B to satisfy every
clause it touches **without changing the remaining variables**.

Witness dominance only requires a certified polynomial map

```text
Mod(R_alpha)
->
Mod(R_alpha*)
```

between whole residual branches.

The map may alter the remaining variables.

Therefore witness dominance can in principle contract branches even when no
autarky exists.

This is the mathematical reason to keep the JANUS abstraction rather than
rename the whole route "autarky search."

## 6. Composed preprocessing lane

Before invoking the harder rigid-torso quotient search:

1. perform all source-proved polynomial autarky reductions available in the
   chosen system;
2. simplify and rebuild the exact overlay / SPQR decomposition;
3. apply ordinary certified witness-dominance contractions;
4. only then expose the remaining lean rigid torso to the nonlocal grouped
   quotient gate.

Every successful step strictly reduces a simple size potential.

## 7. Active residual object

Define:

```text
AUTARKY_REDUCED_WITNESS_DOMINANCE_RIGID_CORE
```

as a rigid torso after:

- adhesion <=2 exact contraction;
- polynomial matching/linear autarky reduction;
- all currently certified branch-dominance contractions.

The new discovery problem is:

```text
Does every nonterminal such core admit
a richer polynomially verifiable
whole-instance witness-dominance quotient,
or another already-proved terminal normalization?
```

No universal answer is claimed.

## 8. Ceiling

```text
AUTARKY AS WITNESS-DOMINANCE SPECIAL CASE
=
PASS

MATCHING / LINEAR AUTARKY REDUCTION
=
SOURCE-PROVED POLYNOMIAL DONOR

GENERAL AUTARKY DISCOVERY
=
NP-COMPLETE

WITNESS-DOMINANCE STRICTLY BROADER
=
YES

UNIVERSAL WITNESS-DOMINANCE EXISTENCE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
