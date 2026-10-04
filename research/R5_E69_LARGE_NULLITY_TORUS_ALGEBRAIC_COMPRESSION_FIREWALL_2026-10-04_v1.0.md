# R5 E69 — Large-Nullity Torus / Algebraic-Compression Firewall

Date: 2026-10-04

Status:
`LARGE_BINARY_NULLITY_DOES_NOT_FORCE_BOUNDED_OR_LOG_GRAPH_WIDTH__TORUS_FAMILY_HAS_D_EQ_SQRT_N_MINUS_1__ALGEBRAIC_COMPRESSION_NOT_SEPARATOR_DP`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

THE TARGET REMAINS A UNIVERSAL, PROVABLE POLYNOMIAL-TIME ALGORITHM FOR THE
SQUARE-CUBIC-LINEAR EXACT-ONE HARD CORE.  P_VS_NP REMAINS OPEN.

E69 TESTS THE POST-E68 DICHOTOMY HOPE

    SMALL BINARY NULLITY -> E61 ENUMERATION,
    LARGE BINARY NULLITY -> FORCED POLYNOMIAL STRUCTURAL DECOMPOSITION.

THE SIMPLE SEPARATOR/WIDTH VERSION OF THE SECOND IMPLICATION IS FALSE.
A CONNECTED INFINITE TORUS FAMILY HAS

    dim_F2 ker(A) = Theta(sqrt(n))

AND LEVI TREEWIDTH Omega(sqrt(n)).

