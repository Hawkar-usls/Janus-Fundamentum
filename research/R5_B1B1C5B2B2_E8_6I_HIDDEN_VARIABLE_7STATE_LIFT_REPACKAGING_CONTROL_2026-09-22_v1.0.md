# R5 E8 6I — Hidden-Variable 7-State Lift Repackaging Control

Date: 2026-09-22

Authority: `PROVED_EXACT_REDUCTION_CONTROL_PLUS_SOURCE_BOUND_LOCAL_CONSISTENCY_CONTROL__NO_D1_PROMOTION`

## 1. External source

Fahiem Bacchus, Xinguang Chen, Peter van Beek, Toby Walsh,
*Binary vs. non-binary constraints*,
Artificial Intelligence 140 (2002), 1–37.

DOI:

https://doi.org/10.1016/S0004-3702(02)00210-2

The source studies the dual and hidden-variable transformations from finite-domain non-binary CSPs to binary CSPs.

Among its exact comparison results, enforcing arc consistency on the hidden-variable transformation has the same inferential power as enforcing the corresponding consistency on the original non-binary formulation.

This is used here only as a local-consistency control.

## 2. Frozen 3-SAT hidden-variable template

Let:

```text
D_B
=
{0,1}
```

be the Boolean-variable sort.

Let:

```text
D_C
=
{0,1}^3 \ {(0,0,0)}
```

be the clause-state sort.

A clause-state tuple records the truth values of its three **literals**, not of its underlying variables.

Thus every clause variable has exactly seven legal states.

For each clause position:

```text
j in {1,2,3}
```

and sign:

```text
s in {POS,NEG},
```

define a fixed binary compatibility relation between clause state `q in D_C` and Boolean variable value `b in D_B`:

```text
R_{j,POS}(q,b)
iff
q_j=b;

R_{j,NEG}(q,b)
iff
q_j=1-b.
```

The resulting two-sorted relational template is fixed and finite.

Call it:

```text
Gamma_HVE_3SAT.
```

## 3. Exact linear reduction

For an arbitrary 3-CNF formula `F`:

1. create one Boolean-sort variable for every SAT variable;
2. create one clause-sort variable for every clause;
3. connect each clause-sort variable to its three Boolean variables using the corresponding fixed relation `R_{j,s}`.

The construction uses:

```text
n+m
variables

3m
binary constraints

constant-size relation tables.
```

Therefore:

```text
T_construct
=
O(|F|).
```

### Soundness

Any solution of the lifted CSP assigns each clause variable a nonzero literal-truth tuple.

Compatibility forces each tuple coordinate to equal the truth value of the corresponding literal.

Hence every original clause has at least one true literal.

Therefore the recovered Boolean assignment satisfies `F`.

### Completeness

Given any satisfying Boolean assignment of `F`, assign each clause variable the three induced literal truth values.

Because the clause is satisfied, this tuple is nonzero and therefore belongs to `D_C`.

All binary compatibility constraints hold.

Thus:

```text
F in SAT
iff
HVE(F) -> Gamma_HVE_3SAT.
```

Reconstruction is linear.

## 4. Complexity consequence

3-SAT reduces in linear time to the fixed-template two-sorted CSP:

```text
CSP(Gamma_HVE_3SAT).
```

Conversely the lifted CSP is plainly in NP.

Therefore:

```text
CSP(Gamma_HVE_3SAT)
=
NP-complete.
```

This is not a conditional statement and does not assume `P != NP`.

It only identifies the exact complexity of the representation under ordinary polynomial reductions.

## 5. Meaning for 6I

The 7-state clause lift does achieve:

```text
EXACT SEMANTICS
=
YES

POLY CONSTRUCTION
=
YES

POLY RECONSTRUCTION
=
YES

LOCAL CLAUSE SATISFACTION
=
BUILT INTO THE CLAUSE DOMAIN
```

but:

```text
GLOBAL CONSISTENCY
=
THE ORIGINAL NP-COMPLETE INTERACTION PROBLEM
```

encoded in the fixed binary projection relations.

Therefore:

```text
RICHER DOMAIN
ALONE
!=
TRACTABLE INTERACTION.
```

The old hidden-variable representation is a useful mechanism donor but not a universal polynomial solver.

The Bacchus–Chen–van Beek–Walsh local-consistency comparison additionally warns that ordinary arc-consistency enforcement on this encoding does not produce extra inferential power relative to the original formulation.

## 6. Relation to previous JANUS barriers

This control is distinct from:

```text
BOOLEAN OCCURRENCE SPLITTING
=
only coordinate conjugation;

HVE 7-STATE LIFT
=
genuine larger-domain exact representation.
```

The first fails to expand B4 coverage.

The second genuinely changes the carrier but moves the original hardness into cross-sort compatibility.

It is therefore another exact instance of:

```text
COMPACT / LOCAL REPRESENTATION
!=
TRACTABLE GLOBAL CONSISTENCY.
```

## 7. What a useful lifted carrier must do

A future lifted-domain candidate must supply more than tuple storage.

It needs a polynomial exact interaction invariant that compresses or algebraically controls the cross-clause compatibility **without**:

- enumerating satisfying assignments;
- solving the HVE CSP as a hidden SAT call;
- using an unbounded interface table;
- falling back to a bounded-width/backdoor assumption.

## 8. Claim ceiling

```text
NAIVE 7-STATE HIDDEN-VARIABLE LIFT
=
EXACT BUT NP-COMPLETE REPACKAGING

GENERAL LIFTED-DOMAIN PREPROCESSING
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
