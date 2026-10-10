# R5 E9 — PG15 minimal 8-macro affine pin and Boolean NOR return

Date: 2026-10-01

Status:
`JANUS_EXACT_PG15_MINIMAL_AFFINE_MACRO_ARITY8__NOR_LOCAL_RETURN__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_PG15_AUGMENTED_TERNARY_FUNDAMENTAL_SUPPORT7_BARRIER_2026-09-30_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_CANONICAL_DIAMOND_CYCLE_AF3_POLYSIZE_COVER_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_pg15_minimal_8macro_affine_pin_nor_return.py`

## 1. Purpose

The Paley-orbit branch admits a five-coordinate `K4-e` diamond whose avoidance forces one affine endpoint equation, and those macro equations close in polynomial size.

PG15 is the first frozen positive parallel-simple AF3 residual that survives the older APSQ simplifications. This note asks the exact transfer question:

> how many coordinate-nonzero conditions are needed before the surviving affine PG15 states are forced into a proper affine subspace?

This is a finite exact question on the complete affine solution space of the frozen PG15 source, not a heuristic gadget search.

## 2. Frozen affine chart

Let `A` be the canonical `15 x 15` PG15 cubic Exact-One incidence matrix with rows

```text
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
(3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
(5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12).
```

Work over `F3` with

```text
A r = 1.
```

Exact RREF has rank `11`, hence the affine solution space has dimension `4` and exactly `3^4=81` points.

Use the free coordinates

```text
t0=r12,
t1=r13,
t2=r14,
t3=r15
```

in one-based source indexing. In this chart the fourth source coordinate is

```text
r4 = 1 + 2 t0 + 2 t1 + 2 t2 + t3.
```

The nowhere-zero PG15 solutions are exactly four of the 81 affine points.

## 3. Macro definition

For a coordinate subset `S`, define

```text
U(S) = { r : A r=1 and r_i != 0 for every i in S }.
```

Let `affdim(S)` be the affine dimension over `F3` of `U(S)` in the four free parameters.

A coordinate macro has produced a new affine implication exactly when

```text
affdim(S) < 4.
```

The checker exhausts every subset through arity eight.

## 4. Exact minimal arity theorem

For every subset `S` with

```text
|S| <= 7,
```

the checker finds

```text
affdim(S) = 4.
```

Thus no combination of at most seven coordinate-nonzero conditions forces any new affine equation at all.

At arity eight, among all

```text
C(15,8)=6435
```

subsets, exactly eight have affine dimension three; the other `6427` still have affine dimension four.

Define the zero-based seven-coordinate core

```text
C = {2,3,6,8,9,12,13}.
```

The eight compressing subsets are exactly

```text
C union {j}
```

for

```text
j in {0,1,4,5,7,10,11,14}.
```

Every one of the eight macros has exactly five surviving affine points and forces the same free-parameter equation

```text
2 t0 + 2 t1 + 2 t2 + t3 = 0.
```

Since

```text
r4 = 1 + 2 t0 + 2 t1 + 2 t2 + t3,
```

this is precisely

```text
r4 = 1.
```

Therefore

```text
minimum coordinate-macro arity that can force any affine PG15 implication = 8.
```

This is an exact finite minimality statement for coordinate-nonzero macros on the frozen PG15 affine chart.

## 5. Seven-core plus one-trigger normal form

Avoiding only the seven core coordinates leaves exactly nine affine states.

Eight of those nine already satisfy

```text
r4=1.
```

The unique exceptional core-survivor has

```text
r4=2
```

and all eight trigger coordinates simultaneously equal zero.

Hence adding the nonzero condition for **any one** trigger removes exactly that exceptional branch and forces `r4=1`.

The arity-eight phenomenon is therefore not eight unrelated gadgets. It is one exact normal form:

```text
SEVEN NONZERO CORE COORDINATES
+
ANY ONE OF EIGHT NONZERO TRIGGERS
=>
r4=1.
```

## 6. Conditioned residual and Booleanization

Impose the proved affine pin

```text
r4=1.
```

The free parameters then satisfy

```text
t3 = t0+t1+t2.
```

The residual affine dimension is three.

For a globally nowhere-zero solution, the source coordinates imply

```text
t0,t1,t2 in {1,2}.
```

Encode Boolean bits by

```text
b_i = t_i - 1,
```

so `1 -> 0` and `2 -> 1`.

Exact enumeration of the conditioned residual gives the complete allowed Boolean relation

```text
(0,0,1),
(0,1,0),
(0,1,1),
(1,0,0).
```

Equivalently,

```text
b0 = NOR(b1,b2).
```

Thus the first non-Paley hard residual does not collapse to another affine island after the minimal macro pin. It exposes an exact Boolean NOR gate relation.

## 7. Scientific interpretation

This result has two parts that must not be conflated.

### Proven here

```text
Paley five-coordinate diamond transfer to PG15 = FALSE.
No coordinate macro of arity <=7 forces an affine equation.
Minimum affine-compressing coordinate macro arity = 8.
The unique arity-8 mechanism is seven-core + one-trigger.
Its affine implication is r4=1.
The conditioned nowhere-zero relation is exactly Boolean NOR.
```

### Not proved here

```text
An arbitrary NOR circuit is not yet source-realized by PG15 gadgets.
Fanout/composition with bounded source cost is not yet proved.
A universal hardness transfer is not claimed.
A universal polynomial solver is not obtained.
```

NOR is therefore a **local source-return frontier**, not by itself a complexity theorem about the full JANUS carrier.

## 8. Constructive next gate

Freeze

```text
R5_E9_PG15_NOR_SOURCE_PRESERVING_COMPOSITION_GATE_V1
```

The next exact questions are:

1. characterize every two-/three-terminal projection of the pinned PG15 residual;
2. test whether the NOR relation composes under legal source gluing without reintroducing exponential boundary state;
3. prove or falsify bounded-cost fanout/copy for the three Boolean parameters;
4. if composition closes polynomially, compare the resulting network with known Boolean-circuit normal forms rather than rediscovering SAT;
5. if composition fails, isolate the exact source invariant blocking NOR-network realization and exploit that invariant algorithmically;
6. keep witness reconstruction explicit at every contraction.

This is preferable to searching larger coordinate subsets blindly: the affine information content has already reached its exact ceiling on PG15.

## 9. Ceiling

```text
PG15 affine dimension                         = 4
coordinate macro affine implication arity <=7 = NONE
minimum affine implication arity              = 8
number of compressing arity-8 subsets         = 8
common implication                            = r4=1
conditioned affine dimension                  = 3
conditioned nowhere-zero Boolean relation     = NOR
NOR source-preserving composition             = OPEN
bounded-cost fanout                            = OPEN
universal polynomial solver                    = NOT PROVED
E8_D1                                           = EMPTY
P_VS_NP                                        = OPEN
```
