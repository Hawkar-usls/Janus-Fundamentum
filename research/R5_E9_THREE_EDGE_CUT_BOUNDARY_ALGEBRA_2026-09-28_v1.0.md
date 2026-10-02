# R5 E9 — Exact three-edge-cut boundary algebra

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_COMPOSITION_THEOREM__CONSTANT_3CUT_SIGNATURE_ALGEBRA__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS PROVES CONSTANT-SIZE EXACT SEMANTICS FOR 3-EDGE INTERFACES.
IT DOES NOT SOLVE A 3-CUT-IRREDUCIBLE CORE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Use the dual/general-factor view of cubic Positive Exact-One on a cubic bipartite Levi graph.

- a variable/EQ vertex is either incident to zero selected edges or all three;
- a clause/EXACT1 vertex is incident to exactly one selected edge.

Let `B` be any vertex region whose edge boundary `D=delta(B)` has exactly three edges.
Let

```text
V_B = variable/EQ vertices inside B,
C_B = clause/EXACT1 vertices inside B,
q   = |C_B|.
```

Split the three boundary edges according to their endpoint inside B:

```text
D_V = boundary edges incident inside B with a variable vertex,
D_C = boundary edges incident inside B with a clause vertex,
r   = |D_V|,
|D_C|=3-r.
```

For a boundary bit-vector `y in {0,1}^D`, write

```text
a(y)=sum_{e in D_V} y_e,
b(y)=sum_{e in D_C} y_e.
```

Let `R_B` be the exact projected boundary relation: `y in R_B` iff the boundary bits extend to a valid Exact-One selection inside B.

## 2. Signed boundary count law

### Theorem 3CUT-1

For every `y in R_B`,

```text
a(y)-b(y) == -q (mod 3).
```

More strongly, if `k` is the number of selected variable vertices in `V_B`, then

```text
3k-q = a(y)-b(y).
```

### Proof

Let `m` be the number of selected internal edges of B.

Every selected variable vertex contributes all three of its incidences. Counting selected incidences at variable vertices inside B gives

```text
3k = m + a(y).
```

Every clause vertex inside B has exactly one selected incidence. Counting on the clause shore gives

```text
q = m + b(y).
```

Subtracting eliminates the unknown internal-edge count:

```text
3k-q = a(y)-b(y).
```

The congruence follows immediately. QED.

This identity is exact and independent of the internal topology of B.

## 3. Complete arity-three classification

There are only four values `r=0,1,2,3` and three residues `q mod 3`.
The count law restricts `R_B` to the following ambient boundary sets, up to the indicated division into V-side then C-side bits.

```text
r=0:
 q=0: {000,111}
 q=1: {001,010,100}
 q=2: {011,101,110}

r=1:
 q=0: {000,101,110}
 q=1: {001,010,111}
 q=2: {011,100}

r=2:
 q=0: {000,011,101}
 q=1: {001,110}
 q=2: {010,100,111}

r=3:
 q=0: {000,111}
 q=1: {011,101,110}
 q=2: {001,010,100}
```

The actual relation `R_B` may be any subset allowed by the internal block, but no other tuple can occur.

## 4. Delta-matroid dichotomy

Every three-element ambient set in the table consists of three tuples of one parity with every two distinct tuples at Hamming distance exactly two.
Consequently every nonempty subset of such a set is an even delta-matroid: for two distinct feasible tuples, toggling their two differing coordinates moves directly from one to the other.

The two-element ambient sets are pairs of complementary 3-bit tuples at Hamming distance three. For such a class:

- a singleton projected relation is an even delta-matroid / pure pinning relation;
- if both complementary tuples extend, the relation is not a delta-matroid, because the symmetric-exchange axiom cannot move from one feasible tuple toward the other by one or two flips.

Every complementary pair is a bit-twist/permutation of

```text
EQ3 = {000,111}.
```

Therefore:

### Theorem 3CUT-2 — constant exact signature algebra

Every nonempty exact 3-edge-cut boundary relation of the cubic Exact-One carrier is exactly one of:

```text
A. an even delta-matroid relation with at most three tuples;
B. a complementary two-state relation, i.e. twisted EQ3.
```

No larger semantic alphabet is possible at a 3-edge interface.

## 5. Composition consequence

For a decomposition tree whose adhesions have size at most three, an already-solved child can be replaced exactly by a constant-size boundary signature of the two types above.

- Type A can be stored explicitly as at most three tuples and is in the even-delta-matroid edge-CSP tractable language.
- Type B carries exactly one Boolean all-or-none choice and may be stored as one twisted EQ3 atom.
- Witness reconstruction stores one child witness pointer for each feasible boundary tuple, so reconstruction data is constant per child state.

Thus 3-edge interfaces themselves cannot cause exponential state growth.

This is a composition theorem, not a claim that every input admits a decomposition into polynomially solved pieces. A 3-cut-irreducible / cyclically highly connected core remains an open terminal.

## 6. Relation to known barriers

This theorem strictly separates two phenomena already present in JANUS:

```text
ordinary matching-friendly 3-cut state
vs
rank-3 all-or-none state {000,111}.
```

The earlier rank-3 matching barrier is recovered exactly as the exceptional complementary case. The theorem does not contradict it and does not claim that twisted EQ3 is matching-realizable.

## 7. Checker

Executable regression:

`experiments/r5_e9_three_edge_cut_boundary_algebra.py`

It exhausts all 12 `(r,q mod 3)` cases, constructs the count-law ambient relations, verifies the table, verifies pairwise-distance/parity properties, and checks the delta-matroid dichotomy exactly.

## 8. New gate

Freeze:

```text
R5_E9_THREE_CUT_IRREDUCIBLE_GLOBAL_CONTRACTION_GATE_V1
```

Admitted progress:

1. recursively compose genuine nontrivial <=3-edge separations using the constant algebra above;
2. on the residual core, produce a different polynomial contraction or exact terminal;
3. never count trivial vertex-isolating 3-cuts as progress when replacement merely recreates the same local EQ3/EXACT1 atom.

## 9. Ceiling

```text
3-EDGE BOUNDARY COUNT LAW = PROVED
3-CUT SIGNATURE SIZE <= 3 OR COMPLEMENTARY PAIR = PROVED
3-CUT NON-EQ SIGNATURES = EVEN DELTA-MATROIDS
COMPLEMENTARY CASE = TWISTED EQ3
3-CUT INTERFACE STATE EXPLOSION = CLOSED
3-CUT-IRREDUCIBLE CORE = OPEN
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