HOWEVER THE SAME FAMILY IS EXACTLY SOLVABLE BY A GLOBAL ALGEBRAIC/SYMMETRY
COMPRESSION.  THIS SHOWS WHAT A LARGE-NULLITY BRANCH WOULD HAVE TO LOOK LIKE:
NOT GENERIC SMALL-SEPARATOR DP, BUT A STRONGER ALGEBRAIC OR QUOTIENT STRUCTURE.
```

Replay correction: the first E69 CI run caught an overstatement in the general
even-section congruence.  The correct universal relation is

```text
D == n (mod 3),
```

not `D == 0 (mod 3)` unless `3|n`.  The torus nullity theorem and the width
firewall were unaffected.  This correction is incorporated below.

## 1. Anti-loop from Fundamentum

Binding earlier results:

* E58:
  `Exact-One SAT iff max_{k in ker_F2(A)} |k| = 2n/3`.
* E61:
  `d=dim ker_F2(A)=O(log n)` gives exact `2^d poly(n)` enumeration.
* E63:
  raw gadget nullity can be inflated and must be quotiented before being treated
  as hardness structure.
* E64-E68:
  connected post-quotient carriers survive simple spectral, exchange, low-moment
  and degree-2 SDP shortcuts.

Therefore E69 works directly with a genuine connected post-quotient family.

## 2. Open-literature anti-loop

Bounded branch-width/decomposition width is algorithmically useful for
finite-field represented matroids, but the literature does not provide a
converse saying that large nullity forces small branch-width/treewidth.  Relevant
references include Hlineny on matroid branch-width, Kral on decomposition width,
and Jeong-Kim-Oum on branch decompositions of represented structures.

The polynomial `1+X+Y` is also not new: over F2 it defines the classical
Ledrappier/3-dot algebraic subshift.  A modern reference is Kari-Moutot,
"Nivat's conjecture and pattern complexity in algebraic subshifts", TCS 777
(2019).  E69 uses a finite-torus specialization of this known algebraic object as
an anti-loop/control family.

## 3. The torus carrier

Fix `m>=3` and index rows and columns by

```text
G_m = Z_m x Z_m.
```

Define

```text
row(i,j) = {(i,j), (i+1,j), (i,j+1)}
```

modulo `m`, equivalently

```text
A_m = I + P_x + P_y.
```

Rows and columns have weight three.  The six ordered nonzero differences of
`{(0,0),(1,0),(0,1)}` are distinct, so row-row and column-column intersections
have size at most one.  The Levi graph is connected because the two translations
generate `Z_m x Z_m`.

Thus `A_m` is a connected square-cubic-linear carrier.

## 4. Exact binary nullity for `m=2^r-1`

Set

```text
m = 2^r - 1.
```

Because `m` is odd, `X^m-1` and `Y^m-1` split with distinct roots over
`F_{2^r}`.  Scalar extension preserves rank/nullity, and the group algebra
becomes diagonal in the character basis.

A character `(alpha,beta)` has eigenvalue

```text
1 + alpha + beta.
```

Every nonzero element of `F_{2^r}` is an `m`th root of unity.  Hence zero
eigenvalue characters are exactly

```text
beta = 1+alpha,
alpha in F_{2^r} minus {0,1}.
```

There are `2^r-2=m-1` of them.  Therefore

```text
boxed:
dim_F2 ker(A_m) = m-1.
```

Since `n=m^2`,

```text
boxed:
d = sqrt(n)-1.
```

This is already far beyond the E61 logarithmic-enumeration regime.

## 5. Large nullity does not force bounded/log graph width

Contract in the Levi graph every natural matching edge

```text
row(i,j) -- column(i,j).
```

The two remaining incidences become

```text
(i,j)--(i+1,j),
(i,j)--(i,j+1),
```

so the contraction minor is

```text
C_m square C_m.
```

Deleting wrap edges gives the ordinary `m x m` grid.  Grid treewidth is
Theta(m), and treewidth is minor-monotone.  Hence

```text
boxed:
tw(Levi(A_m)) = Omega(m) = Omega(sqrt(n)).
```

Therefore

```text
large nullity -> bounded/log Levi-treewidth -> polynomial separator DP
```

is false even inside connected square-cubic-linear carriers.

This statement is deliberately limited to the graph-width route; it does not
rule out every matroidal or algebraic compression.

## 6. Kernel words are cubic even-sections

Let `H_A` have the columns of `A` as vertices and the row supports as
3-uniform hyperedges.  For `U=supp(k)`,

```text
A k = 0 mod 2
```

iff every hyperedge meets `U` in `0` or `2` points.

Keep only the hyperedges meeting `U` twice and replace each by the pair of
selected vertices.  Every selected column lies in exactly three rows, and every
such row must contain one other selected column.  Thus the resulting graph on
`U` is cubic.  Linearity makes it simple.

Hence

```text
boxed:
k in ker_F2(A)
iff supp(k) is a cubic even-section of H_A.
```

Let `D(k)` be the number of row-hyperedges disjoint from `U`.  There are `n-D`
used hyperedges.  Double counting gives

```text
3|U| = 2(n-D).
```

Therefore the correct universal congruence is

```text
boxed:
D == n (mod 3),
```

and

```text
|k| = 2(n-D)/3.
```

When `3|n` this specializes to

```text
D == 0 (mod 3),
|k| = 2n/3 - 2D/3.
```

This is exactly the regime used by E65, where `D=3m_defect`.

Combining with E58 (and hence automatically `3|n` in any SAT instance):

```text
boxed:
Exact-One SAT
iff there exists a kernel cubic even-section with D=0,
i.e. one using every row-hyperedge.
```

The first CI run failed precisely because the `D==0 mod 3` specialization had
been incorrectly asserted before checking `3|n`; the checker now enforces the
correct universal congruence.

## 7. The torus family is algebraically compressible

Every Exact-One solution uses exactly `n/3=m^2/3` columns, so `3|m` is
necessary.

If `3|m`, set

```text
x_(i,j)=1 iff i-j == 0 mod 3.
```

The three columns in row `(i,j)` have residues

```text
(i-j), (i-j)+1, (i-j)-1 mod 3,
```

so exactly one is selected.  Thus

```text
boxed:
A_m is Exact-One SAT iff 3 divides m.
```

For `m=2^r-1`,

```text
3 | (2^r-1) iff r is even,
```

hence

```text
boxed:
SAT iff r is even.
```

So this family simultaneously has

```text
d = Theta(sqrt(n)),
tw(Levi)=Omega(sqrt(n)),
```

and a constant-description exact decision rule.  This is the model lesson:
large-nullity compression, when it exists, can be global/algebraic rather than a
small-separator DP.

## 8. Hardness-bridge control

The checker also replays the frozen E17/E12 `q=6` RXC3 source.  Its binary
nullity is zero, so E58 immediately certifies UNSAT.  The highly translational
torus family is not claimed to represent the hard RXC3 branch and must not be
used as evidence that arbitrary large-nullity quotients admit Fourier
compression.

## 9. Consequence for the universal P=NP route

The desired dichotomy must now be sharpened to something stronger than width:

```text
small nullity
    -> E61 enumeration;

large nullity + compressible dependency algebra
    -> polynomial quotient/Fourier/recurrence solver;

large nullity without such compression
    -> unresolved universal frontier.
```

A genuine P=NP route has to prove the third case empty or solve it separately in
polynomial time.

The next object to study is therefore not nullity alone but the **dependency
algebra** of the left/right kernels: support growth, module/orbit structure,
short descriptions/recurrences, and the algebra generated by cubic
even-sections.  Every proposed theorem must be attacked against E12/RXC3 and
against connected non-gadget controls E64-E69.

## 10. Replay

Companion checker:

```text
experiments/r5_e69_nullity_structure_torus_firewall.py
```

It verifies `r=2,3,4,5` (`m=3,7,15,31`):

```text
* square/cubic/linear incidence;
* Levi connectivity;
* contraction to C_m square C_m;
* exact binary nullity m-1;
* cubic even-section structure for every computed kernel-basis word;
* correct universal congruence D == n mod 3;
* explicit Exact-One cover for 3|m;
* divisibility obstruction for 3 not dividing m;
* E58 top-shell witness when SAT;
* frozen E17 q=6 source nullity control.
```

Scientific status remains:

```text
P_VS_NP = OPEN.
```
