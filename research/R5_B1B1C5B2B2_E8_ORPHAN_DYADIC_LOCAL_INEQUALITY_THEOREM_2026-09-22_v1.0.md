# R5 E8 — Orphan Dyadic-Local Inequality Theorem

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_THEOREM__FROZEN_POWER_OF_TWO_CYCLIC_FAMILY__NO_D1_PROMOTION`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_PAIR_LEVEL_ORPHAN_CONE_REDUCTION_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ORPHAN_PAYLOAD_SAVINGS_CAP_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`

## Setup

Let `m=2^r>=8` and `n=m/2>=4` be the number of adjacent odd/even selector-pair positions.

Let `P` be the set of pair positions whose odd selector has already been projected; assume at least one odd selector remains unresolved, so `P` is a proper subset of the `n` pair leaves.

For every dyadic interval `I` in the complete pair tree define:

```text
w_P(I) = 2^{|P intersect I|}.
```

For pair-position set `T`:

```text
W_P(T)
=
sum of w_P(I)
over all dyadic intervals I intersecting T,
including size-1 leaf intervals.
```

The pair-level reduction lemma already proved:

```text
min unresolved odd cone
=
C_Shannon + 5 + min_{q notin P} W_P({q}),

and for orphan payload z:

A_z
>=
C_Shannon + L_z + W_P(E_z).
```

Thus it suffices to prove:

```text
L_z + W_P(E_z)
>=
min_{q notin P} W_P({q}) + 9.
```

## Lemma A — projected leaf path dominates an unresolved minimum

For any projected pair leaf `p in P`:

```text
W_P({p})
>=
min_{q notin P} W_P({q}) + 1.
```

Proof sketch:

Follow the dyadic path from `p` upward until the first interval whose sibling side contains an unresolved leaf. Below that split, the child containing `p` is fully projected. A fully projected subtree path has strictly larger local weight than a minimum path through a same-size subtree containing an unresolved leaf; already at the terminal leaf the projected contribution is 2 versus 1. All common ancestors above the split cancel. Hence the gap is at least 1.

## Lemma B — projected leaf with projected sibling

If projected leaf `p` has its size-1 sibling also projected, then:

```text
W_P({p})
>=
min_{q notin P} W_P({q}) + 3.
```

At the bottom pair of leaves, the projected path contributes:

```text
leaf weight 2
+ size-2 interval weight 4
= 6.
```

Any unresolved path through a size-2 interval contributes at most:

```text
leaf weight 1
+ size-2 interval weight 2
= 3.
```

If the global minimum unresolved leaf lies outside this size-2 interval, descend to the first dyadic split separating the fully projected child containing `p` from a child containing an unresolved leaf. The fully projected child path exceeds the unresolved-side minimum by at least the same 3; common ancestors cancel. QED.

## Lemma C — two consecutive projected leaves

Let `a,b` be two cyclic-consecutive pair leaves and suppose both are projected.

Then:

```text
W_P({a,b})
>=
min_{q notin P} W_P({q}) + 5.
```

Proof:

### C1. a,b are a size-2 sibling pair

By Lemma B:

```text
W_P({a}) >= minW + 3.
```

The union `W_P({a,b})` adds the distinct projected leaf `b` with weight 2; every larger dyadic interval on the two paths is already shared.

Therefore:

```text
W_P({a,b}) >= minW + 5.
```

### C2. a,b are not siblings

By Lemma A:

```text
W_P({a}) >= minW + 1.
```

The portion of the `b` path not already on the `a` path contains:

- the projected leaf `b`, weight 2;
- at least one proper dyadic ancestor below `LCA(a,b)`, containing `b` and therefore having weight at least 2.

Thus `b` contributes at least 4 new weight to the union, giving:

```text
W_P({a,b}) >= minW + 5.
```

The cyclic wrap pair `{n-1,0}` belongs to C2 for `n>=4`, so wrap is included.

## Orphan support geometry

For any payload there are only two pair-level support patterns.

### Type A — aligned two-pair support

