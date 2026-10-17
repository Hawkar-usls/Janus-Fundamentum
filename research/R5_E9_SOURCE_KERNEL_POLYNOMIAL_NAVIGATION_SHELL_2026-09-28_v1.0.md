# R5 E9 — Source-Kernel Polynomial Navigation Shell

Date: 2026-09-28

Status: `JANUS_DERIVED_POLYNOMIAL_NAVIGATION_SHELL__GLOBAL_BOUNDARY_DIRECTION_SELECTION_OPEN__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_TOPE_GEODESIC_AUGMENTING_PATH_BOUND_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_BOUNDARY_NONCONVEX_GATED_BARRIER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_source_kernel_polynomial_navigation_shell.py`

Scientific ceiling:

```text
AFTER THE RATIONAL-KERNEL REPRESENTATION CHANGE, THE FOLLOWING ARE
DETERMINISTIC POLYNOMIAL:

1. CONSTRUCT THE KERNEL BASIS;
2. DETECT FULL-RANK AND ZERO-KERNEL-ROW UNSAT TERMINALS;
3. CONSTRUCT ONE FULL-SUPPORT STARTING TOPE;
4. SIMPLIFY TO DISTINCT PROJECTIVE HYPERPLANES;
5. ENUMERATE THE COMPLETE FACET-NEIGHBORHOOD OF ANY GIVEN TOPE BY <= n LPs;
6. VERIFY A PROPOSED BOUNDARY TOPE / EXACT-ONE WITNESS;
7. IF A BOUNDARY TOPE EXISTS, A SHORTEST ROUTE TO ONE HAS LENGTH <= n.

THE ONLY UNSOLVED GLOBAL STEP IN THIS SHELL IS DETERMINISTIC SELECTION OF A
BOUNDARY-DIRECTED NEIGHBOR, OR A POLYNOMIAL CERTIFICATE THAT NO BOUNDARY
TOPE EXISTS.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Input and exact kernel representation

Let

```text
A in {0,1}^{n x n}
```

be a cubic square Exact-One source matrix. Compute a rational basis of

```text
K=ker_Q(A)
```

by exact Gaussian elimination and write the basis as columns of

```text
B in Q^{n x d}.
```

Then every rational kernel vector is

```text
y=B alpha.
```

The already proved source equivalence is

```text
A x = 1, x Boolean
iff
there exists full-support y=B alpha whose positive set has size n/3
iff
source-kernel origin depth = n/3.
```

Exact rational Gaussian elimination has polynomial bit complexity in this
integer input model, so constructing `B` is polynomial.

Immediate terminals:

```text
d=0                         => UNSAT,
some row b_i of B is zero   => UNSAT,
n mod 3 != 0                => UNSAT.
```

The zero-row terminal is sound because every SAT witness would provide the
full-support kernel vector `3x-1`.

Assume these terminals fail.

## 2. Deterministic polynomial construction of one full-support tope

A remaining concern is whether obtaining even one chamber of the kernel
arrangement could hide arrangement enumeration. It does not.

For an integer parameter `t`, take the moment-curve coefficient vector

\[
\alpha(t)=(1,t,t^2,\ldots,t^{d-1}).
\]

For each nonzero kernel row

```text
b_i=(b_i0,...,b_i,d-1),
```

the coordinate

\[
f_i(t)=b_i\cdot\alpha(t)
\]

is a nonzero univariate rational polynomial of degree at most `d-1`. Therefore
it has at most `d-1` real roots.

Across all `n` rows there are at most

```text
n(d-1)
```

bad integer values of `t`. Consequently among the

```text
n(d-1)+1
```

integers

```text
0,1,...,n(d-1)
```

at least one satisfies

```text
f_i(t) != 0 for every i.
```

Search those integers in order and evaluate all dot products exactly. This
constructs a full-support kernel vector

```text
y=B alpha(t)
```

and hence an initial chamber without enumerating any other chamber.

The bit length is polynomial: `t=O(nd)` and the largest power has
`O(d log(nd))` bits before combination with the polynomial-bit rational basis
entries.

Thus:

```text
FULL_SUPPORT_START_TOPE
= DETERMINISTIC POLYNOMIAL.
```

## 3. Projective simplification is polynomial

Two nonzero rows `b_i,b_j` define the same geometric arrangement hyperplane iff
they are nonzero scalar multiples over `Q`.

Exact proportionality can be tested by cross multiplication. Partition the `n`
rows into projective classes and choose one oriented rational representative

```text
h_1,...,h_q,
q<=n.
```

For a full-support coefficient vector `alpha`, record the projective tope sign

```text
sigma_j=sign(h_j dot alpha).
```

Rows antiparallel to the chosen representative carry the corresponding fixed
orientation reversal; this is bookkeeping only and does not change the
distinct geometric hyperplanes.

## 4. Complete neighbor oracle by rational LP

Fix a current tope sign vector

```text
sigma in {+,-}^q.
```

For each projective class `j`, form the sign vector `sigma^(j)` obtained by
flipping exactly coordinate `j`.

Question:

```text
does there exist a chamber with sign sigma^(j)?
```

Write `s_k in {+1,-1}` for the desired sign on class `k`. The strict system is

\[
s_k\,h_k\cdot\alpha>0\quad(k=1,\ldots,q).
\]

Because the system is homogeneous, it is feasible iff the non-strict margin-one
system is feasible:

\[
s_k\,h_k\cdot\alpha\ge1\quad(k=1,\ldots,q).
\]

Proof: a strict feasible point has a positive minimum margin; scale by the
reciprocal of that margin. The reverse implication is immediate.

The margin-one system is an ordinary rational LP feasibility problem with `d`
variables and `q<=n` inequalities. Therefore it is decidable in polynomial time
with polynomial-bit rational certificates/solutions.

Run this LP once for each `j=1,...,q`. Whenever it is feasible, the returned
`alpha_j` realizes a tope differing from the current tope on exactly one
distinct hyperplane. Such a chamber is a facet-neighbor; conversely every
facet-neighbor differs on exactly one projective hyperplane and is found by one
of these tests.

Hence:

\[
\boxed{
\text{the complete chamber neighborhood is enumerable in polynomial time}
}
\]

using at most `q<=n` LP feasibility calls.

This does **not** enumerate all chambers.

## 5. Boundary verification is polynomial

For any returned chamber representative `alpha`, compute

```text
y=B alpha
```

and its positive set

```text
P={i:y_i>0}.
```

The source sign-count theorem guarantees `|P|>=n/3` after choosing the smaller
orientation. If `|P|=n/3`, then the indicator `x=1_P` is automatically an exact
Boolean witness. Directly verify

```text
A x = 1
```

in polynomial time.

Therefore reaching the boundary is a polynomially recognizable terminal.

## 6. Path length is already polynomial

The source-kernel tope graph after projective simplification is a partial cube.
For every known pair of topes `C,D`,

```text
dist(C,D)=# separating projective hyperplanes <= q <= n.
```

Consequently, if the source is SAT and `D` is any boundary tope, then from the
polynomially constructed starting chamber `C_0` there exists a boundary-reaching
facet gallery of length at most `n`.

Thus none of the following can be the remaining source of superpolynomial
runtime inside this representation:

```text
finding a starting chamber,
generating all immediate moves,
checking a boundary endpoint,
minimum required number of moves.
```

## 7. The exact missing oracle

Let

```text
Bdry={D : D is a source-kernel tope with p(D)=n/3}.
```

When `Bdry` is nonempty define

\[
\delta(C)=\min_{D\in Bdry}\operatorname{dist}(C,D).
\]

By the partial-cube theorem,

```text
0<=delta(C)<=q<=n.
```

The complete missing step can be phrased as the following deterministic oracle:

```text
BOUNDARY_DIRECTION(B,C)
```

which must do one of:

```text
if delta(C)=0:
    return BOUNDARY_WITNESS

