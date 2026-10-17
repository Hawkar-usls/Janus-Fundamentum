# R5 E9 — Witness-Selection Bilinear Hankel-Rank Barrier

Date: 2026-09-28

Status: `JANUS_DERIVED_SCOPED_EXPONENTIAL_LINEAR_STATE_BARRIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_PATH_XOR_AND_OVERLAY_NORMAL_FORM_2026-09-23_v1.0.md`
- `research/R5_E9_BOUNDARY_MYHILL_NERODE_AND_NAE4PART_STRESS_FRONTIER_2026-09-23_v1.0.md`
- `research/R5_E9_CYCLE_SYNDROME_HOMOLOGY_DELTA_MATROID_BOUNDARY_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_witness_selection_bilinear_hankel_rank.py`

Scientific ceiling:

```text
THIS IS NOT A LOWER BOUND FOR SAT.
THIS DOES NOT RULE OUT NONLINEAR, ADAPTIVE, RANDOMIZED, SOURCE-SPECIFIC,
OR REPRESENTATION-CHANGING POLYNOMIAL ALGORITHMS.

IT RULES OUT ONE PRECISE PROPOSAL CLASS:
AN EXACT POLYNOMIAL-DIMENSIONAL LINEAR/BILINEAR ANNIHILATION SUMMARY WHOSE
CROSS-BLOCK JOIN IS READ BY A BILINEAR SCALAR ZERO/NONZERO TEST.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact witness-selection normal form

For an arbitrary CNF formula, create one vertex for every literal occurrence.
Partition occurrence vertices by source clause.

A **selector witness** chooses exactly one occurrence from every clause.
It is globally consistent iff no source variable is chosen in both polarities.

This is exactly SAT:

- from a satisfying assignment, choose one true literal occurrence in every clause;
- from a consistent selector, assign every source variable according to the
  polarity selected for it (arbitrary on variables never selected).

Thus the only global compatibility rule in selector space is

```text
never select both +x and -x.
```

Equivalently, conflicts for one source variable form the complete biclique
between its positive and negative occurrence sets.

## 2. Independent polarity-channel interface family

Fix `m` distinct source-variable channels `x_1,...,x_m`.
Consider left and right partial selector states that have already selected one
polarity for every channel.

Index a left state by

```text
s in {+,-}^m
```

and a right state by

```text
t in {+,-}^m.
```

Because both sides select a polarity for every channel, their union is globally
consistent iff they select the same polarity on every channel:

```text
COMPATIBLE(s,t) iff s=t.
```

Therefore the exact cross-interface compatibility matrix has the zero pattern
of the `2^m x 2^m` identity matrix.

This family is an interface stress family; it is not asserted that an arbitrary
SAT algorithm must expose this particular cut.

## 3. Bilinear-summary model

Let `K` be any field.  Suppose an exact proposed annihilation scheme represents
left and right partial selector states by vectors

```text
u_s in K^d,
v_t in K^d,
```

and joins them by one bilinear scalar form

```text
B : K^d x K^d -> K
```

with exact zero semantics

```text
B(u_s,v_t) != 0  iff  s and t are compatible.
```

This includes any finite-dimensional algebra scheme in which block summaries
are multiplied bilinearly and then observed by a linear scalar readout.

Choose a matrix `Q` for `B` and matrices `U,V` whose rows are the summaries.
The connection matrix is

```text
H = U Q V^T.
```

Hence

```text
rank_K(H) <= d.
```

## 4. Exact exponential rank theorem

### Theorem WSH-1

Every exact bilinear-summary scheme above satisfies

\[
\boxed{d\ge 2^m.}
\]

### Proof

By Section 2, `H[s,t]=0` for every `s!=t`, while every diagonal entry
`H[s,s]` is nonzero.  Therefore `H` is a diagonal matrix with `2^m` nonzero
diagonal entries.  Over every field,

```text
rank_K(H)=2^m.
```

But Section 3 gives `rank_K(H)<=d`.  Thus `d>=2^m`. QED.

No asymptotics, complexity assumptions, or finite experiments enter the proof.

## 5. Consequence for the tempting annihilation algebra

A natural SAT zero-test proposal is:

```text
- give +x and -x algebra elements that annihilate each other;
- sum the three literal elements inside every clause;
- multiply all clause sums;
- declare SAT iff the final product is nonzero.
```

If the cross-block semantics of such a proposal are carried by a
polynomial-dimensional linear state and exact bilinear scalar zero test, WSH-1
shows that it cannot represent `m` independent polarity channels once `m` is
linear: the required state dimension is at least `2^m`.

The familiar explicit partial-assignment algebra with per-variable states

```text
NONE / PLUS / MINUS
```

indeed has exponential tensor-product dimension.  WSH-1 shows that this is not
merely an artifact of that obvious basis inside the scoped bilinear model.

## 6. Relation to rank / communication methods

The proof is the elementary connection-matrix rank method: an exact bilinear
factorization of a matrix has inner dimension at least its matrix rank.
The rank method is standard in communication complexity and Hankel/weighted-
automata theory.  JANUS uses only the self-contained factorization argument
above; no external lower-bound theorem is imported.

## 7. What remains open

WSH-1 does **not** exclude:

```text
- nonlinear succinct summaries with polynomial exact operations;
- adaptive contraction rules that change the representation after each step;
- source-generated auxiliary variables that destroy the independent-channel cut;
- non-bilinear composition;
- algorithms that never materialize such a selector interface;
- a genuine polynomial SAT algorithm by an entirely different mechanism.
```

Therefore the admissible frontier remains representation-changing/global.
In the current JANUS stack the strongest exact source-specific object is the
cycle endpoint-syndrome gate:

```text
R5_E9_CYCLE_ENDPOINT_SYNDROME_GLOBAL_QUOTIENT_GATE_V1
```

and, for arbitrary signed 3CNF, the high-girth-safe nonlocal GLOBAL_PIVOT gate.

## 8. Anti-loop freeze

```text
POLYNOMIAL-DIMENSIONAL EXACT BILINEAR POLARITY-ANNIHILATION SUMMARY
= CLOSED BY rank >= 2^m.

CLAUSE-SUM TIMES CLAUSE-SUM ZERO TEST
= NOT A POLYNOMIAL SOLVER MERELY FROM A SMALL LINEAR/BILINEAR STATE CLAIM.

SAT LOWER BOUND
= NOT CLAIMED.

UNIVERSAL POLYNOMIAL DECIDER
= OPEN.

E8_D1
= EMPTY.

P_VS_NP
= OPEN.
```