The two odd support selectors and the two even support blocks occupy the same two cyclic-consecutive pair positions.

For an orphan payload both pair positions are projected.

Hence by Lemma C:

```text
W_P(E_z) >= minW + 5.
```

The pair-level reduction already gives:

```text
L_z >= 5.
```

Therefore:

```text
L_z + W_P(E_z)
>=
minW + 10
>
minW + 9.
```

Type A is closed.

### Type B — staggered three-pair support

The two projected odd support pair positions are two consecutive leaves `p,q`.

The two unresolved-even support pair positions are `e,p`, where `e,p,q` are three cyclic-consecutive pair positions.

Thus `E_z={e,p}`, with `p in P`; the O-only projected support is `q in P`.

#### B1. e is also projected

Then `e,p` are two cyclic-consecutive projected leaves.

Lemma C yields:

```text
W_P(E_z) >= minW + 5.
```

Together with `L_z>=5`, the target follows immediately.

#### B2. e is unresolved

Use the unresolved odd selector in pair position `e` as the comparator.

The union `W_P({e,p})` contains the full `e` path plus the portion of projected `p`'s path not shared with `e`.

If `e,p` are not siblings, that unique portion contains the projected leaf (weight 2) and at least one proper projected-containing interval (weight at least 2), so:

```text
W_P(E_z) - W_P({e}) >= 4.
```

In this subcase the generic local floor `L_z>=5` already gives the target.

If `e,p` are siblings, the unique tree contribution is exactly at least the projected leaf weight:

```text
W_P(E_z) - W_P({e}) >= 2.
```

Now use the staggered local geometry.

The two unresolved even support blocks contribute at least four z-dependent nodes below pair roots.

The two projected odd supports share at most one structurally identical z-containing residual two-literal clause; at least one such residual node is live, giving one more node.

The O-only projected support pair `q` is not in `E_z`; the branch in which its residual contains z contributes a z-dependent pair-root instance outside `W_P(E_z)`, giving one more node.

Because `e,p` are siblings and `q` is the next cyclic pair position, `q` cannot lie in the same size-2 dyadic interval. Before the q-path joins the `E_z` union it therefore contributes at least one additional z-dependent upper interval instance outside `W_P(E_z)`.

Hence:

```text
L_z >= 4 + 1 + 1 + 1 = 7.
```

Therefore:

```text
L_z + W_P(E_z)
>=
7 + W_P({e}) + 2
=
W_P({e}) + 9
>=
minW + 9.
```

Type B is closed.

## Main theorem

For every `m=2^r>=8`, every odd-selector-only prefix state with at least one unresolved odd selector, and every orphan payload `z`:

```text
L_z + W_P(E_z)
>=
min_{q notin P} W_P({q}) + 9.
```

Therefore there exists an unresolved odd selector `o` such that:

```text
A_z - A_o >= 4.
```

This proves:

```text
R5_E8_ORPHAN_PAYLOAD_CONE_GAP_V1
=
PROVED.
```

## Scheduler consequence

Previously proved:

```text
sigma_z <= 12
kappa_z = 0

sigma_o >= 8
kappa_o = 0.
```

Hence:

```text
E_z-E_o
>=
(A_z-A_o) - (12-8)
>=
0.
```

If primary net charge ties, `A_z-A_o>=4`, so `A_o<A_z` and the odd selector wins the secondary cone key.

Thus:

```text
ORPHAN_PAYLOAD_BARRIER
=
CLOSED
```

for all `m=2^r>=8`.

Together with the repaired related-payload theorem, every payload class is excluded while an odd selector remains unresolved.

For `m=4`, the full odd prefix `x1 -> x3` is already proved directly.

## Claim ceiling

```text
ORPHAN_DYADIC_LOCAL_INEQUALITY
=
PROVED

ORPHAN_PAYLOAD_CONE_GAP
=
PROVED

ORPHAN_PAYLOAD_BARRIER
=
CLOSED

ODD_SELECTOR_GREEDY_PREFIX
=
READY_TO_SEAL

P_VS_NP
=
OPEN
```
