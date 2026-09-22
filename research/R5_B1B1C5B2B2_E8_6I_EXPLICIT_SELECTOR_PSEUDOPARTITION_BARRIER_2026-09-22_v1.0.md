# R5 E8 6I — Explicit Selector Pseudopartition Barrier

Date: 2026-09-22

Authority: `PROVED_EXACT_FINITE_ALGEBRAIC_BARRIER__SCOPED_MODEL_ONLY__NO_D1_PROMOTION`

## Parent objects

- `research/R5_B1B1C5B2B2_E8_6I_THREE_SHEET_MAJORITY_COVER_AND_SELECTOR_CONTROL_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_A3_SBM_MAJORITY_LIFT_POSITIVE_CONTROL_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_CORPUS_FIRST_MECHANISM_SYNTHESIS_DOCTRINE_2026-09-22_v1.0.md`

Checker:

`research/tools/r5_e8_6i_explicit_selector_pseudopartition_checker.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_EXPLICIT_SELECTOR_PSEUDOPARTITION_BARRIER_2026-09-22_v1.0.json`

## 1. Relation under test

Freeze the exact three-sheet selector relation:

```text
T(s,a,b,c)

s=0 => MAJ(a,b,c)
s=1 => MAJ(a,NOT b,c)
s=2 => MAJ(a,b,NOT c)
```

with:

```text
s in {0,1,2}
a,b,c in {0,1}.
```

The previously sealed three-sheet theorem gives:

```text
exists s T(s,a,b,c)
iff
OR3(a,b,c).
```

The explicit selector CSP is an exact 3-SAT repackaging and is therefore not progress by itself.

## 2. Old structural donor being tested

Bergman–Failing prove:

```text
finite idempotent algebra
+
pseudopartition operation
+
every semilattice-replica block
in one tractable variety

=>
tractable CSP.
```

Source:

Clifford Bergman, David Failing,
*Commutative, idempotent groupoids and the constraint satisfaction problem*,
Algebra Universalis 73 (2015), 391–417,
Theorem 4.1.

Open manuscript:
https://faculty.sites.iastate.edu/cbergman/files/inline-files/cigcsp.pdf

Bergman–DeMeo later use Płonka sums of tractable fibres as an explicit tractability-composition donor.

Source:

Clifford Bergman, William DeMeo,
*Universal Algebraic Methods for Constraint Satisfaction Problems*,
Logical Methods in Computer Science 18(1), 2022.

https://lmcs.episciences.org/8975

These sources justify testing direct semilattice/pseudopartition absorption.

They do not assert that the present selector relation admits such an operation.

## 3. Exact finite classification

### Selector sort

The checker exhaustively enumerates every labelled binary semilattice operation on the three-element selector domain.

Exact count:

```text
9.
```

### Boolean visible sorts — idempotent case

Every idempotent Boolean binary operation is one of exactly four truth tables:

```text
AND
OR
PROJ_1
PROJ_2.
```

The three visible Boolean coordinates are allowed independent operations.

Therefore the exact candidate count is:

```text
9 * 4^3
=
576.
```

For every candidate the checker tests binary multisorted preservation of all pairs of tuples of T.

Result:

```text
PRESERVES T
=
0 / 576.
```

Hence no direct operation of the form

```text
selector:
3-element semilattice

visible a,b,c:
independent idempotent Boolean binary operations
```

preserves the exact selector relation.

## 4. All Boolean binary operations control

The Boolean coordinates were then expanded from the four idempotent binary operations to all:

```text
16
```

Boolean binary truth tables independently.

Candidate count:

```text
9 * 16^3
=
36864.
```

Exact preserving count:

```text
9.
```

In all nine preserving candidates the visible operation triple is exactly:

```text
(CONST_1, CONST_1, CONST_1).
```

The selector operation may be any of the nine semilattices.

Thus the only preservation gained by dropping visible idempotence is the trivial collapse:

```text
(a,b,c)
->
(1,1,1),
```

which satisfies every sheet but destroys the required Boolean value semantics.

## 5. Barrier theorem

```text
R5_E8_6I_EXPLICIT_SELECTOR_PSEUDOPARTITION_BARRIER_V1
```

For the frozen relation T:

```text
DIRECT
3-STATE SEMILATTICE SELECTOR SORT
+
IDEMPOTENT BINARY BOOLEAN VISIBLE SORTS
+
MULTISORTED BINARY PRESERVATION

=
IMPOSSIBLE.
```

Allowing arbitrary non-idempotent Boolean binary operations yields only the trivial all-true visible collapse.

Therefore the most direct Płonka/pseudopartition repair:

```text
"make the explicit clause selector
a semilattice coordinate
and absorb it algebraically"
```

is blocked in this exact finite model.

## 6. Scope firewall

This theorem does **not** block:

- general Płonka sums with a different visible carrier;
- semilattice-block Mal'tsev algebras on a larger domain;
- higher-arity polymorphisms;
- multi-sorted non-Boolean visible coordinates;
- representation-changing preprocessing;
- global refinement / independence certificates;
- nonlocal source-bound composition theorems.

It blocks only the direct explicit-selector binary semilattice/idempotent-Boolean absorption model tested above.

## 7. Consequence for the active frontier

Previously:

```text
independent selector per clause
=
NP-complete repackaging.
```

Now additionally:

```text
explicit selector
+
direct semilattice/pseudopartition absorption
on Boolean visible coordinates
=
algebraically blocked.
```

Therefore the next useful interface should not keep `s_C` as an independent semantic variable and merely try to hide it inside a direct semilattice block.

The next legitimate donor family is a global refinement / independence theorem that makes local sheet admissibility a consequence of a polynomial-size global structure.

## Claim ceiling

```text
EXPLICIT_SELECTOR_PSEUDOPARTITION_BARRIER
=
PROVED

GENERAL PLONKA / SBM
=
OPEN OUTSIDE THIS SCOPE

GLOBAL DISJUNCTIVE REFINEMENT
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
