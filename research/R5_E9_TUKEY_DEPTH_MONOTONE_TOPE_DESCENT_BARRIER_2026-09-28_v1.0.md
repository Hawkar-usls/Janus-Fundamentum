# R5 E9 — Tukey-Depth Monotone Tope-Descent Barrier

Date: 2026-09-28

Status: `JANUS_EXACT_SAT_COUNTERCONTROL__MONOTONE_TOPE_DESCENT_FALSIFIED__AUGMENTING_CASCADE_EXPOSED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_FRACTIONAL_SUPPORT_EXACT_CLOSURE_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_tukey_depth_monotone_tope_descent_barrier.py`

Scientific ceiling:

```text
THE SOURCE KERNEL DEPTH OBJECTIVE HAS STRICT NON-GLOBAL LOCAL MINIMA.
A GREEDY ALGORITHM THAT ONLY CROSSES TO A LOWER-DEPTH ADJACENT TOPE IS FALSE,
EVEN ON THE FROZEN 15-VARIABLE SAT CONTROL.

THE SAME CONTROL EXHIBITS AN EXACT FINITE AUGMENTING CASCADE
6 -> 8 -> 7 -> 6 -> 5,
SO NONMONOTONE / AUGMENTING-PATH-LIKE MOVES REMAIN OPEN.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Depth boundary recalled

For a cubic square Exact-One source matrix `A`, every full-support
`y in ker_Q(A)` has

```text
p(y)=#{i:y_i>0} >= n/3
```

after orienting the tope to its smaller side, and when `3|n`,

```text
A SAT iff the minimum chamber-positive count h(A)=n/3.
```

For `n=15`, the exact boundary is therefore `p=5`.

A tempting polynomial algorithm is:

```text
construct any full-support rational-kernel tope;
while an adjacent chamber has smaller p:
    cross to it;
accept iff p reaches 5.
```

This note gives an exact counterexample to that monotone rule.

## 2. Frozen PG15 SAT source

Use the frozen cubic SAT control with rows

```text
(1,2,3)
(1,10,11)
(1,12,13)
(2,9,11)
(2,12,14)
(3,4,7)
(3,5,6)
(4,9,13)
(4,10,14)
(5,8,13)
(5,10,15)
(6,8,14)
(6,9,15)
(7,8,15)
(7,11,12)
```

Its rational rank is `11` and its rational nullity is `4`.

One exact rational-kernel basis, written as a `15 x 4` row matrix `B`, is

```text
1  (-1,-1, 0, 0)
2  (-1, 0,-1, 0)
3  ( 2, 1, 1, 0)
4  (-1,-1,-1, 1)
5  (-1,-1, 0, 0)
6  (-1, 0,-1, 0)
7  (-1, 0, 0,-1)
8  ( 1, 0, 0, 0)
9  ( 1, 0, 1,-1)
10 ( 1, 1, 0,-1)
11 ( 0, 0, 0, 1)
12 ( 1, 0, 0, 0)
13 ( 0, 1, 0, 0)
14 ( 0, 0, 1, 0)
15 ( 0, 0, 0, 1)
```

Thus the coincident arrangement-hyperplane classes are exactly

```text
{1,5}, {2,6}, {3}, {4}, {7}, {8,12},
{9}, {10}, {11,15}, {13}, {14}.
```

Crossing one chamber facet flips precisely one such projective row class.

## 3. An exact non-global local minimum

Take kernel coefficient vector

```text
alpha_0=(-1,2,2,-2).
```

Then

```text
y_0=B alpha_0
   =(-1,-1,2,-5,-1,-1,3,-1,3,3,-2,-1,2,2,-2).
```

Direct multiplication gives

```text
A y_0 = 0,
```

and every coordinate is nonzero. Its positive set is

```text
P_0={3,7,9,10,13,14},
```

so

```text
p(y_0)=6.
```

The source sign-count theorem gives exactly

```text
3 p - n = 3
```

two-positive (`++-`) source rows. They are

```text
(3,4,7),
(4,9,13),
(4,10,14).
```

Hence this is a legitimate full-support kernel chamber strictly above the SAT
boundary.

## 4. Why no adjacent chamber can lower p

Every positive coordinate of `y_0` is a singleton projective row class:

```text
3,7,9,10,13,14.
```

For each one there is a source row in which it is the unique positive entry:

```text
3  -> (1,2,3)
7  -> (7,8,15)
9  -> (2,9,11)
10 -> (1,10,11)
13 -> (1,12,13)
14 -> (2,12,14)
```

If one of these singleton signs were crossed from `+` to `-` while every other
arrangement sign stayed fixed, the displayed source row would become `---`.
That is impossible for a full-support rational-kernel vector because the three
entries in every source row sum to zero.

Therefore no facet crossing that removes a positive coordinate is feasible.

There is one negative singleton class, coordinate `4`. Flipping it to positive
would make source row

```text
(3,4,7)
```

all positive, so that crossing is impossible as well.

The only remaining projective classes are

```text
{1,5}, {2,6}, {8,12}, {11,15},
```

and both coordinates in every one of them are negative in `y_0`. Any feasible
facet crossing through one of those classes therefore changes

```text
p: 6 -> 8.
```

Consequently every adjacent chamber of the `y_0` chamber has strictly larger
positive count, in fact count `8` whenever it exists.

Thus `p=6` is a strict local minimum of the exact source-kernel chamber graph.

## 5. It is not the global minimum

The same frozen source has the Exact-One witness

```text
X={3,11,13,14,15}.
```

Its kernel word

```text
y_*=3 1_X - 1
    =(-1,-1,2,-1,-1,-1,-1,-1,-1,-1,2,-1,2,2,2)
