# R5 E8 6I — Global Sheet-Selection Delta-Matroid Falsifier

Date: 2026-09-23

Authority: `PROVED_FINITE_EXACT_MODEL_BINDING_FALSIFIER__NO_D1_PROMOTION`

Checker:

`research/tools/r5_e8_6i_sheet_selection_delta_matroid_falsifier.py`

Parent:

`R5_E8_6I_REPRESENTATION_CHANGE_COMPRESSION_CURRENCY_GATE_V1`

## 1. Question

Could the global choice of one frozen majority sheet per original clause itself form a
matroid / delta-matroid feasible family, so that global sheet coherence could be compressed
by direct matroid-intersection / delta-matroid machinery?

Use the natural ground set

```text
E = {(C,s) : clause C, sheet s in {0,1,2}}
```

and encode a sheet assignment as the size-m set containing exactly one `(C,s)`
for each of the m clauses.

A feasible set means that the conjunction of the selected majority-sheet relations is
satisfiable.

## 2. Minimal two-clause witness

Take

```text
C0 = (~x OR ~y OR ~z)
C1 = ( x OR ~y OR ~z).
```

For each clause choose one frozen sheet

```text
0 = M0(a,b,c)
1 = M1(a,NOT b,c)
2 = M2(a,b,NOT c).
```

Exhaustive evaluation of the eight Boolean assignments gives exactly the feasible sheet
pairs

```text
(0,0), (0,1), (0,2),
(1,0), (1,1),
(2,0), (2,2).
```

The pairs `(1,2)` and `(2,1)` are infeasible.

## 3. Matroid basis-exchange failure

Let

```text
A = {(C0,0),(C1,1)}
B = {(C0,2),(C1,0)}.
```

Both are feasible.

Choose

```text
e = (C0,0) in A\B.
```

The candidates in `B\A` are `(C0,2)` and `(C1,0)`.

Replacing `e` by `(C0,2)` produces selection `(2,1)`, which is infeasible.
Replacing it by `(C1,0)` no longer contains exactly one element for each clause and is
not in the feasible family.

Thus basis exchange fails.

Therefore the feasible global sheet-selection family is not the set of bases of a matroid
under the natural encoding.

## 4. Delta-matroid symmetric-exchange failure

The checker also evaluates the weaker delta-matroid symmetric-exchange axiom over the
same feasible set family.

For

```text
X = {(C0,0),(C1,1)}
Y = {(C0,2),(C1,0)}
```

it finds an element of `X Delta Y` for which no second symmetric-difference element
produces another feasible set.

Therefore:

```text
GLOBAL FEASIBLE SHEET-SELECTION FAMILY
=
NOT A DELTA-MATROID
```

already on two clauses.

## 5. Interpretation

This is stronger than the separate observation that high-arity `EQ_d` is not a
delta-matroid for `d>=3`.

Even if variable-coherence constraints are temporarily hidden and one looks directly at
the induced family of satisfiable sheet selections, the natural global choice family need
not satisfy delta-matroid exchange.

Thus the route

```text
GLOBAL SHEET CHOICES
->
ONE DIRECT MATROID / DELTA-MATROID OBJECT
->
MATCHING / INTERSECTION SOLVER
```

is falsified in the natural encoding.

## 6. Scope firewall

This does NOT rule out:

- an extended formulation with auxiliary elements;
- a nontrivial delta-matroid gadgetization;
- a different ground-set encoding;
- an efficiently-coverable delta-matroid representation proved by a new theorem;
- a representation-changing matching reduction that is not the natural sheet-choice family.

Any such escape must prove exact polynomial construction and reconstruction.

## 7. Ceiling

```text
DIRECT NATURAL GLOBAL SHEET
MATROID / DELTA-MATROID CURRENCY
=
FALSIFIED

EXTENDED MATCHING / DELTA-MATROID REPRESENTATION
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
