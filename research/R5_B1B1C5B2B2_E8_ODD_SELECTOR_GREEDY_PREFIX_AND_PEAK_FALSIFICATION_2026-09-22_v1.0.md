# R5 E8 — Odd Selector Greedy Prefix Theorem and Frozen-Greedy Peak Falsification

Date: 2026-09-22

Authority: `SCOPED_ARBITRARY_SIZE_THEOREM__EXACT_FROZEN_SELECTOR__NO_P_VS_NP_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_ODD_SELECTOR_BRANCH_INJECTIVITY_LEMMA_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_RELATED_PAYLOAD_CONE_GAP_SCOPE_REPAIR_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_ORPHAN_DYADIC_LOCAL_INEQUALITY_THEOREM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_EVEN_SELECTOR_BARRIER_THEOREM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_NET_PROJECTION_CHARGE_AND_STEP0_THEOREM_2026-09-22_v1.0.md`

## Family

For `m=2^r` define the cyclic signed 3-CNF:

```text
F_m
=
AND_i [
  (x_i OR z_i OR NOT z_{i+1})
  AND
  (NOT x_i OR z_{i+2} OR NOT z_{i+3})
]
```

with payload indices cyclic modulo `m`.

The encoded input length satisfies:

```text
L = Theta(m log m)
```

under the frozen integer-variable encoding.

## Direct base m=4

The arbitrary-r step-zero theorem gives first winner `x1`.

Exact frozen replay of the only remaining odd-selector step gives:

```text
x1 -> x3.
```

Thus the complete odd-selector prefix theorem holds directly for `m=4`.

## Inductive regime m>=8

Assume the frozen run has so far projected only distinct odd selectors and at least one odd selector remains unresolved.

Every remaining non-odd variable belongs to exactly one of three classes:

1. related payload: at least one odd support selector remains unresolved;
2. orphan payload: both odd support selectors are already projected;
3. even selector.

These classes are exhaustive.

### Related payloads

The scope-repaired related-payload cone theorem proves that for `m>=8`, every related payload loses to one of its unresolved odd support selectors under the exact frozen key.

### Orphan payloads

The orphan dyadic-local theorem proves that every orphan payload has an unresolved odd comparator with:

```text
A_z - A_o >= 4.
```

Together with `sigma_z<=12`, `sigma_o>=8`, and `kappa=0`, this excludes every orphan payload from the greedy winner set.

### Even selectors

The even-selector barrier theorem proves that every even selector loses either to its paired unresolved odd selector or to the minimum-weight unresolved odd pair position.

Therefore:

```text
while any odd selector remains unresolved,
the exact frozen greedy winner is an odd selector.
```

By induction the first `m/2` greedy choices are exactly the `m/2` odd selector variables, in some frozen deterministic order.

## Theorem

```text
R5_E8_ODD_SELECTOR_GREEDY_PREFIX_THEOREM_V1
=
PROVED
```

for every:

```text
m=2^r >= 4.
```

Precisely:

```text
the frozen exact structural projector
selects all m/2 odd selector variables
before any payload variable
or even selector variable.
```

## Amplification consequence

The already-proved odd-selector branch-injectivity lemma states that after any prefix of `t` distinct odd selector projections, while the even selector blocks remain unresolved, the live structural state contains at least:

```text
2^t
```

distinct reachable nonconstant noncomplement branch-root refs.

Apply the greedy-prefix theorem at:

```text
t = m/2.
```

Immediately after the last odd selector in the prefix:

```text
Peak(F_m)
>=
2^(m/2).
```

Since:

```text
L = Theta(m log m),
```

we have:

```text
m = Theta(L / log L)
```

up to the standard equivalent asymptotic inversion for this encoding, and therefore:

```text
Peak(F_m)
>=
2^(Omega(L/log L)).
```

This is superpolynomial in the original encoded input length.

## Falsified candidate theorem

The candidate:

```text
R5_E8_GREEDY_PROJECTOR_PEAK_THEOREM_V1

For every signed 3-CNF F of encoded length L,
the frozen MIN_EXACT_PROJECTED_AIG_SIZE run satisfies

max_i |S_i| <= p(L)

for one fixed polynomial p
```

is false.

Therefore:

```text
R5_E8_GREEDY_PROJECTOR_PEAK_THEOREM_V1
=
FALSIFIED_BY_EXPLICIT_ARBITRARY_SIZE_FAMILY.
```

The counterfamily is the frozen cyclic power-of-two family `F_{2^r}`.

## Scientific interpretation

This is a theorem-level negative result about one exact structural-only greedy AIG projector.

It is not:

- a lower bound for all AIG quantifier elimination;
- a lower bound for all variable orders;
- a lower bound for SAT;
- a proof that `P != NP`;
- evidence that semantic projection itself requires exponential size.

Indeed each selector block has a compact semantic existential elimination `A_i OR B_i`; the lower bound is representation/grammar/scheduler specific.

## Consequence for E8

The exact frozen structural greedy route is removed from the live D1 candidate set.

Any successor route must not merely modify the one-step tie heuristic without a new theorem-level reason; AIG quantifier scheduling and semantic compaction are already prior art and are covered by the anti-duplication audit.

## Claim ceiling

```text
ODD_SELECTOR_GREEDY_PREFIX
=
PROVED

POWER_OF_TWO_STRUCTURAL_PEAK_LOWER_BOUND
=
PROVED

FROZEN_GREEDY_POLYNOMIAL_PEAK_CANDIDATE
=
FALSIFIED

D1
=
NOT_ADMITTED

P_VS_NP
=
OPEN
```
