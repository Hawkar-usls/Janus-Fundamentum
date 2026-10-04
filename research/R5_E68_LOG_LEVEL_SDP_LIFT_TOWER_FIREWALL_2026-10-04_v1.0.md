# R5 E68 — Log-Level Complexity / SDP Lift-Tower Firewall

Date: 2026-10-04

Status:
`LOG_LEVEL_IS_NOT_YET_POLYNOMIAL__MOMENT_ONLY_ORDER_GROWS_ON_LIFT_TOWER__DEGREE2_INCIDENCE_SDP_DOES_NOT_SEPARATE_TRANSPOSE_PAIR`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

THE TARGET REMAINS A UNIVERSAL, PROVABLE POLYNOMIAL-TIME ALGORITHM FOR THE
SQUARE-CUBIC-LINEAR EXACT-ONE HARD CORE.  P_VS_NP REMAINS OPEN.

E68 CONTINUES E67 UNDER AN ANTI-LOOP RULE:

1. CHECK FUNDAMENTUM FIRST;
2. CHECK OPEN LITERATURE BEFORE REINVENTING A HIERARCHY;
3. REPLAY EVERY NEW CLAIM;
4. DO NOT CALL QUASI-POLYNOMIAL OR FIXED-INSTANCE CERTIFICATES A P=NP RESULT.
```

## 1. Why `t = O(log n)` is not enough by itself

E67 computes the first `t` dual weight counts by support enumeration / rowspace
membership.  For fixed `t` this costs

```text
n^{O(t)}.
```

Therefore

```text
t = O(1)      -> polynomial,
t = O(log n)  -> n^{O(log n)} = exp(O(log^2 n)),
```

so a logarithmic hierarchy level is only quasi-polynomial under the current
implementation.

For the actual P=NP target, one of the following is required:

```text
A. a universal constant hierarchy level;
B. a new compressed algorithm evaluating t=O(log n) hierarchy data in poly(n);
C. a different polynomial certificate / construction entirely.
```

This is a complexity firewall against accidentally lowering the target from
polynomial to quasi-polynomial time.

## 2. Open-literature anti-loop

The hierarchy direction is real, but there is no known theorem from the open
literature that gives our desired constant or logarithmic exact level on the
square-cubic-linear Exact-One family.

### 2.1 Higher-order Delsarte LPs

Coregliano, Jeronimo and Jones introduced a complete LP hierarchy for linear
codes.  Their general completeness guarantee recovers the true optimum at level
`O(n^2)`; this is a completeness theorem, not a low-level polynomial algorithm
for our problem.

Reference:

* Leonardo Nagami Coregliano, Fernando Granha Jeronimo, Chris Jones,
  "A Complete Linear Programming Hierarchy for Linear Codes", ITCS 2022,
  DOI `10.4230/LIPIcs.ITCS.2022.51`.

The later higher-order Delsarte literature strengthens and studies this family
of relaxations; it does not supply a universal `O(log n)` exactness theorem for
our incidence codes.

### 2.2 Coding-theory SDP hierarchies

Schrijver's Terwilliger-algebra SDP strengthens ordinary Delsarte by retaining
three-point information.  Laurent placed it inside a hierarchy of semidefinite
bounds for binary codes.  At any fixed stage the hierarchy is polynomial in
`n`, but the polynomial degree / SDP size grows sharply with the stage;
Laurent notes that the second full bound has `O(n^7)` variables, while
Schrijver's symmetry-reduced bound is of size `O(n^3)`.

References:

* Alexander Schrijver, "New Code Upper Bounds from the Terwilliger Algebra and
  Semidefinite Programming", IEEE Trans. Inf. Theory 51 (2005),
  DOI `10.1109/TIT.2005.851748`.
* Monique Laurent, "Strengthened semidefinite programming bounds for codes",
  Mathematical Programming 109 (2007), DOI `10.1007/s10107-006-0030-3`.
* Pin-Chieh Tseng, Ching-Yi Lai, Wei-Hsuan Yu,
  "Semidefinite programming bounds for binary codes from a split Terwilliger
  algebra", Designs, Codes and Cryptography (2023), arXiv `2203.06568`.

### 2.3 Hypergraph matching hierarchy warning

Our Exact-One problem is perfect matching in a 3-uniform 3-regular linear
hypergraph.  Generic hierarchy behavior for hypergraph matching is not benign:
Chan and Lau prove integrality gaps can survive a linear number of rounds of the
Sherali-Adams lift-and-project procedure for general `k`-uniform hypergraph
matching.

Reference:

* Yuk Hei Chan, Lap Chi Lau, "On linear and semidefinite programming
  relaxations for hypergraph matching", Mathematical Programming 135
  (2012), DOI `10.1007/s10107-011-0451-5`.

This result is NOT asserted to hold for our much narrower regular-linear
family.  Its role here is anti-loop: no generic LP/SDP hierarchy should be
assumed to become exact at logarithmic level without a new structural theorem.

## 3. Deterministic Tutte-12 lift tower

E67 produced a connected 126 x 126 two-lift of the Tutte-12 UNSAT orientation.
E68 continues the same deterministic construction with seeds

```text
1,2,3,4,5.
```

Starting from the 63 x 63 base carrier, the checked orders are

```text
n = 63,126,252,504,1008,2016.
```

Every checked matrix is

```text
square,
binary,
row weight 3,
column weight 3,
linear on both sides,
connected.
```

The construction is an iterated graph 2-cover of the girth-12 base, so no lift
can introduce a shorter cycle than the base carrier.

## 4. Exact binary-kernel data on the tower

Complete Gray-code enumeration gives:

| level | n | dim ker_F2 | code size | max kernel weight | SAT target 2n/3 | gap |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 63 | 14 | 16,384 | 40 | 42 | 2 |
| 1 | 126 | 16 | 65,536 | 80 | 84 | 4 |
| 2 | 252 | 17 | 131,072 | 160 | 168 | 8 |
| 3 | 504 | 18 | 262,144 | 320 | 336 | 16 |
| 4 | 1008 | 20 | 1,048,576 | 640 | 672 | 32 |
| 5 | 2016 | 22 | 4,194,304 | 1280 | 1344 | 64 |

Thus every checked tower member is UNSAT and the top-shell deficit doubles on
each checked lift.

However this tower is **not** a hardness witness for the universal problem.  On
all six checked levels

```text
2^{dim ker} <= 5 n^2.
```

So the E61/E58 exact kernel enumeration is itself polynomial-sized on this
finite tower.  The tower is useful as a hierarchy stress-test, not as evidence
that the full hard core is easy or hard.

## 5. Canonical discrete moment-only annihilator

Let the exact binary-kernel weight support be

```text
S = {w>0 : A_w>0}.
```

Define

```text
F(w) = product_{s in S} (w-s).
```

We only need nonnegativity on the allowed even grid

```text
G = {0,2,...,2n/3}.
```

Between consecutive non-root grid points where the sign of `F` changes, E68
inserts one exact sign-correction root.  Multiplying all correction factors
produces `H`; after choosing a global sign,

```text
Q(w) = +/- F(w) H(w)
```

satisfies

```text
Q(0)>0,
Q(s)=0 for every actual positive support weight s,
Q(w)>0 for every other allowed grid point.
```

Therefore

```text
sum_w A_w Q(w) = Q(0).
```

Any nonnegative pseudo weight distribution with `A_0=1` and the same polynomial
moments through `deg Q` must put zero mass on every positive grid point where
`Q>0`, in particular the forbidden SAT top shell.

This is an explicit moment-only UNSAT certificate.  It is a diagnostic
construction from the exact enumerator, not an algorithm for discovering the
support without already solving an exponential problem.

## 6. Observed certificate-order growth

The exact positive-support sizes are

```text
6,14,32,55,93,144.
```

The corresponding canonical sign-corrected moment-only annihilator degrees are

```text
boxed:
12,28,44,74,120,186.
```

The first three levels suggested the tempting pattern

```text
12 -> 28 -> 44   (+16 per doubling),
```

but the next levels immediately falsify it:

```text
44 -> 74 -> 120 -> 186.
```

Hence E68 freezes the claim

```text
"the Tutte lift tower empirically has a +16/logarithmic annihilator order"
```

as FALSE.

Important limitation: these numbers are sufficient orders for the explicit
moment-only annihilators above.  They are NOT proved to be the minimum exact
levels of the full Delsarte hierarchy, higher-order Delsarte hierarchy, or an
SDP hierarchy.

## 7. Degree-2 incidence-aware SoS/Lasserre firewall

E65 gives the transpose pair

```text
R   : UNSAT,
R^T : SAT with 36 Exact-One solutions.
```

Both are 63 x 63 square-cubic-linear Tutte-12 orientations with real nullity 14.

Let `A` denote either orientation and let `P` be the orthogonal projector onto
its right real kernel.

The E68 exact rational checker proves in both orientations

```text
diag(P) = (2/9) 1.
```

Set

```text
m = (1/3) 1,
X = (1/9) J + P.
```

Because `A 1 = 3 1` and `A P = 0`,

```text
A m = 1,
A X = (1/3) J.
```

Also

```text
diag(X)=m.
```

The degree-2 Boolean/Exact-One moment matrix is

```text
M = [ 1   m^T ]
    [ m    X  ].
