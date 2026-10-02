# R5 E8 — Cell-Tree Competitor Barriers and Full Odd-Selector Prefix Theorem

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_THEOREM__EXACT_FROZEN_STRUCTURAL_AIG__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

PR lineage: `#510 / codex/r5-e8-direct-contract-20260921-82493a57`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ODD_PREFIX_KAPPA_ZERO_LEMMA_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_PAYLOAD_BACKBONE_RIGIDITY_2026-09-22_v1.0.json`
- `research/R5_B1B1C5B2B2_E8_RELATED_PAYLOAD_CONE_GAP_SCOPE_REPAIR_2026-09-22_v1.0.md`
- `research/tools/r5_e8_frozen_structural_aig_executor.py`

## 1. Scope

Let

```text
m = 2^r >= 8
n = m/2 = 2^(r-1).
```

Group the frozen block tree into `n` first-level cells

```text
C_q
=
AND(G_{2q-1},G_{2q}),
q=1,...,n.
```

Let `P` be the set of cells whose odd selector `x_{2q-1}` has already been projected.

This theorem concerns an arbitrary odd-selector-only prefix state with

```text
P != all cells.
```

All even selectors remain unresolved.

## 2. Exact cell-tree variant count

For a dyadic subtree interval `I` of the complete cell tree, define

```text
p(I)
=
|P intersect Leaves(I)|.
```

### Lemma 2.1

The frozen state contains exactly

```text
2^{p(I)}
```

distinct reachable structural variants of the root of `I`.

### Proof

At a cell leaf:

- if its odd selector is unresolved, there is one cell root;
- if its odd selector has been projected, the cell has the two roots
  `AND(R^0,G_even)` and `AND(R^1,G_even)`.

They are distinct, nonconstant and noncomplementary by the already-proved odd-selector branch-injectivity argument.

At an internal dyadic node with children `I_L,I_R`, every assignment to projected odd selectors in the left and right intervals occurs in a reachable branch.

By induction the child-root variant counts are

```text
2^{p(I_L)}
and
2^{p(I_R)}.
```

The frozen AND unique table is injective on distinct canonical child-ref pairs, and unresolved even anchors exclude CONST / IDEMPOTENCE / COMPLEMENT collapse.

Commutative canonicalization cannot create a left/right swap collision: the two dyadic child intervals contain disjoint unresolved even-selector ID sets, so a structural root from the left interval cannot equal or be the exact complement of a structural root from the right interval.

Therefore the parent has exactly their Cartesian product:

```text
2^{p(I_L)+p(I_R)}
=
2^{p(I)}.
```

QED.

## 3. Weighted cell path

For cell leaf `q`, define

```text
W_P(q)
=
sum over all cell-tree nodes I
on the path from cell q to the cell-tree root
of
2^{p(I)}.
```

The cell leaf itself is included.

If `q notin P`, its leaf contribution is 1.

If `q in P`, its leaf contribution is 2.

The pre-existing Shannon-OR aggregation region produced by earlier odd projections is common to every unresolved selector and every payload: every branch root still contains every unresolved selector block and every payload still occurs in unresolved even blocks.

Hence that common region cancels from all cone comparisons below.

## 4. Projected-path dominance lemma

### Lemma 4.1

If `P` is a proper subset of the cell leaves, then for every projected cell `p in P` there exists an unprojected cell `u notin P` such that

```text
W_P(u)
<
W_P(p).
```

Moreover, after removing the leaf-cell contribution from both path weights, the corresponding internal-path inequality is non-strict:

```text
W_P^internal(u)
<=
W_P^internal(p).
```

In particular:

```text
min_{u notin P} W_P(u)
<
W_P(p).
```

### Proof sketch by induction on tree height

The root contribution `2^{|P|}` is common to every leaf path.

If the child subtree containing `p` also contains an unprojected leaf, apply induction inside that child.

If that child is fully projected, let its size be `s`. Its child-root contribution alone is `2^s`.

The opposite child contains an unprojected leaf. Along any path to such a leaf, each dyadic subinterval of size `t` contains at most `t-1` projected leaves, so its contribution is at most `2^{t-1}`. The sum over all proper nested dyadic sizes is strictly below `2^s` for `s>=2); the height-one base is immediate.

Thus an unprojected path in the opposite child is strictly cheaper than the fully projected-child path.

Including the leaf contribution preserves strictness because projected leaves contribute 2 and unprojected leaves contribute 1.

QED.

## 5. Adjacent support-union lemma

Let `a,b` be adjacent cyclic cell leaves and suppose at least one of them is projected.

Let `U_P(a,b)` be the number of cell-tree variant nodes in the union of the two root paths, counting all `2^{p(I)}` variants of each distinct dyadic node and counting both cell leaves.

### Lemma 5.1

There exists an unprojected cell `u` such that

```text
U_P(a,b)
>=
W_P(u) + 2.
```

### Proof

Choose whichever one of `a,b` is projected and call it `p`.

