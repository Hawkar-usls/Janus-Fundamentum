# R5 E9 — Single-Odd Rooted Dual-Fano Polynomial Syndrome Terminal

Date: 2026-09-28

Status: `JANUS_SOURCE_BOUND_CLASSICAL_POLYNOMIAL_TERMINAL__DUAL_FANO_INTERSECTION_FRONTIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_ROOTED_MFMC_SYNDROME_POLY_TERMINAL_2026-09-28_v1.0.md`
- `research/R5_E9_ROOTED_F7STAR_SOURCE_CONTROLS_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_rooted_dual_fano_source_controls.py`

External sources:
- K. Truemper, *Max-Flow Min-Cut Matroids: Polynomial Testing and Polynomial Algorithms for Maximum Flow and Shortest Routes*, Mathematics of Operations Research 12(1), 72–96 (1987), DOI `10.1287/moor.12.1.72`.
- A. N. Letchford, *Binary Clutter Inequalities for Integer Programs*, Mathematical Programming 98 (2003), 201–221. Section 3 records as Theorem 4 the Truemper single-odd-element shortest-odd-circuit result: SOC is polynomial when the unique odd element `f` is in no `F7` minor, or is in no `F7*` minor.

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT STRICTLY ENLARGES THE ROOTED-MFMC POSITIVE REGION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact source objective is a single-odd SOC instance

Let `A` be a cubic square Exact-One incidence matrix and put `b=1_n`. Over `F2` form

```text
A_plus = [A | b]
```

and let `e_b` be the final column. Give every original-column element weight one and `e_b` weight zero.

The already proved syndrome identity is

\[
\mu(A)=\min\{|x|:Ax=b\pmod 2\}
\]

and this equals the minimum weight of a circuit of `M_F2(A_plus)` containing `e_b`. Moreover

\[
A\text{ is Exact-One SAT}\iff \mu(A)=n/3.
\]

Now label exactly one matroid element odd:

```text
p(e_b)=1,
p(e)=0 for every original-column element e.
```

For every circuit `C`,

```text
p(C)=1  iff  e_b in C.
```

Therefore the JANUS rooted shortest-circuit objective is literally the Short Odd Circuit problem with a unique odd element `e_b`; no approximation or additional reduction is used.

## 2. Truemper single-odd theorem

The source-bound classical result is:

> For a binary matroid with exactly one odd element `f`, Short Odd Circuit is polynomial-time solvable if either there is no `F7` minor using `f`, or there is no `F7*` minor using `f`.

Here `using f` is rooted: the minor must retain `f`; an `F7`/`F7*` minor obtainable only after deleting or contracting `f` does not count.

Thus the existing rooted-MFMC branch (`no rooted F7*`) is only one side of a larger polynomial union.

### Theorem RDF-1

For every source-generated cubic square Exact-One matrix `A`, deterministic polynomial decision and witness reconstruction are available whenever at least one of

```text
NO_ROOTED_F7_THROUGH_e_b
NO_ROOTED_F7STAR_THROUGH_e_b
```

holds in the connected component of `M_F2([A|1])` containing `e_b`.

Algorithm:
1. solve `Ax=1` over `F2`; if inconsistent return `UNSAT`;
2. restrict to the matroid component containing `e_b`;
3. use the polynomial rooted-minor recognition machinery underlying Truemper's theorem;
4. if at least one rooted obstruction family is absent, run the polynomial single-odd SOC algorithm with weights `(1,...,1,0)`;
5. obtain optimum `mu` and a minimum odd circuit;
6. return `SAT` iff `3 | n` and `mu=n/3`;
7. reconstruct the Boolean selector from the original elements of the returned circuit and verify `Ax=1` over the integers.

All reconstruction and final verification are polynomial.

## 3. Exact finite source controls

The companion checker performs complete rooted seven-element minor censuses.

### FANO_7

For the augmented Fano `7_3` source:

```text
rooted F7 minors     = 7
rooted F7* minors    = 7
```

Contraction of any one original column yields a rooted `F7`; deletion of any one original column yields a rooted `F7*`.

This control lies in the dual-Fano intersection, though `n=7` makes Exact-One trivially UNSAT by divisibility.

### AFFINE_3X3

For the SAT affine `9_3` source:

```text
rooted F7 minors     = 0
rooted F7* minors    = 0
```

so it lies deeply inside the polynomial region.

### SAT_12_3

For the frozen unique-model SAT `12_3` source from the rooted-F7* control:

```text
rooted F7 minors     = 80
rooted F7* minors    = 144
Exact-One models     = 1
```

Therefore the strengthened polynomial terminal does not eliminate the live residual: genuine satisfiable source instances exist with both rooted obstructions through `e_b`.

## 4. Sharpened hard residual

The old residual

```text
rooted F7* through e_b
```

is too broad.

The exact surviving gate is now

```text
R5_E9_ROOTED_DUAL_FANO_INTERSECTION_GLOBAL_CONTRACTION_GATE_V1
```

with source condition

```text
A = cubic square linear Exact-One carrier,
Ax=1 over F2 is consistent,
e_b belongs to a rooted F7 minor,
e_b belongs to a rooted F7* minor.
```

A PASS must give one of:
1. an exact polynomial contraction eliminating at least one rooted dual-Fano obstruction while preserving `mu(A)` and witness lifting;
2. a polynomial decomposition whose total semantic interface state is polynomially bounded;
3. a stronger source-specific polynomial terminal covering the entire dual-Fano intersection;
4. an end-to-end deterministic polynomial algorithm for the source carrier.

Forbidden pseudo-progress:
- treating presence of either rooted minor as SAT/UNSAT status;
- branching independently on constant-size minors without a polynomial global branch bound;
- deleting/contracting obstruction elements without preserving the rooted minimum-circuit objective;
- invoking generic binary-matroid shortest circuit as a free oracle.

## 5. Ceiling

```text
EXACT-ONE = SINGLE-ODD SOC THRESHOLD
= PROVED

NO ROOTED F7* THROUGH e_b
= POLY (prior rooted-MFMC terminal)

NO ROOTED F7 THROUGH e_b
= POLY (Truemper single-odd SOC theorem)

TRUE SURVIVING MATROID OBSTRUCTION
= ROOTED F7 AND ROOTED F7* BOTH THROUGH e_b

SAT_12_3 DUAL-FANO INTERSECTION CONTROL
= YES / EXACT

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