if Bdry is nonempty and delta(C)>0:
    return a facet-neighbor C' with delta(C')=delta(C)-1

if Bdry is empty:
    return a polynomially verifiable UNSAT certificate
```

If such an oracle is computable in deterministic polynomial time, then the
whole source-kernel shell is a deterministic polynomial solver: construct
`C_0`, call the oracle at most `q<=n` times, and verify the endpoint.

Conversely, a universal polynomial Exact-One solver trivially decides whether
`Bdry` is empty and can reconstruct a target boundary witness, so this gate is
not being advertised as an easier problem by definition. The value of the
normal form is localization: every surrounding navigation operation has now
been removed from the unknown part.

## 8. PG15 finite binding

For the frozen PG15 rational kernel, `d=4`, so the moment-curve search needs at
most

```text
n(d-1)+1=46
```

integer candidates `t=0,...,45`.

Already

```text
t=1,
alpha=(1,1,1,1)
```

is full support. Its antipode

```text
-alpha=(-1,-1,-1,-1)
```

orients the chamber with six positive source coordinates.

For the separate strict local-minimum chamber

```text
alpha_0=(-1,2,2,-2),
p=6,
```

the complete exact facet-neighborhood consists of four chambers, all with
`p=8`, across the projective pair classes

```text
{1,5}, {2,6}, {8,12}, {11,15}.
```

Exact representatives are

```text
flip {1,5}:   (-2,1,4,-2)
flip {2,6}:   (-2,4,1,-2)
flip {8,12}:  ( 1,1,1,-2)
flip {11,15}: (-2,4,4, 1).
```

Every singleton-class flip is impossible by the explicit monochromatic-row
certificates frozen in the monotone-descent barrier. Thus this control makes the
separation visible:

```text
LOCAL NEIGHBOR ENUMERATION = EASY / EXACT,
LOCAL OBJECTIVE DESCENT     = IMPOSSIBLE AT THIS CHAMBER,
GLOBAL CORRECT DIRECTION    = THE HARD PART.
```

## 9. Anti-loop consequences

Freeze:

```text
STARTING_TOPE_CONSTRUCTION_AS_HARDNESS
= CLOSED

