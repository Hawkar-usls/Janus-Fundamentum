# R5 E8 — Even Selector Barrier Theorem

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_THEOREM__FROZEN_POWER_OF_TWO_CYCLIC_FAMILY__NO_D1_PROMOTION`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_PAIR_LEVEL_ORPHAN_CONE_REDUCTION_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ORPHAN_DYADIC_LOCAL_INEQUALITY_THEOREM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.md`

## Statement

For every `m=2^r>=8` odd-selector-only prefix state with at least one unresolved odd selector, no even selector variable can beat all unresolved odd selectors under the exact frozen key.

## Pair-level cone formula

Let pair position `q` contain odd selector `x_{2q-1}` and even selector `x_{2q}`.

For every unresolved selector in pair position `q`, the common Shannon contribution is `C_Shannon`, the selector-local contribution below the pair root is exactly 5, and the pair-tree contribution is `W_P({q})`.

Hence:

```text
A_even(q) = C_Shannon + 5 + W_P({q}).
```

If the paired odd selector is unresolved, the same exact cone formula holds for it:

```text
A_odd(q) = A_even(q).
```

## Even-selector local savings

Under the frozen clause grammar and odd-only history, restricting an unresolved even selector rebuilds the same fixed local selector pattern in both cofactors.

The exact local accounting is:

```text
sigma_even = 8
kappa_even = 0.
```

The already-proved odd-selector local bound is:

```text
sigma_odd >= 8
kappa_odd = 0.
```

## Case A — paired odd selector unresolved

Then:

```text
A_odd = A_even
sigma_odd >= sigma_even.
```

So:

```text
E_odd <= E_even.
```

If primary net charge ties, cone size also ties, but:

```text
odd_id = 2q-1 < 2q = even_id.
```

Thus the paired odd selector wins the frozen tertiary key.

## Case B — paired odd selector already projected

Then pair position `q` belongs to projected set `P`.

The dyadic projected-leaf lemma already proved in the orphan theorem gives:

```text
W_P({q})
>=
min_{u notin P} W_P({u}) + 1.
```

Choose unresolved odd selector `o` at pair position `u` attaining the minimum.

Then:

```text
A_even(q) >= A_o + 1.
```

Also:

```text
sigma_even = 8
sigma_o >= 8.
```

Therefore:

```text
E_even - E_o
=
(A_even-A_o) - (sigma_even-sigma_o)
>=
1.
```

So the unresolved odd selector strictly beats the even selector on the primary net-charge key.

## Theorem

```text
R5_E8_EVEN_SELECTOR_BARRIER_V1
=
PROVED
```

for every `m=2^r>=8` odd-selector-only prefix state with an unresolved odd selector.

For `m=4`, the exact direct base `x1 -> x3` already closes the complete odd prefix.

## Consequence

Before the odd-selector prefix completes:

- related payloads are excluded;
- orphan payloads are excluded;
- even selectors are excluded.

Therefore every remaining competitor class is closed except unresolved odd selectors themselves.

## Claim ceiling

```text
EVEN_SELECTOR_BARRIER
=
PROVED

ALL_NON_ODD_COMPETITORS
=
CLOSED

ODD_SELECTOR_GREEDY_PREFIX
=
READY_TO_SEAL

P_VS_NP
=
OPEN
```
