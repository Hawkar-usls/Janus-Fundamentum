# R5 E8 6I — Three-Sheet Majority Cover and Selector-Repackaging Control

Date: 2026-09-22

Authority: `PROVED_BOOLEAN_DECOMPOSITION_PLUS_EXACT_HIDDEN_CHOICE_CONTROL__NO_D1_PROMOTION`

## 1. Parent positive controls

The current corpus contains two exact polynomial lifecycle controls whose coverage is threshold-two:

1. `A3` semilattice-block-Mal'tsev lift;
2. pure `F2^2` Mal'tsev affine lift.

Both admit local exact lifted relations when the corresponding coarse decoder condition has at least two satisfied literals.

The universal gap remains:

```text
AT_LEAST_2_OF_3
->
AT_LEAST_1_OF_3.
```

## 2. Exact three-sheet Boolean identity

For Boolean literal truth values:

```text
a,b,c in {0,1},
```

let:

```text
M0(a,b,c)
=
MAJ(a,b,c);

M1(a,b,c)
=
MAJ(a,NOT b,c);

M2(a,b,c)
=
MAJ(a,b,NOT c).
```

Then:

```text
OR3(a,b,c)
=
M0(a,b,c)
OR
M1(a,b,c)
OR
M2(a,b,c).
```

Checker:

`research/tools/r5_e8_6i_three_sheet_majority_cover_checker.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_THREE_SHEET_MAJORITY_COVER_2026-09-22_v1.0.json`

The checker verifies all eight Boolean input rows and all eight signed 3-clause variants.

The cover is minimal within the four signed-majority sheets that individually exclude `000`:

```text
minimum sheet count
=
3.
```

## 3. Interpretation using the sealed A3 mechanism

The A3 control already gives an exact polynomial lift for every threshold-two signed majority sheet.

Therefore ordinary OR3 can be viewed as:

```text
OR3
=
UNION OF THREE
A3-ADMISSIBLE EXACT SHEETS.
```

This is a meaningful structural decomposition.

It says that local clause semantics are no longer the missing object.

The missing object is the composition of the three sheets.

## 4. Explicit selector representation

Introduce a three-valued selector:

```text
s in {0,1,2}
```

and define the four-ary relation:

```text
T(s,a,b,c)
```

by:

```text
s=0 => M0(a,b,c);
s=1 => M1(a,b,c);
s=2 => M2(a,b,c).
```

Then exactly:

```text
exists s T(s,a,b,c)
iff
OR3(a,b,c).
```

For an arbitrary signed 3-CNF `F`, add one independent selector variable `s_C` per clause and replace every clause by the corresponding signed version of `T`.

Construction size is linear.

## 5. Selector-repackaging theorem

The selector instance is satisfiable iff the original 3-CNF is satisfiable.

### Completeness

Given a satisfying Boolean assignment, every satisfied clause has a nonzero literal-truth row.

By the three-sheet identity, at least one sheet accepts that row.

Choose such a selector value for that clause.

### Soundness

If a selector instance is satisfied, then every selected majority sheet implies the original OR3 clause by the exact identity.

Therefore the Boolean variable assignment satisfies the original 3-CNF.

Thus:

```text
3SAT
<=_m^linear
THREE_SHEET_SELECTOR_CSP.
```

The selector CSP is plainly in NP.

Therefore:

```text
THREE_SHEET_SELECTOR_CSP
=
NP-COMPLETE.
```

This conclusion is unconditional and does not assume `P != NP`.

## 6. Why this matters

Each individual sheet is already handled by a polynomial A3 lifecycle.

But:

```text
POLY SHEET 0
+
POLY SHEET 1
+
POLY SHEET 2
+
INDEPENDENT CLAUSE-WISE CHOICE

=
NP-COMPLETE INTERACTION.
```

This is an exact instance of the corpus-first doctrine:

```text
POLY MECHANISM A
+
POLY MECHANISM B
!=
POLY UNIVERSAL SOLVER

WITHOUT A POLYNOMIAL
INTERFACE THEOREM.
```

The hard object is now isolated to the interface.

## 7. Source-bound composition donors

### Semilattice-block Mal'tsev

Andrei A. Bulatov,
*Constraint Satisfaction Problems over semilattice block Mal'tsev algebras*,
arXiv:1701.02623 / Information and Computation 268 (2019), 104437.

The source proves polynomial CSP solving for a semilattice quotient combined with Mal'tsev residual blocks.

This remains the primary solver donor for an algebraic composition layer.

### Płonka / semilattice sums

Classical Płonka sums construct one algebra from a semilattice-indexed system of algebras using connecting homomorphisms.

This is a structural composition donor only.

No claim is made here that a Płonka sum of the three majority sheets automatically gives an exact OR3 solver.

The exact compatibility interface must be proved.

## 8. New exact composition target

Freeze:

```text
R5_E8_6I_ALGEBRAIC_SHEET_ABSORPTION_GATE_V1
```

The goal is not to choose a sheet.

The goal is to construct one polynomially tractable algebraic carrier in which the three exact threshold-two sheets are absorbed into one exact OR3-compatible relation without exposing an independent semantic selector.

A candidate must satisfy all:

### S1 — exact local semantics

For every signed 3-clause:

```text
decoded lifted relation
=
exact signed OR3.
```

### S2 — sheet absorption

The three A3-admissible sheets are combined by algebraic closure / block composition.

No independent per-clause selector may remain as an unresolved choice variable.

### S3 — source-bound tractable carrier

The composed relations must be preserved by a fixed source-bound tractable algebraic structure, for example:

```text
SBM
Mal'tsev / few-subpowers
bounded-width
or another proved tractable carrier.
```

### S4 — global variable coherence

One lifted state per original SAT variable must participate consistently in every clause occurrence.

No occurrence-wise witness choice may bypass exact Boolean reconstruction.

### S5 — exact reconstruction

Every lifted solution decodes in polynomial time to one Boolean assignment satisfying the original formula.

### S6 — completeness

Every Boolean satisfying assignment, or an explicitly proved polynomially obtainable equivalent witness, must lift to a global composed solution.

### S7 — total lifecycle

```text
T_construct
+
T_composition_certificate
+
T_lifted_solve
+
T_reconstruct
+
T_verify
+
T_history

<=
poly(L).
```

### S8 — hidden-choice firewall

Reject any construction whose sheet/block labels form a CSP polynomially equivalent to the original 3-SAT instance.

The explicit three-valued selector construction is the frozen negative control.

## 9. Current conceptual frontier

We now have:

```text
LOCAL OR3 SEMANTICS
=
COVERED BY THREE EXACT POLY SHEETS

NAIVE SHEET CHOICE
=
NP-COMPLETE REPACKAGING

MISSING OBJECT
=
ALGEBRAIC SHEET ABSORPTION
WITH POLYNOMIAL GLOBAL INTERACTION
```

This is more precise than searching for an arbitrary larger domain.

A larger carrier is interesting only if it proves S1–S8.

## 10. Claim ceiling

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

THREE-SHEET LOCAL COVER
=
PROVED

EXPLICIT SELECTOR COMPOSITION
=
REJECTED AS NP-COMPLETE REPACKAGING

ALGEBRAIC SHEET ABSORPTION
=
OPEN
```