By Lemma 4.1, because the weights are integers:

```text
W_P(p)
>=
W_P(u)+1
```

for some unprojected cell `u`.

The union `U_P(a,b)` contains the entire weighted path of `p`.

Because `a` and `b` are distinct cells, the second support cell contributes at least its own distinct reachable cell-root ref, which is not on the leaf-to-root path of `p`.

Therefore:

```text
U_P(a,b)
>=
W_P(p)+1

>=
W_P(u)+2.
```

No comparison of the two internal path geometries is required.

QED.

## 6. Even-selector rigidity

Fix an unresolved even selector `e=2q`.

### Lemma 6.1

Throughout every odd-only prefix:

```text
kappa_e = 0
sigma_e = 8.
```

### Proof

The even selector block `G_e` is never itself projected in this state class.

Its two 3-clauses and block root have the same local selector structure as at step 0.

Across `e=0` and `e=1`, the ten local dependent-gate opportunities from the two copies of the five local selector-dependent gates create exactly two residual two-literal payload-clause nodes.

Those residual nodes cannot have been pre-created by an earlier odd-selector projection. In this cyclic family the duplicate residual identity has two-block shift, e.g. `A_i=B_{i-2}`; when `i` is even the duplicate source index is also even. Odd-only history therefore never projected the duplicate source block. The original 3-clause AIG also contains no payload-payload two-literal residual node.

Hence both residual nodes are genuinely fresh and local saving is exactly 8.

Every cell-tree / branch-tree node above `G_e` rebuilds distinctly in both cofactors:

- prior odd assignment signatures remain present;
- the common even block changes to two distinct residual forms;
- no cofactor root is constant or complementary;
- structural interning cannot merge distinct child-ref pairs.

Hence the upper backbone contributes no further saving.

Every old `e)-independent node remains reachable in at least one cofactor by the same sibling-coverage argument used in the odd-prefix kappa-zero lemma.

Thus:

```text
kappa_e=0
sigma_e=8.
```

QED.

### Theorem 6.2 — even selectors cannot win before the odd prefix is exhausted

Case 1: cell `q` is unprojected.

Then odd sibling `o=2q-1` is unresolved and has exactly the same cell-tree path and the same five below-cell local selector gates.

Therefore:

```text
A_o=A_e.
```

Previously proved:

```text
sigma_o>=8
sigma_e=8.
```

So:

```text
E_o<=E_e.
```

If primary and secondary keys tie, then

```text
o=2q-1 < 2q=e,
```

so the odd selector wins the ID tie-break.

Case 2: cell `q` is projected.

Choose an unresolved odd selector `o` in an unprojected cell minimizing `W_P`.

The five below-cell selector gates are the same for `e` and `o`, while Lemma 4.1 gives

```text
W_P(o)<W_P(q).
```

Hence

```text
A_o<A_e.
```

With `sigma_o>=8=sigma_e`:

```text
E_o<E_e.
```

Thus every unresolved even selector is beaten by some unresolved odd selector.

Therefore:

```text
EVEN_SELECTOR_BARRIER
=
PROVED.
```

## 7. Orphan payload savings cap

A payload `z` is ORPHAN when both of its odd support selectors have already been projected.

Let its two unresolved even support blocks be `e,f`.

For each even occurrence define

```text
c_e,c_f in {1,2}
```

as the number of local frozen 3-clause gates depending on `z`.

### Lemma 7.1

For every orphan payload:

```text
sigma_z
<=
c_e+c_f+8.
```

### Proof

The payload-backbone rigidity theorem already proves that no saving comes from the global Shannon/block-tree backbone.

Each unresolved even support occurrence has the original local budget:

```text
c+2
```

savings, i.e. 3 when `c=1` and 4 when `c=2`.

Each projected odd support block has been replaced on branches by a two-literal residual. For a fixed payload `z`, exactly one of the two selector residuals contains `z); its one dependent OR gate can contribute at most two skipped rebuild opportunities across the two payload cofactors.

There are two projected odd supports.

Therefore:

```text
sigma_z
<=
(c_e+2)
+
(c_f+2)
+
2
+
2

=
c_e+c_f+8.
```

QED.

## 8. Orphan payload cone gap

The two even support blocks of any payload lie in two adjacent cyclic cells.

For an orphan payload, at least one of these two cells is projected:

- for even-index payloads both even-support cells coincide with the two projected odd-support cells;
- for odd-index payloads one even-support cell is paired with one of the projected odd supports.

Therefore Lemma 5.1 applies.

Choose an unresolved odd selector `o` in the unprojected comparison cell supplied by Lemma 5.1.

Below the cell roots:

- unresolved odd selector `o` has exactly five dependent gates: four clause gates plus `G_o`;
- orphan payload `z` has
  - `c_e+1` gates from even support block `e`,
  - `c_f+1` gates from even support block `f`,
  - one canonical two-literal residual gate shared by the two projected odd-support occurrences.

The last count is one, not two: the two residual clauses containing `z` are the same frozen two-literal clause and structural interning merges them.

