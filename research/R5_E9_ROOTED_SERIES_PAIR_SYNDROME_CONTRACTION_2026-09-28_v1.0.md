# R5 E9 — Rooted Series-Pair Syndrome Contraction

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_WEIGHTED_ROOTED_CIRCUIT_CONTRACTION__SAT12_COLLAPSES_TO_AG32__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_SINGLE_ODD_ROOTED_DUAL_FANO_POLY_TERMINAL_2026-09-28_v1.0.md`
- `research/R5_E9_ROOTED_DUAL_FANO_E10_CROSS_ROUTE_RECONCILIATION_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_rooted_series_pair_syndrome_contraction.py`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT ADDS AN EXACT SERIES-CONTRACTION PREPROCESSOR FOR THE ROOTED
MINIMUM-CIRCUIT OBJECTIVE AND REMOVES SAT_12_3 AS A GENUINE
ASYMPTOTIC DUAL-FANO HOSTILE CORE.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Rooted weighted circuit objective

Let `M` be a binary matroid with distinguished root `r` and nonnegative weights
`w(e)` on `E(M)-{r}`. Define

\[
\mu_r(M,w)=\min\{w(C-r): C\text{ is a circuit of }M,\ r\in C\}.
\]

For the cubic square Exact-One source, `M=M_F2([A|1])`, `r=e_b`, original
columns have weight one and the root has weight zero. The already proved syndrome
identity gives

\[
A\text{ Exact-One SAT}\iff \mu_r(M,w)=n/3.
\]

## 2. Binary circuit-cocircuit parity

In a binary matroid every circuit and cocircuit meet in an even number of
elements.

Hence if `{a,b}` is a 2-cocircuit disjoint from the root, every circuit uses
`a,b` either both or neither.

If `{r,a}` is a 2-cocircuit containing the root, every circuit through `r`
necessarily contains `a`.

These parity facts make series pairs exact weighted contractions rather than
branching objects.

## 3. Nonroot series-pair contraction

### Theorem RSP-1

Let `{a,b}` be a 2-cocircuit of binary `M`, with `r notin {a,b}`. Form

```text
M' = M / a
w'(b) = w(a)+w(b)
w'(e) = w(e) for all other nonroot e.
```

Then

\[
\boxed{\mu_r(M,w)=\mu_r(M',w')}.
\]

Moreover a minimum rooted circuit of `M'` lifts in polynomial time:
- if it avoids `b`, keep the same circuit;
- if it contains `b`, insert `a`.

### Proof

Because `{a,b}` is a cocircuit and `M` is binary, every circuit of `M` meets
`{a,b}` evenly. Thus a rooted circuit either avoids both or contains both.

Under contraction of `a`, a circuit containing both maps to its image with `a`
removed and still containing `b`; its weight is preserved exactly because the
new weight of `b` is `w(a)+w(b)`. A circuit avoiding both is unchanged.
Conversely, circuits of `M/a` that contain `b` lift through the series pair by
reinserting `a`; circuits avoiding `b` lift unchanged. Taking minima proves the
identity. QED.

## 4. Root-series contraction

### Theorem RSP-2

Let `{r,a}` be a 2-cocircuit. Every rooted circuit contains `a`. Contract `a`,
keep `r` distinguished, and define a fixed offset

\[
\kappa' = \kappa+w(a).
\]

Then