```

has exactly five positive coordinates. Therefore

```text
h(A)<=5.
```

The universal source depth floor gives `h(A)>=5`, hence

```text
h(A)=5.
```

So the chamber of `y_0` is a strict **non-global** local minimum:

```text
local p = 6,
global p = 5.
```

This alone falsifies monotone adjacent-tope descent as a universal exact
algorithm.

## 6. Exact nonmonotone escape / augmenting cascade

The countercontrol is more informative than a dead end. The following exact
full-support rational-kernel vectors form a chamber path:

```text
p=6
P0={3,7,9,10,13,14}
alpha=(-1,2,2,-2)
y=(-1,-1,2,-5,-1,-1,3,-1,3,3,-2,-1,2,2,-2)

p=8
P1={3,7,9,10,11,13,14,15}
alpha=(-2,4,4,1)
y=(-2,-2,4,-5,-2,-2,1,-2,1,1,1,-2,4,4,1)

p=7
P2={3,9,10,11,13,14,15}
alpha=(-1,4,4,2)
y=(-3,-3,6,-5,-3,-3,-1,-1,1,1,2,-1,4,4,2)

p=6
P3={3,10,11,13,14,15}
alpha=(-1,4,2,2)
y=(-3,-1,4,-3,-3,-1,-1,-1,-1,1,2,-1,4,2,2)

p=5
P4={3,11,13,14,15}
alpha=(-1,2,2,2)
y=(-1,-1,2,-1,-1,-1,-1,-1,-1,-1,2,-1,2,2,2)
```

Successive sign separators are exactly

```text
P0 -> P1 : {11,15}
P1 -> P2 : {7}
P2 -> P3 : {9}
P3 -> P4 : {10}.
```

Each separator is one projective hyperplane class of `B`. Both endpoint topes
of every step are explicitly realized, so the corresponding chambers are
adjacent.

Hence the exact escape profile is

```text
6 -> 8 -> 7 -> 6 -> 5.
```

Interpretation: a two-coordinate activation opens a sequence of three
single-coordinate discharges. This looks like an augmenting-path/cascade move,
not like monotone local descent.

No universal claim is made from this single finite control.

## 7. Anti-loop consequence

Freeze the failed shortcut:

```text
MONOTONE_SOURCE_KERNEL_TOPE_DESCENT
= FALSIFIED.
```

Forbidden future pseudo-progress:
- claim that every non-boundary chamber has a lower-depth neighbor;
- call local optimality of `p` a certificate of UNSAT;
- use ordinary steepest descent on the tope graph as the universal solver;
- infer convexity of chamber depth from the linearity of the underlying kernel.

The PG15 SAT control already refutes all four.

## 8. New live gate

Open:

```text
R5_E9_SOURCE_KERNEL_AUGMENTING_CASCADE_GATE_V1
```

The target is no longer monotone descent. A PASS must give one of:

1. a polynomial-time method that, from any non-boundary source-kernel chamber,
   finds a polynomial-description nonmonotone augmenting cascade ending at a
   strictly smaller depth whenever the source is SAT;
2. a polynomially bounded potential stronger than raw `p` that decreases over
   such cascades and reaches the `n/3` boundary exactly on SAT instances;
3. a polynomial UNSAT certificate proving that no boundary tope exists;
4. a different complete source-specific algorithm.

Mandatory hostile controls:
- this PG15 local-minimum chamber `P0`;
- the PG15 boundary chambers;
- the singular rank-14 UNSAT depth-`6/15` control;
- the high-nullity / lift families already frozen in E9.

A fixed bounded-lookahead claim is not admissible without an arbitrary-size
proof: this control only shows that lookahead depth one is insufficient.

## 9. Ceiling

```text
SOURCE KERNEL DEPTH FLOOR
= 1/3

PG15 SAT GLOBAL DEPTH
= 5/15

EXPLICIT PG15 LOCAL MINIMUM
= 6/15

EVERY FIRST FACET EXIT FROM THAT CHAMBER
= DEPTH 8/15 WHEN FEASIBLE

EXPLICIT ESCAPE CASCADE
= 6 -> 8 -> 7 -> 6 -> 5

MONOTONE ADJACENT-TOPE DESCENT
= FALSE

POLYNOMIAL AUGMENTING-CASCADE THEOREM
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```