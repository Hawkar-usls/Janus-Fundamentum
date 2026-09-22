# R5 E8 — Orphan Payload Savings Cap

Date: 2026-09-22

Authority: `SCOPED_SYMBOLIC_LEMMA__FROZEN_POWER_OF_TWO_CYCLIC_FAMILY__NO_D1_PROMOTION`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_PAYLOAD_BACKBONE_RIGIDITY_2026-09-22_v1.0.json`
- `research/R5_B1B1C5B2B2_E8_ODD_PREFIX_KAPPA_ZERO_LEMMA_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_RELATED_PAYLOAD_CONE_GAP_SCOPE_REPAIR_2026-09-22_v1.0.md`

## Definition

An orphan payload `z` is one whose two odd support selectors have both already been projected; its two even support blocks remain unresolved.

## Generic savings budget

Previously proved:

```text
sigma_z <= s_z + 12.
```

For one original payload occurrence, the local maximum savings budget is 4 when `c_i=2` and 3 when `c_i=1`.

Once an odd support selector has been projected, that occurrence is represented branch-locally by one residual two-literal payload clause `A_p` or `B_p`. A fixed payload occurs in at most one of them. Across `z=0,1`, that residual can contribute at most 2 units of structural saving.

For the two odd support occurrences, `c_o=c_p`.

### Case c_o=c_p=2

The two original odd-occurrence budgets total 8 and become at most 4 after both supports are projected. Thus:

```text
sigma_z <= s_z + 8 <= 12.
```

### Case c_o=c_p=1

The two original odd-occurrence budgets total 6 and become at most 4. Thus:

```text
sigma_z <= s_z + 10 <= 12.
```

## Theorem

```text
R5_E8_ORPHAN_PAYLOAD_SAVINGS_CAP_V1

For every power-of-two cyclic odd-only prefix state
and every orphan payload z:

sigma_z <= 12.
```

Together with the already-proved `kappa_z=0`:

```text
E_z = A_z - sigma_z >= A_z - 12.
```

For every unresolved odd selector `o`, the existing selector-side local analysis gives `sigma_o>=8`, and `kappa_o=0`, so:

```text
E_o = A_o - sigma_o <= A_o - 8.
```

Therefore the orphan barrier is reduced to a pure cone-gap statement.

## Reduced orphan barrier

It is sufficient to prove:

```text
R5_E8_ORPHAN_PAYLOAD_CONE_GAP_V1

For every orphan payload z,
while some odd selector remains unresolved,
there exists an unresolved odd selector o such that

A_z - A_o >= 4.
```

Then:

```text
E_z - E_o
>= (A_z-12) - (A_o-8)
= (A_z-A_o)-4
>= 0.
```

If primary net charge ties, `A_o<A_z`, so the odd selector wins the secondary frozen key.

## Finite controls

Exact executor diagnostics are consistent with the theorem: exhaustive odd-only orders for `m=8` and verified `m=16` odd-prefix states show orphan `sigma_z` only in `{10,12}`. These runs are controls only.

## Claim ceiling

```text
ORPHAN_PAYLOAD_SAVINGS_CAP
=
PROVED

ORPHAN_PAYLOAD_CONE_GAP_4
=
OPEN

ORPHAN_PAYLOAD_BARRIER
=
OPEN

RELATED_PAYLOADS
=
CLOSED

ODD_SELECTOR_GREEDY_PREFIX
=
OPEN

P_VS_NP
=
OPEN
```