\[
\boxed{\mu_r(M,w)+\kappa=\mu_r(M/a,w|_{E-a})+\kappa'}.
\]

Witness lifting reinserts `a` in every rooted circuit.

This is an exact forced-cost contraction.

## 5. Polynomial preprocessing

A 2-cocircuit is recognizable in polynomial time from a binary matrix
representation. Equivalently, `{a,b}` is a cocircuit iff deleting the pair lowers
rank by one while deleting either element alone does not.

Repeatedly apply RSP-1/RSP-2 until no rooted or nonroot series pair remains.
Each step removes one element, preserves the exact rooted optimum up to the
explicit offset, and stores one constant-size lifting record. Thus total
construction, contraction bookkeeping, and witness reconstruction are polynomial.

This is a genuine exact preprocessor for the rooted syndrome objective.

## 6. Frozen SAT_12_3 collapses

Use the exact `SAT_12_3` source from
`experiments/r5_e9_rooted_dual_fano_source_controls.py`.
It has one Exact-One witness `[0,1,2,3]` and the augmented matroid contains both
rooted `F7` and rooted `F7*` minors.

The checker proves that the augmented matroid has four disjoint nonroot
2-cocircuits:

```text
{4,6}
{8,9}
{5,10}
{7,11}
```

Contract respectively `4,8,5,7`, accumulating their unit weights onto
`6,9,10,11`. The rooted optimum remains four.

The reduced 9-element matroid then has the root-series 2-cocircuit

```text
{0,e_b}.
```

Contract `0` and add its unit weight to the fixed offset. The remaining rooted
matroid has eight elements and rank four.

## 7. The eight-element core is AG(3,2), not S8

After row operations, the reduced column set is isomorphic to

```text
{0001,0010,0100,1000,0111,1011,1101,1110}.
```

Equivalently it is exactly

\[
\{v\in\mathbb F_2^4:(1111)\cdot v=1\}.
\]

This is the binary affine geometry `AG(3,2)`: the affine 3-cube represented as an
affine hyperplane in `F2^4`.

Source audit:
- Oxley notation / binary `(8,4,4)` affine geometry is standard `AG(3,2)`;
- Sage/PassageMath catalog records `AG(3,2)` as a rank-4, 8-element,
  3-connected binary matroid, identically self-dual;
- every single-element deletion is `F7*` and every single-element contraction is
  `F7`.

This explains why the constant core is saturated with both obstruction types.
It is not evidence for an unbounded hard family.

The weighted core has weights

```text
1,1,1,2,2,2,2,0(root)
```

up to relabelling, plus fixed offset `1`. Its minimum rooted circuit uses the
three unit-weight elements corresponding to source columns `[1,2,3]`, so the
reduced rooted cost is `3`; adding the offset gives `4=n/3`, recovering the
unique source witness `[0,1,2,3]`.

## 8. Consequence for the live residual

`SAT_12_3` is therefore not a genuine asymptotic rooted-dual-Fano obstruction.
It is exactly reducible to a constant `AG(3,2)` terminal.

The next hostile object must survive all prior terminals **and** the new series
preprocessor. In particular the matroid component containing `e_b` must be
series-irreducible; for a genuinely decomposition-resistant torso the natural
next target is 3-connectivity.

Freeze the sharpened gate:

```text
R5_E9_SERIES_IRREDUCIBLE_ROOTED_DUAL_FANO_GLOBAL_GATE_V1
```

A useful hostile family must have unbounded size and simultaneously survive:

```text
rooted F7 through e_b,
rooted F7* through e_b,
no nonroot 2-cocircuit contraction,
no root-series forced contraction,
all previously admitted polynomial terminals.
```

A PASS requires either:
1. an exact polynomial contraction/decomposition on the full intersection
   residual;
2. a polynomial terminal covering every remaining source instance; or
3. the end-to-end universal SAT solver contract.

## 9. Anti-loop

Do not reuse `SAT_12_3` as evidence that the rooted dual-Fano intersection is
asymptotically hard without first applying exact series compression.

Do not identify the final 8-element core with `S8`: its standard source form is
`AG(3,2)`.

## 10. Ceiling

```text
NONROOT 2-COCIRCUIT WEIGHT AGGREGATION
= EXACT

ROOT-SERIES FORCED-COST CONTRACTION
= EXACT

TOTAL SERIES PREPROCESSOR
= POLYNOMIAL

SAT_12_3 ROOTED DUAL-FANO CONTROL
= EXACTLY CONTRACTS TO CONSTANT AG(3,2)

SAT_12_3 AS ASYMPTOTIC HOSTILE RESIDUAL
= REJECTED

UNBOUNDED SERIES-IRREDUCIBLE DUAL-FANO SOURCE FAMILY
= NOT YET ESTABLISHED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
