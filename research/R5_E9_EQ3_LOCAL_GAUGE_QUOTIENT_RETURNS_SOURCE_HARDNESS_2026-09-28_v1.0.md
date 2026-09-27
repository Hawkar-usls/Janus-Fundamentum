# R5 E9 — EQ3 local gauge quotient returns source hardness

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_ANTI_LOOP_THEOREM__LOCAL_GAUGE_QUOTIENT_NOT_PROGRESS`

Parents:
- `R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `R5_E9_EQ3_REGULARIZER_LINEAR_GF2_NULLITY_UNSAT_FAMILY_2026-09-27_v1.0.md`

Scientific ceiling:

```text
THIS IS AN EXACT SEMANTIC QUOTIENT THEOREM.
IT DOES NOT GIVE A POLYNOMIAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. The regularizer gadget

Use terminals `t0,t1,t2` and auxiliaries `a3,...,a9`, with the nine Positive-1-in-3 rows

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6)
```

The already-sealed regularization theorem proves that the Boolean projection of the exact satisfying relation to `(t0,t1,t2)` is exactly

```text
EQ3 = {000,111}.
```

Moreover the three exact gadget witnesses are

```text
1110000001,
0001110000,
0000001110,
```

so terminal value `111` has one internal extension and terminal value `000` has two.

## 2. Exact semantic elimination of the auxiliaries

Let `Phi` be any cubic Positive-1-in-3 instance.  Let `R(Phi)` be the linear-cubic regularized instance obtained by splitting each source variable `x` into three occurrence terminals `x_0,x_1,x_2`, retaining every old clause on occurrence copies, and attaching one disjoint copy of the gadget to each triple `(x_0,x_1,x_2)`.

Existentially eliminate all gadget auxiliaries from `R(Phi)`.

Because gadgets are disjoint outside their terminals, existential elimination factors gadget-by-gadget.  By the exact terminal projection above, each eliminated gadget is replaced by precisely

```text
EQ3(x_0,x_1,x_2).
```

Therefore the quotient relation is exactly

```text
Q(Phi)
=
(old source clauses on occurrence copies)
AND
AND_x EQ3(x_0,x_1,x_2).
```

No approximation or counting argument is used.

## 3. Collapse recovers the source instance

Define the collapse map

```text
kappa : Q(Phi) assignments -> Phi assignments
kappa(x) = common value of x_0,x_1,x_2.
```

`EQ3` makes this well-defined.

Conversely every source assignment `sigma` lifts uniquely on the occurrence terminals by assigning all three copies of each source variable the value `sigma(x)`.

Every retained source clause sees exactly the same three truth values before and after collapse. Hence

```text
Phi SAT
iff
Q(Phi) SAT.
```

Witness conversion in both directions is linear-time.

Thus, up to occurrence splitting plus equality identification, `Q(Phi)` is the original source semantics.

## 4. The local F2 gauge really exists, but quotienting it is not algorithmic progress

Over `F2`, the 9x10 gadget incidence matrix has rank 7 and kernel dimension 3.  The zero-terminal kernel contains the nonzero internal mode

```text
g = (0,0,0,1,1,1,1,1,1,0).
```

Direct substitution gives `A_gadget g = 0 mod 2`.

The zero-terminal kernel is one-dimensional; quotienting this local gauge removes one spurious parity degree of freedom per gadget.

However, exact semantic elimination of the corresponding internal choices leaves `EQ3`, and collapsing `EQ3` recovers arbitrary cubic Positive-1-in-3 SAT.  Therefore the local gauge degrees are representation redundancy, not the source of NP-complete global semantics.

## 5. Theorem

### EQ3_LOCAL_GAUGE_QUOTIENT_RETURNS_SOURCE_HARDNESS

For every cubic Positive-1-in-3 instance `Phi`, the exact regularized linear-cubic instance `R(Phi)` satisfies

```text
exists gadget auxiliaries R(Phi)
=
Q(Phi),
```

where `Q(Phi)` is occurrence-split `Phi` plus one `EQ3` constraint per source variable; and `Q(Phi)` collapses to `Phi` with exact satisfiability and polynomial witness preservation.

Consequently any proposed universal progress measure whose only decrease on the regularized family is deletion/factorization of gadget-internal gauge modes does not reduce the semantic problem: after the quotient it returns an arbitrary NP-complete source instance.

This is an anti-loop theorem, not a lower bound against other global quotients.

## 6. Algorithmic consequence

Forbidden as standalone universal progress:

```text
large raw kernel
-> identify local zero-boundary modes
-> quotient all such modes
-> declare residual easy
```

The first two arrows are valid on the regularized family; the third is false without an additional global theorem.

Any successful quotient route must also compress the surviving `EQ3 + source Exact-One` interaction, not merely remove internal extension multiplicity.

## 7. Checker

Executable regression:

`experiments/r5_e9_eq3_local_gauge_quotient.py`

It verifies exactly:
- exact Boolean terminal projection `{000,111}`;
- the three gadget witnesses;
- F2 rank 7 / nullity 3;
- zero-terminal kernel dimension 1;
- the explicit internal gauge mode;
- a small source-instance truth-table comparison between source semantics and the projected/collapsed quotient.

## 8. Ceiling

```text
LOCAL INTERNAL GAUGE MODE = PROVED
EXACT AUXILIARY ELIMINATION = EQ3
EQ3 COLLAPSE = ORIGINAL SOURCE SEMANTICS
LOCAL GAUGE QUOTIENT AS UNIVERSAL PROGRESS = CLOSED
GLOBAL SEMANTIC COMPRESSION = OPEN
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