FACET_NEIGHBOR_ENUMERATION_AS_HARDNESS
= CLOSED

EXPONENTIAL_SHORTEST_WINNING_PATH_LENGTH
= CLOSED
```

Do not spend future cycles on:
- enumerating all chambers merely to obtain one start chamber;
- generic arrangement traversal to discover immediate neighbors;
- claims that the SAT path may intrinsically need exponentially many facet
  crossings;
- greedy `p` descent, already falsified;
- convex/gated boundary projection, already falsified.

## 10. Sharpened live gate

Freeze

```text
R5_E9_SOURCE_KERNEL_BOUNDARY_DIRECTION_ORACLE_GATE_V2
```

A PASS requires a deterministic polynomial construction which, on every source
instance surviving the admitted terminals, either:

1. produces a neighbor reducing `delta(C)` to the unknown boundary set;
2. jumps by a polynomially describable multi-facet move with a polynomially
   decreasing globally sound potential;
3. emits a polynomially verifiable UNSAT certificate when the boundary set is
   empty;
4. supplies a different complete universal polynomial solver.

Mandatory hostile controls:
- PG15 p=6 strict local minimum with four p=8 neighbors;
- PG15 nonconvex/nongated boundary set;
- singular rank-14 UNSAT depth `6/15` control;
- high-nullity lift families;
- fractional-support closure survivors.

## 11. Ceiling

```text
KERNEL BASIS
= POLY

FULL-RANK / ZERO-ROW / MOD-3 TERMINALS
= POLY

ONE FULL-SUPPORT START TOPE
= POLY BY MOMENT CURVE

PROJECTIVE SIMPLIFICATION
= POLY

COMPLETE FACET NEIGHBORHOOD OF A GIVEN TOPE
= POLY BY <=n RATIONAL LPs

BOUNDARY VERIFICATION
= POLY

SHORTEST SAT-BOUNDARY PATH LENGTH
<= n

GLOBAL BOUNDARY-DIRECTION SELECTION
= OPEN

UNSAT BOUNDARY-EXCLUSION CERTIFICATE
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```