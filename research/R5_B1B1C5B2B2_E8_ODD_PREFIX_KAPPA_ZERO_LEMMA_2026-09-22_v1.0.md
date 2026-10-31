# R5 E8 — Odd-Prefix Kappa-Zero Lemma

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_LEMMA__FROZEN_POWER_OF_TWO_CYCLIC_FAMILY__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authority:

- `research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`
- `research/tools/r5_e8_frozen_structural_aig_executor.py`

## Statement

Let

```text
m = 2^r >= 4
```

and let `S_O` be any frozen structural-AIG state obtained from the cyclic shared-payload family by projecting an arbitrary sequence `O` of distinct odd selector variables only.

Assume, as in this gate, that all even selector variables remain unresolved.

For every currently unresolved:

1. odd selector `x_o`, and
2. payload variable `z_j`,

the exact net-projection accounting quantity

```text
kappa_v
=
# old v-independent reachable nodes
that disappear after the complete trial projection
```

satisfies

```text
kappa_v = 0.
```

Therefore throughout every odd-only prefix state the exact greedy primary comparison reduces to

```text
E_v
=
A_v - sigma_v.
```

## Structural setup

Each original selector block is

```text
G_i
=
(x_i OR A_i)
AND
(NOT x_i OR B_i)
```

with

```text
A_i = (z_i OR NOT z_{i+1})
B_i = (z_{i+2} OR NOT z_{i+3}).
```

For every odd block `G_{2q-1}`, the complete power-of-two block tree pairs it first with the unresolved even block `G_{2q}`.

After projecting a subset of odd selectors, each branch root corresponds to one assignment to the projected odd selectors. In the local odd/even pair, a projected odd block is represented by either

```text
AND(A_{2q-1}, G_{2q})
```

or

```text
AND(B_{2q-1}, G_{2q}).
```

The previous odd-selector branch-injectivity lemma proves that these assignment signatures remain structurally distinct, nonconstant and noncomplementary before any payload projection.

## Part I — remaining odd-selector trial

Fix an unresolved odd selector `x_o`.

### I.1 Every Shannon-backbone node depends on x_o

Every branch root still contains the unchanged unresolved block `G_o`, hence structurally depends on `x_o`.

Every frozen Shannon-OR backbone node combines branch subgraphs that each still depend on `x_o`.

Thus no Shannon-backbone node is counted as `x_o`-independent.

### I.2 Old independent nodes inside the local block are covered by the two cofactors

The two restrictions give

```text
x_o=0  =>  G_o -> A_o
x_o=1  =>  G_o -> B_o.
```

All old AND gates of the two original 3-clauses and the block gate `G_o` depend on `x_o`, so they are not candidates for `kappa`.

The old independent payload-variable refs occurring in `A_o` or `B_o` remain reachable in at least one of the two cofactors.

### I.3 Independent siblings above G_o survive

At the first block-tree parent, the sibling is the unresolved even anchor paired with `G_o`.

Neither `A_o` nor `B_o` is constant, equal to that even anchor, or its exact complement. Hence neither cofactor collapses away the independent sibling.

At each higher complete-tree level, the sibling interval contains unresolved selector structure. The changed child and the sibling are distinct nonconstant noncomplement refs, so CONST / IDEMPOTENCE / COMPLEMENT do not remove the sibling.

Induction lifts this retention to the branch root.

### I.4 Final Shannon OR retains both cofactors

The two complete cofactor roots differ at the local `A_o` versus `B_o` choice under the same unresolved even anchor. The odd-prefix branch-injectivity argument lifts this difference through every branch and the Shannon backbone.

Therefore the two cofactor roots are distinct and noncomplementary; the final frozen OR retains both reachable sets.

Hence every old `x_o`-independent reachable node remains reachable from the projected root:

```text
kappa_{x_o}=0.
```

## Part II — payload trial

Fix payload variable `z_j`.

### II.1 Persistent unresolved-even support

In the cyclic family `z_j` occurs in the four selector blocks

```text
G_j,
G_{j-1},
G_{j-2},
G_{j-3}
```

modulo `m`.

Among four consecutive indices exactly two are even.

Since the prefix projects odd selectors only, those two even blocks remain unresolved in every branch.

Therefore every branch root still structurally depends on `z_j`, and consequently every Shannon-backbone node also depends on `z_j`.

No Shannon-backbone node is therefore a candidate for `kappa_{z_j}`.

### II.2 Payload restriction preserves prior odd assignment signatures

Fix any previously projected odd selector `x_i`.

Its two local branch alternatives before the payload trial are

