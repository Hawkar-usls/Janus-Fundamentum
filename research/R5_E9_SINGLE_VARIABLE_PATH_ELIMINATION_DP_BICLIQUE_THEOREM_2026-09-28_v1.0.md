# R5 E9 — Whole Variable-Path Elimination Equals the Davis–Putnam Biclique

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_GLOBAL_MICROGATE_CLASSIFICATION__SINGLE_VARIABLE_PATH_PIVOT_IS_DP__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS CLOSES ALL PIVOTS CONFINED TO ONE ORIGINAL VARIABLE COHERENCE PATH
AS A NEW UNIVERSAL CONTRACTION MECHANISM.
IT DOES NOT RULE OUT GENUINELY GROUPED MULTI-VARIABLE CONTRACTIONS.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_TWO_PATH_XOR_AND_OVERLAY_NORMAL_FORM_2026-09-23_v1.0.md`
- `research/R5_E9_TWO_CLAUSE_ONE_COHERENCE_DP_EXACTNESS_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_single_variable_path_dp_biclique.py`

## 1. Exact variable star

Write an arbitrary CNF around one original variable `x` as

```text
F(x,Y)
=
C(Y)
AND product_i (x OR A_i(Y))
AND product_j (NOT x OR B_j(Y)),
```

where `C` contains no `x`.  The `A_i,B_j` may themselves be clauses of any width.

In the two-path XOR/AND normal form the split occurrence copies of `x` are tied by an XOR2 coherence path, so existentially eliminating the complete path is exactly existentially eliminating this one original `x`.

## 2. Exact projection theorem

### Theorem SVP-1

```text
exists x F(x,Y)
=
C(Y)
AND [ (AND_i A_i(Y)) OR (AND_j B_j(Y)) ].
```

Proof. For `x=0`, every negative-`x` clause is automatically true and every positive-`x` clause requires `A_i`; this is `C AND AND_i A_i`. For `x=1`, the symmetric residual is `C AND AND_j B_j`. Existential quantification is the disjunction of these two residuals. QED.

## 3. DP biclique form

Distributivity gives

```text
(AND_i A_i) OR (AND_j B_j)
=
AND_{i,j} (A_i OR B_j).
```

Thus

```text
boxed(
exists x F
=
C AND product_{i,j}(A_i OR B_j)
).
```

The clauses `(A_i OR B_j)` are exactly all non-tautological Davis–Putnam resolvents between a positive and a negative occurrence of `x` (with ordinary tautology/subsumption simplification allowed afterward).

If one polarity is absent, one branch is `TRUE`, recovering ordinary pure-literal deletion.

## 4. Consequence for the two-path overlay

Splitting occurrences into an XOR2 path does not create a new one-variable contraction algebra. Any exact pivot whose support is contained in one complete original-variable coherence path and its incident clause-product paths projects to precisely the same two-branch / complete-biclique DP object.

Therefore the following are forbidden as claims of new universal progress:

```text
contract one XOR occurrence path;
keep its exact boundary relation;
call the result a new GLOBAL_PIVOT.
```

If flattened to CNF, this is ordinary DP fill-in. If kept as the compact disjunction

```text
(AND A_i) OR (AND B_j),
```

the Boolean choice between the two branches is still exactly the eliminated value of `x`; no live-choice dimension has been destroyed unless an additional nonlocal theorem removes one branch or couples this choice to another contraction.

## 5. Required next scale

A genuinely new `GLOBAL_PIVOT` must therefore operate on at least two original variable paths simultaneously, or on a larger cross-layer structure such as an alternating cycle/block, and prove something stronger than repeated DP:

1. exact SAT preservation;
2. polynomial witness lift;
3. polynomial construction;
4. strict decrease of a polynomially bounded joint potential;
5. no reintroduction of the eliminated Boolean choices as selectors or a DP-resolvent explosion.

This binds the current frontier directly to the already frozen grouped/nonlocal contraction requirement.

## 6. Ceiling

```text
WHOLE ONE-VARIABLE XOR COHERENCE PATH
= EXACTLY ELIMINABLE

EXACT PROJECTION
= TWO-BRANCH RESIDUAL
= COMPLETE DP RESOLVENT BICLIQUE

SINGLE-VARIABLE-PATH PIVOT AS NEW UNIVERSAL MECHANISM
= CLOSED

MINIMUM ADMISSIBLE NEW SCALE
= GENUINELY MULTI-VARIABLE CROSS-LAYER CONTRACTION

UNIVERSAL POLYNOMIAL DECIDER
= OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
