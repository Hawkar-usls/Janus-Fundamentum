# R5 E8 — Odd-selector branch injectivity lemma

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_LEMMA__FROZEN_STRUCTURAL_AIG_ONLY__NO_D1_PROMOTION`

Parent gate:
`research/R5_B1B1C5B2B2_E8_CYCLIC_POWER_OF_TWO_SELECTOR_PREFIX_GATE_2026-09-22_v1.0.json`

## Family

For `m=2^r >= 4`, define

```text
F_m =
AND_i [
  ( x_i OR z_i OR NOT z_{i+1} )
  AND
  ( NOT x_i OR z_{i+2} OR NOT z_{i+3} )
]
```

with payload indices modulo `m`.

Write

```text
A_i = (z_i OR NOT z_{i+1})
B_i = (z_{i+2} OR NOT z_{i+3})

C_i^+ = (x_i OR A_i)
C_i^- = (NOT x_i OR B_i)

G_i = C_i^+ AND C_i^-.
```

Under the frozen clause ordering, `C_i^+` and `C_i^-` are adjacent and the first formula-AND round forms exactly the block `G_i`.

For power-of-two `m`, the block-level AND tree over

```text
G_1,G_2,...,G_m
```

is a complete balanced binary tree.

## Lemma

Let `O` be any subset of the odd selector indices

```text
{1,3,5,...,m-1}.
```

For every assignment `a in {0,1}^O`, let `R_a` be the exact frozen structural restriction of the initial AIG by the selector assignment `a), leaving all even selector variables unresolved.

Then:

1. `R_a` is nonconstant.
2. Every top-level restriction root has complement bit false.
3. If `a != b`, then `R_a != R_b` as exact structural refs.
4. Hence no two `R_a,R_b` are exact complements.
5. Sequential Shannon projection of the variables in `O` under the frozen structural-only rules retains at least `2^|O|` distinct restricted branch-root refs as reachable descendants, unless a payload/even-selector projection is performed first.

Therefore a frozen greedy prefix consisting of `t` distinct odd selector variables yields

```text
LIVE_REACHABLE_NODES >= 2^t.
```

## Proof

### Step 1 — local odd block has two distinct restricted forms

For odd `i`:

```text
x_i = 0  =>  G_i -> A_i
x_i = 1  =>  G_i -> B_i.
```

For `m>=4`, `A_i` and `B_i` are distinct two-literal clause refs under the frozen grammar. Neither is constant.

### Step 2 — each odd block is paired with an unresolved even anchor

At the next block-tree level, the frozen power-of-two tree pairs

```text
(G_1,G_2), (G_3,G_4), ..., (G_{m-1},G_m).
```

Thus every odd selector block `G_{2j-1}` is paired with the still-unresolved even block `G_{2j}`.

After restricting an odd selector, the local pair is therefore exactly one of

```text
AND(A_{2j-1}, G_{2j})
AND(B_{2j-1}, G_{2j}).
```

The fixed anchor `G_{2j}` is a positive AND ref built from two unresolved 3-clause refs. It is neither equal to nor the complement of either two-literal clause ref `A_{2j-1}` or `B_{2j-1}`.

Hence none of the frozen simplifications

```text
CONST
IDEMPOTENCE
COMPLEMENT
```

fires on this pair.

Structural interning is injective on the canonical ordered child pair, so

```text
AND(A_{2j-1},G_{2j})
!=
AND(B_{2j-1},G_{2j}).
```

The local pair therefore preserves the odd assignment bit structurally.

### Step 3 — injectivity lifts through the complete balanced tree

Proceed upward by induction.

At each higher tree level the two children represent disjoint consecutive block intervals. Each interval still contains at least one unresolved even selector block and therefore a syntactic selector-variable occurrence that is absent from the disjoint sibling interval.

Consequently the two child refs cannot be identical. They are positive conjunction roots, so they are not exact complements. No constant/idempotence/complement rewrite removes the parent.

The frozen unique table therefore creates or reuses exactly the node corresponding to the canonical ordered child-ref pair. If one lower child changes because an odd assignment bit changed, the parent pair changes and so does the parent ref.

Inductively, any difference in an odd assignment reaches the root. Hence

```text
a != b  =>  R_a != R_b.
```

The unresolved even blocks also imply the root remains nonconstant.

### Step 4 — sequential projection retains all branch roots

Frozen projection uses

```text
Project(S,x)
=
OR(S[x=0], S[x=1]).
```

For an odd-selector projection prefix, the leaves of the resulting nested Shannon-OR construction are exactly the restricted roots `R_a` for assignments to the projected odd selectors.

By Steps 1–3 these leaves are pairwise distinct, nonconstant, and non-complementary. Therefore the frozen OR construction cannot remove a branch by CONST, IDEMPOTENCE or COMPLEMENT. Structural interning can merge only an already identical structural ref, which pairwise injectivity excludes.

Hence all `2^t` restricted branch-root refs remain reachable.

QED.

## Scope firewall

This lemma does **not** prove that greedy chooses odd selectors.

It proves only:

```text
ODD SELECTOR PREFIX OF LENGTH t
=>
AT LEAST 2^t REACHABLE STRUCTURAL BRANCH ROOTS
```

for the exact frozen representation.

The remaining theorem obligation is scheduler-only:

```text
for m=2^r,
prove frozen greedy selects
all or a linear fraction of odd selectors
before any payload variable.
```

## Finite diagnostic pattern

The frozen selector traces already show:

```text
m=4:
1,3,...

m=8:
1,7,3,5,...

m=16:
1,15,5,9,3,11,7,13,...

m=32:
independent memory-bounded replay matches
odd selectors for the first 16 steps:
1,31,9,17,7,21,15,25,19,3,11,27,5,23,13,29
```

The `m=32` line is diagnostic support only; the symbolic lemma above does not depend on it.

## Claim ceiling

```text
ODD_BRANCH_INJECTIVITY
=
PROVED

ODD_PREFIX_AMPLIFICATION
=
PROVED CONDITIONALLY ON THE SELECTOR PREFIX

ODD_SELECTOR_GREEDY_PREFIX
=
OPEN

ARBITRARY_N_GREEDY LOWER BOUND
=
OPEN

P_VS_NP
=
OPEN
```