```text
AND(A_i,G_{i+1})
```

and

```text
AND(B_i,G_{i+1})
```

after choosing the appropriate paired even block notation.

The payload-variable sets of `A_i` and `B_i` are disjoint:

```text
Vars(A_i)
=
{z_i,z_{i+1}}

Vars(B_i)
=
{z_{i+2},z_{i+3}}.
```

Hence a single payload variable `z_j` can affect at most one of `A_i,B_i`.

Under a Boolean restriction:

- an affected two-literal payload clause becomes either TRUE or a single payload literal;
- the unaffected alternative remains a nonconstant two-literal clause;
- the paired even block remains nonconstant because at most one of its two selector clauses contains `z_j`, while the other still contains its unresolved even selector.

Thus the two local refs corresponding to the old odd assignment bit cannot become identical or exact complements after either `z_j=0` or `z_j=1`.

Therefore every prior odd branch signature remains structurally visible in each payload cofactor.

This preserves injectivity through the complete block tree and then through the pre-existing Shannon backbone.

### II.3 Coverage of old payload-independent local nodes

Outside the four support blocks, restriction leaves every old node unchanged and reachable.

Inside an affected unresolved selector block, `z_j` occurs in at most one of the two selector clauses.

For the affected 3-clause:

- one cofactor may satisfy the payload literal and make that clause TRUE;
- the other cofactor removes the false payload literal and retains the remaining selector/payload subclause.

Every old node in that clause that is independent of `z_j` is therefore retained in at least one cofactor.

The other selector clause of the block is unaffected and remains reachable.

The block gate itself depends on `z_j` and is not a `kappa)-candidate.

Inside a previously projected odd block represented by `A_i` or `B_i`:

- if the chosen clause does not contain `z_j`, it is unchanged in both cofactors;
- if it contains `z_j`, its OR gate depends on `z_j`, while its other payload literal is retained in the falsifying cofactor.

Thus every old `z_j`-independent local node is covered by the union of the two cofactor reachable sets.

### II.4 Independent siblings on upper paths are retained

Every changed local block remains non-FALSE in both cofactors: it is either a surviving unresolved-selector block, a nonconstant reduced clause, a literal, or a conjunction containing the unresolved even anchor.

Therefore an upper AND parent never loses an independent sibling through a FALSE collapse.

The preserved branch signatures also exclude exact idempotence/complement collapse on the relevant upper pairs.

By induction all old independent siblings remain reachable in at least one cofactor.

### II.5 Final OR does not discard a cofactor

The two payload cofactors differ structurally inside at least one of the two unresolved even support blocks.

Each cofactor retains unresolved-even structure and all previously projected odd assignment signatures.

Hence the complete cofactor roots are nonconstant, structurally distinct, and noncomplementary under the frozen rules.

The final OR therefore retains both cofactor reachable sets.

Combining II.3-II.5:

```text
kappa_{z_j}=0.
```

## Consequence

For every relevant comparator throughout an odd-only prefix:

```text
cost(v)
=
N + A_v - sigma_v.
```

Since `N` is common to all trials in the same state, the exact frozen selector key reduces to

```text
(
  A_v - sigma_v,
  A_v,
  variable_id
).
```

The remaining scheduler theorem no longer contains `kappa`.

## Remaining open theorem

It is now sufficient to prove:

```text
R5_E8_ODD_PREFIX_CONE_SAVING_DOMINATION_THEOREM_V1
```

For every `m=2^r` odd-only prefix state before all odd selectors are eliminated, there exists an unresolved odd selector `o` such that for every payload `z`:

```text
A_z - A_o
>=
sigma_z - sigma_o.
```

If equality holds:

```text
A_o < A_z.
```

Then every frozen greedy choice throughout the first `m/2` relevant steps is an odd selector.

## Finite exact controls

The frozen executor gives `kappa_v=0` for every unresolved trial candidate throughout the complete verified odd prefixes for:

```text
m=4
m=8
m=16.
```

The `m=32` diagnostic odd prefix is also consistent with the lemma.

These runs are controls only; the proof above is the scoped authority.

## Claim ceiling

```text
ODD_PREFIX_KAPPA_ZERO
=
PROVED

NET_CHARGE
=
A - sigma
ON THIS PREFIX REGIME

CONE_SAVING_DOMINATION
=
OPEN

ODD_SELECTOR_GREEDY_PREFIX
=
OPEN

ARBITRARY_N_GREEDY_LOWER_BOUND
=
OPEN

P_VS_NP
=
OPEN
```