Thus:

```text
LOCAL_z
=
c_e+c_f+3

LOCAL_o
=
5.
```

The local excess is

```text
c_e+c_f-2.
```

The cell-tree support union exceeds the selected odd cell path by at least 2.

The common Shannon aggregation region cancels.

Hence:

```text
A_z-A_o
>=
(c_e+c_f-2)+2

=
c_e+c_f.
```

Since `c_e,c_f in {1,2}`, this also gives the strict secondary-cone separation

```text
A_z>A_o.
```

## 9. Orphan net-charge barrier

Previously proved:

```text
kappa_z=kappa_o=0
sigma_o>=8.
```

From Lemma 7.1:

```text
sigma_z-sigma_o
<=
(c_e+c_f+8)-8

=
c_e+c_f.
```

From Section 8:

```text
A_z-A_o
>=
c_e+c_f+1.
```

Therefore:

```text
E_z-E_o

=
(A_z-A_o)
-
(sigma_z-sigma_o)

>=
0.
```

If the primary net-charge key ties, the cone bound gives

```text
A_z-A_o
>=
c_e+c_f
>=
2,
```

so the unresolved odd selector wins the secondary cone-size key.

Thus every orphan payload is excluded from the greedy winner set.

Thus:

```text
R5_E8_ORPHAN_PAYLOAD_BARRIER_V1
=
PROVED
for m>=8.
```

No secondary tie-break is required.

## 10. Full competitor closure for m>=8

At any odd-only prefix state with at least one unresolved odd selector, every non-odd competitor belongs to exactly one of:

1. unresolved even selector;
2. RELATED payload;
3. ORPHAN payload.

Already proved:

```text
EVEN SELECTOR
=
beaten by an unresolved odd selector

RELATED PAYLOAD
=
beaten by an unresolved odd support selector

ORPHAN PAYLOAD
=
strictly beaten by an unresolved odd selector.
```

Therefore the frozen greedy winner must be an odd selector.

Induction over the number of projected odd selectors proves:

```text
For every m=2^r>=8,
the first m/2 frozen greedy eliminations
are exactly the m/2 odd selectors
in some order.
```

## 11. m=4 base

The repaired related-payload theorem deliberately excludes `m=4`.

The exact frozen base is separately closed:

```text
m=4:
x1 -> x3
```

before any even selector or payload wins.

Therefore the full theorem extends to every

```text
m=2^r>=4.
```

## 12. Full odd-selector greedy-prefix theorem

```text
R5_E8_ODD_SELECTOR_GREEDY_PREFIX_THEOREM_V1
=
PROVED
```

Statement:

For every `m=2^r>=4`, on the cyclic shared-payload family, the exact frozen structural-only greedy projector selects all `m/2` odd selector variables before any even selector or payload variable.

## 13. Counterfamily consequence

The already-proved odd-selector branch-injectivity lemma gives:

```text
after t odd selector projections:
LIVE_REACHABLE_NODES >= 2^t.
```

Set

```text
t=m/2.
```

Then the exact greedy run satisfies

```text
Peak(F_m)
>=
2^(m/2).
```

The family has `2m` signed 3-clauses and variable identifiers of `O(log m)` bits, hence under ordinary explicit bit encoding:

```text
L
=
Theta(m log m).
```

Therefore:

```text
Peak(F_m)
>=
2^(Omega(L/log L)).
```

This is superpolynomial in the original input length.

Hence:

```text
R5_E8_GREEDY_PROJECTOR_PEAK_THEOREM_V1
=
FALSIFIED
```

for the exact frozen selector.

Equivalently, the current structural-only exact-greedy projector is **not** a D1 polynomial SAT algorithm candidate.

## 14. Diagnostics

Independent frozen-executor checks used only as controls:

- exhaustive odd-prefix states for `m=8`: no counterexample to the even-selector or orphan barriers;
- sampled odd-prefix states for `m=16`: no counterexample;
- the symbolic proof above does not depend on these finite runs.

## 15. Claim ceiling

```text
RELATED_PAYLOAD_BARRIER_m>=8
=
PROVED

ORPHAN_PAYLOAD_BARRIER_m>=8
=
PROVED

EVEN_SELECTOR_BARRIER_m>=8
=
PROVED

m4_ODD_PREFIX_BASE
=
PROVED_DIRECTLY

ODD_SELECTOR_GREEDY_PREFIX_THEOREM
=
PROVED

CYCLIC_POWER_OF_TWO_SUPERPOLY_PEAK_COUNTERFAMILY
=
PROVED FOR THE EXACT FROZEN SELECTOR

GREEDY_PROJECTOR_PEAK_THEOREM
=
FALSIFIED

D1
=
NOT_ADMITTED

P_VS_NP
=
OPEN
```

This result is a scoped lower bound on one exact structural-only projection algorithm. It is not a lower bound for SAT, general AIG quantification, semantic/FRAIG compaction, or arbitrary future E8 mechanisms.
