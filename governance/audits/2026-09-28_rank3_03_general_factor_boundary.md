# Source audit — rank-3 `{0,3}` coupling vs. the 2026 subcubic general-factor dichotomy

Date: 2026-09-28

Scope:
- `research/R5_E9_ROW_BASIS_RANK3_MATCHING_ROUTER_2026-09-28_v1.0.md`
- `research/R5_E9_EQ3_MID_NULLITY_HARDNESS_SLAB_2026-09-28_v1.0.md`
- `research/R5_E9_ROW_BASIS_RANK3_HYPERMATCHING_QUOTIENT_2026-09-28_v1.0.md`

Decision:
`PASS_EXTERNAL_BOUNDARY_IDENTIFIED__LOCAL_MATCHING_SHORTCUT_NOT_A_NEW_ROUTE__GLOBAL_03_COUPLING_REMAINS_OPEN__NO_D1_PROMOTION`

## 1. Exact translation to General Factor

Take the clause-variable incidence graph of Positive Exact-One / Positive 1-in-3 SAT.
Select an incidence edge precisely when the corresponding variable is true at that occurrence.

For every clause vertex of degree three, Exact-One is the degree constraint

```text
D_clause = {1}.
```

For every variable that survives as a rank-three / multiplicity-three atom, the three incidences must be selected all together or not at all.  Its exact all-or-none degree constraint is

```text
D_rank3 = {0,3}.
```

Thus the surviving JANUS rank-three coupling is exactly a subcubic General Factor instance using the mixed constraint family

```text
{{1}, {0,3}}
```

(up to already-polynomial singleton/pair material that the row-basis router absorbs by graph matching).

## 2. Fresh external boundary

Shao and Zivny, *Real-weighted general factors on subcubic graphs*, Mathematical Programming, published 14 September 2026, DOI `10.1007/s10107-026-02416-3`, prove a complexity dichotomy for real-weighted General Factor on subcubic graphs.

Their Theorem 1.2 states that the problem is strongly polynomial when the arity-three constraint `{0,3}` is absent, or when every local degree constraint is all-or-none in the sense `D subseteq {0,k}`; otherwise the problem is NP-hard.

For the JANUS mixed family:

```text
{0,3} is present,
{1} is not a subset of {0,3} at arity three.
```

Therefore the exact local constraint family exposed by the JANUS row-basis quotient lands on the NP-hard side of the published subcubic dichotomy.

This is not used as a new hardness proof for the JANUS carrier; JANUS already has its own exact Karp reduction.  It is an independent external collision confirming that the rank-three all-or-none coupling is the correct hard boundary rather than an artifact of the current representation.

## 3. Matching-gadget interpretation

The same paper characterizes matching-realizable degree constraints in its tractable gap-length-at-most-one regime and shows that genuinely non-matching-realizable local behavior already appears at arity three.  More importantly for this audit, their subcubic dichotomy singles out `{0,3}` itself as the exceptional hard constraint in the mixed case.

Hence a uniform polynomial replacement of every `{0,3}` atom by ordinary matching gadgets while preserving the surrounding `{1}` clause constraints would yield a polynomial algorithm for a problem on the NP-hard side of Theorem 1.2.  Such a replacement therefore cannot be treated as a routine representation lemma: establishing it would already imply `P=NP` when composed with the existing exact JANUS reduction.

No assumption `P!=NP` is made here, and no impossibility theorem stronger than the published dichotomy is claimed.

## 4. JANUS internal sharpening

For an actual-row rational basis, let

```text
p = number of multiplicity-1 columns,
s = number of multiplicity-2 columns,
h = number of multiplicity-3 columns,
k = rational nullity.
```

Exact incidence counting gives

```text
3k = 2p+s,
delta = s+2h,
h-p = n-3k.
```

The frozen EQ3 image satisfies

```text
n/10 <= k <= n/6.
```

Therefore every actual-row rational basis of every instance in that exact hard image obeys

```text
h >= n-3k >= n/2.
```

So basis re-selection cannot make the `{0,3}` population logarithmic on this slab.  The rank-three hard atoms remain at linear density for every actual-row basis.

This closes the candidate escape

```text
CHOOSE A CLEVER ACTUAL-ROW BASIS
-> h=O(log n)
-> ENUMERATE RANK3 ATOMS
-> MATCH THE REST
```

on the exact EQ3 hardness slab.

## 5. Surviving global obligation

The legitimate residual is now narrower than the former generic middle-nullity band:

```text
GLOBAL EXACT SOLUTION OF A LINEAR-DENSITY {0,3} COUPLING LAYER
INTERACTING WITH {1} EXACT-ONE CLAUSE CONSTRAINTS,
WITH POLYNOMIAL CONSTRUCTION + SOLVE + RECONSTRUCTION + VERIFICATION.
```

Equivalently in the current row-basis language:

```text
R5_E9_ROW_BASIS_RANK3_GLOBAL_COUPLING_GATE_V1
```

may be sharpened semantically to

```text
R5_E9_LINEAR_DENSITY_03_GENERAL_FACTOR_GLOBAL_QUOTIENT_GATE_V1.
```

A PASS must not:

```text
- branch over the linearly many rank-three atoms;
- re-expand multiplicity-two material already solved by matching;
- claim that another actual-row basis makes h logarithmic on the frozen hard slab;
- replace `{0,3}` by independent pair choices that lose all-or-none semantics;
- count a polynomial verifier as a polynomial constructor/solver.
```

A genuine PASS must provide an exact deterministic polynomial algorithm or exact polynomial representation change for the mixed `{1},{0,3}` global coupling, with witness reconstruction and direct verification charged in the total runtime.

## 6. Scientific ceiling

```text
ROW-BASIS N1/N2/N3 QUOTIENT
= PROVED INTERNALLY

N1/N2 RESIDUAL AFTER FIXING N3
= POLYNOMIAL MATCHING

DEDICATED 2^h ROUTER
= PROVED INTERNALLY

FROZEN EQ3 HARD SLAB
= NP-COMPLETE INTERNALLY

h >= n/2 ON THAT SLAB FOR EVERY ACTUAL-ROW BASIS
= DERIVED EXACTLY

SURVIVING RANK3 ATOM
= EXACTLY GENERAL-FACTOR D={0,3}

EXTERNAL SUBCUBIC DICHOTOMY
= COLLISION CONFIRMED (SHAO-ZIVNY 2026)

GLOBAL POLYNOMIAL ABSORPTION OF LINEAR-DENSITY {0,3} ATOMS
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