```

Its Schur complement is

```text
X - m m^T = P >= 0,
```

so `M` is positive semidefinite.

Thus the same natural degree-2 incidence-aware Lasserre/SoS relaxation is
feasible for both the UNSAT orientation and its SAT transpose.

Therefore

```text
boxed:
degree-2 incidence-aware SDP does not decide the hard core.
```

This does NOT refute Schrijver/Terwilliger, split-Terwilliger, higher Lasserre,
or other stronger SDPs.  It only removes the lowest natural level from the
candidate list.

## 8. What survives E68

The universal frontier is now stricter.

A successful hierarchy route must provide at least one of:

```text
1. UNIVERSAL CONSTANT LEVEL
   A fixed LP/SDP/SoS level is exact for every square-cubic-linear carrier.

2. COMPRESSED LOG-LEVEL EVALUATION
   A t=O(log n) level is exact AND can be evaluated in poly(n), not n^{O(t)}.

3. STRUCTURE-SENSITIVE COLLAPSE
   Prove that our incidence codes admit a special block diagonalization,
   recursion, separator, or quotient making the relevant high-order moments
   polynomially accessible.

4. DIFFERENT UNIVERSAL CERTIFICATE
   Leave generic hierarchy machinery and exploit a new invariant specific to
   3-regular linear incidence systems.
```

The next correct experiment is not to extrapolate the lift tower.  It is to
attack a **post-quotient hard family whose nullity is not already logarithmic**,
and test whether an incidence-aware 3-point / Terwilliger-style SDP or another
compressed certificate separates SAT from UNSAT there.

## 9. Replay

Companion checker:

```text
experiments/r5_e68_log_level_sdp_tower_firewall.py
```

It verifies:

```text
* exact SAT/UNSAT status of the Tutte transpose pair;
* exact rational right-kernel projectors;
* constant diagonal 2/9 in both orientations;
* the explicit degree-2 pseudo-moment equations;
* six deterministic connected square-cubic-linear lift levels;
* complete binary-kernel enumerators on all six checked levels;
* exact nullities, top-shell maxima and doubled deficits;
* positive-support counts;
* canonical discrete annihilator degrees 12,28,44,74,120,186;
* the finite-tower warning 2^d <= 5 n^2.
```

Scientific status remains:

```text
P_VS_NP = OPEN.
```
