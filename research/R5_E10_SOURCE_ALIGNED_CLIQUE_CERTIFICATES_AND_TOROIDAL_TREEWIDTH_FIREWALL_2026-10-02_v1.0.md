# R5 E10 — Source-Aligned Clique Certificates and Toroidal Treewidth Firewall

Date: 2026-10-02

Status:
`EXACT_NEW_CERTIFICATE_FAMILY__TREEWIDTH_ROUTE_FIREWALLED__UNIVERSAL_ALGORITHM_NOT_YET_PROVED`

Scientific ceiling:

```text
THIS NOTE ADDS A POLYNOMIALLY VERIFIABLE UNSAT CERTIFICATE FAMILY,
AN EXACT O(2^d poly(n)) RATIONAL-NULLITY TERMINAL,
AND AN INFINITE FAMILY OF SQUARE CUBIC LINEAR INSTANCES WITH UNBOUNDED PRIMAL TREEWIDTH.

IT DOES NOT PROVE A POLYNOMIAL-TIME ALGORITHM FOR ALL INSTANCES.
P_VS_NP = OPEN.
```

## 1. Source setting

Let

```text
A in {0,1}^{m x n}
```

have exactly three ones in every row.  An Exact-One witness is

```text
x in {0,1}^n,   A x = 1
```

over the integers.

Define the conflict graph `G_A` on the columns of `A`: distinct columns `u,v` are adjacent iff some row of `A` contains both columns.  Every Exact-One witness is an independent set of `G_A`.

When the source is square/cubic/linear, every row and every column has weight three and any two rows meet in at most one column.  Then

```text
A^T A = 3 I + Adj(G_A).
```

Consequently

```text
nullity_Q(A) = multiplicity of eigenvalue -3 of G_A,
```

and every eigenvalue of `G_A` is at least `-3`.

## 2. Exact rational-nullity terminal

Let

```text
d = nullity_Q(A).
```

Because every row has weight three,

```text
A (1/3 * 1) = 1.
```

Thus every rational solution of `A x = 1` is

```text
x = 1/3 * 1 + z,   z in ker_Q(A).
```

Equivalently, putting

```text
y = 3x - 1,
```

we obtain the exact equivalence

```text
A x = 1, x in {0,1}^n
iff
A y = 0, y in {-1,2}^n.
```

Choose `d` free coordinates after rational row reduction.  Every Boolean solution is uniquely determined by the `2^d` assignments to the free coordinates; the pivot coordinates are then rationally forced and can be tested for membership in `{0,1}`.

Therefore Exact-One is decidable in

```text
O(2^d poly(n))
```

exact arithmetic.

This is a fixed-parameter terminal in rational nullity.  It is not polynomial in the worst case unless `d = O(log n)` or another structural branch handles large `d`.

### Frozen PG15 controls

Using the matrices in the existing R5 E9 exact checker:

```text
PG15_SAT:
  rank_Q(A)    = 11
  nullity_Q(A) = 4
  exact-one witnesses = 4

PG15_UNSAT:
  rank_Q(A)    = 14
  nullity_Q(A) = 1
  exact-one witnesses = 0
```

Hence both hostile size-15 controls terminate immediately under the rational-nullity branch: at most `16` and `2` free-coordinate assignments, respectively.

For `PG15_UNSAT`, a primitive generator of the rational kernel is

```text
z = (1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

Since every Boolean witness would require a nonzero scalar multiple of `z` to lie in `{-1,2}^15`, and the coordinate ratios make this impossible, the one-dimensional kernel itself gives a short exact UNSAT proof.

## 3. Source-aligned subset identity

Let `U` be a subset of columns and suppose its indicator is in the rational row space:

```text
1_U = A^T lambda
```

for some `lambda in Q^m`.

Then every Exact-One witness satisfies

```text
x(U) = |U|/3.
```

Proof:

```text
x(U)
= 1_U^T x
= lambda^T A x
= lambda^T 1.
```

Also, since `A 1 = 3 1`,

```text
|U|
= 1_U^T 1
= lambda^T A 1
= 3 lambda^T 1.
```

Hence `lambda^T 1 = |U|/3` and therefore `x(U)=|U|/3`.

This identity is exact over `Q` and is polynomially verifiable by Gaussian elimination.

## 4. Source-aligned clique-cover UNSAT certificate

Because every Exact-One witness is independent in `G_A`, if `G_A[U]` is covered by `q` cliques then

```text
x(U) <= q.
```

Combining with the source-aligned identity yields:

### Theorem SA-CLIQUE

If

```text
1_U in row_Q(A)
```

and `G_A[U]` has a clique cover with

```text
q < |U|/3,
```

then `A` is Exact-One UNSAT.

A certificate consists only of:

1. the subset `U`;
2. a rational (or scaled integer) vector proving `1_U in row_Q(A)`;
3. the clique cover of `G_A[U]`.

All three parts are polynomially checkable.

This theorem is a certificate family, not yet a polynomial search theorem for finding such a `U` and clique cover on every UNSAT source.

## 5. PG15_UNSAT local certificate

For the frozen singular UNSAT control, take

```text
U = V \ {2,6,11}.
```

Then `|U|=12` and `G_A[U]` is covered by three disjoint `K4` cliques:

```text
{1,7,9,13}
{3,8,10,15}
{4,5,12,14}
```

so every independent set obeys

```text
x(U) <= 3.
```

A scaled integer row-space certificate is

```text
c = (9,5,8,10,6,-18,11,3,13,6,8,9,2,4,0)
```

with

```text
A^T c = 19 * 1_U
sum(c) = 76.
```

Thus every Exact-One witness would satisfy

```text
19 x(U) = c^T A x = sum(c) = 76,
```

hence

```text
x(U)=4.
```

But the clique cover gives `x(U)<=3`.  Contradiction:

```text
4 = x(U) <= 3.
```

This is a compact exact local UNSAT certificate independent of stable-set facet machinery.

## 6. Treewidth firewall: the bounded-treewidth donor is false

A 2025 paper by Omar Kettani proposes a polynomial algorithm for Cubic Monotone 1-in-3 SAT by claiming that the associated conflict graph has treewidth at most six under the conditions

```text
maximum degree <= 6,
no induced K_{1,4},
each vertex belongs to at least three triangles.
```

The proposed proof contains invalid implications.  Two direct examples:

1. A vertex being simplicial in `G[C]` does not imply that the triangles containing it in the full graph `G` lie inside `C`.
2. A separator in the induced subgraph `G[C]` need not separate the same two vertices in the full graph `G`; a path may leave `C`.

More importantly, the bounded-treewidth conclusion is false even for actual square cubic linear Exact-One conflict graphs, as shown by the explicit family below.

Reference checked:

```text
Omar Kettani,
"Cubic Monotone 1-in-3 SAT Problem is Polynomial Time Solvable",
International Journal of Mathematics Trends and Technology 71(9), 2025,
DOI 10.14445/22315373/IJMTT-V71I9P105.
```

Therefore this route is retained only as an anti-loop / negative-control source, not as a theorem donor.

## 7. Infinite toroidal square+cubic+linear family

For integer `k >= 3`, let the variables be

```text
x_{i,j},   i,j in Z_k,
```

and define one clause for every `(i,j)`:

```text
C_{i,j} = { x_{i,j}, x_{i+1,j}, x_{i,j+1} }.
```

All indices are modulo `k`.

Call the resulting incidence matrix `A_k`.

### Structural properties

There are exactly `k^2` variables and `k^2` clauses.

Every clause has size three.

Every variable `x_{a,b}` occurs in exactly the three clauses

```text
C_{a,b}, C_{a-1,b}, C_{a,b-1}.
```

Hence `A_k` is square and cubic.

For `k>=3`, two distinct clauses share at most one variable, so the family is linear.

The conflict graph contains every horizontal and vertical torus edge

```text
x_{i,j} -- x_{i+1,j}
x_{i,j} -- x_{i,j+1}.
```

Therefore it contains `C_k square C_k` as a spanning subgraph.  Since the toroidal grid contains a `k x k` planar grid as a subgraph after deleting wrap-around edges,

```text
tw(G_{A_k}) >= k.
```

Thus the conflict graphs of square+cubic+linear Exact-One instances have unbounded treewidth.

This directly kills any universal bounded-treewidth route for the source class.

## 8. Exact SAT/UNSAT classification of the toroidal family

The family is nevertheless exactly solvable, and therefore makes an excellent high-treewidth stress control.

Let

```text
R_i = sum_j x_{i,j}.
```

Summing all `k` clause equations with fixed first index `i` gives

```text
2 R_i + R_{i+1} = k.
```

Hence

```text
R_{i+1} = k - 2 R_i.
```

Writing

```text
S_i = R_i - k/3,
```

we get

```text
S_{i+1} = -2 S_i.
```

After one trip around the torus,

```text
S_i = (-2)^k S_i.
```

Since `(-2)^k != 1` for positive `k`, necessarily `S_i=0`, so every row sum must equal

```text
R_i = k/3.
```

Because `R_i` is an integer, a necessary condition is

```text
3 | k.
```

It is also sufficient.  If `3 | k`, set

```text
x_{i,j}=1  iff  i-j == 0 (mod 3).
```

Each clause contains residues `r, r+1, r-1` modulo three and therefore exactly one selected variable.

Thus

```text
A_k is Exact-One SAT  iff  3 divides k.
```

This gives both SAT and UNSAT instances with arbitrarily large treewidth.

## 9. Spectral form of the toroidal family

For the linear family,

```text
A_k^T A_k = 3I + Adj(G_{A_k}).
```

The toroidal matrices are block-circulant.  Their Fourier eigenvalues are

```text
1 + omega^a + omega^b,
```

where `omega` ranges over the `k`th roots of unity.

A zero eigenvalue occurs exactly when `{1,omega^a,omega^b}` are the three cube roots of unity.  Therefore over characteristic zero:

```text
nullity_Q(A_k) = 2  if 3 | k,
nullity_Q(A_k) = 0  otherwise.
```

So this family simultaneously demonstrates:

```text
unbounded treewidth does NOT imply large rational nullity,
```

and the rational-nullity terminal solves these high-treewidth controls immediately.

This is useful for the desired dichotomy: treewidth and rational nullity are genuinely different axes and should not be conflated.

## 10. Literature firewall around the linear/regular frontier

Porschen--Schmidt--Speckenmeyer--Wotzlaw prove NP-completeness for several linear and regular XSAT classes.  In particular they prove NP-completeness for monotone linear `l`-regular formulas in broad clause-size classes, and for `l`-uniform `l`-regular linear formulas when `l=q+1` via a projective-plane construction, but that latter construction uses negated backbone variables and therefore must not be silently cited as hardness of the fully monotone `3-uniform + 3-regular + linear` subclass.

Reference:

```text
S. Porschen, T. Schmidt, E. Speckenmeyer, A. Wotzlaw,
"XSAT and NAE-SAT of linear CNF classes",
Discrete Applied Mathematics 167 (2014), 1-14,
preprint 2011.
```

Governance rule:

```text
DO NOT PROMOTE hardness of the fully monotone square+cubic+linear subclass
without an explicit reduction preserving all four properties.
```

The universal Cubic Monotone 1-in-3 SAT source itself remains NP-complete; solving it in deterministic polynomial time would suffice for `P=NP`.

## 11. New frontier

The treewidth shortcut is dead, but the rational-nullity and source-aligned-certificate routes survive.

The next universal target is now precise:

```text
Given square cubic (preferably linear) A,
let d = nullity_Q(A).

SMALL d:
  exact O(2^d poly(n)) terminal.

LARGE d:
  exploit the large -3 eigenspace of G_A to force
  either
    (a) a polynomially detectable source-aligned clique/fractional-clique obstruction,
    (b) a decomposition into smaller independent source components,
    (c) a constructive Boolean kernel vector y in {-1,2}^n,
  or another polynomial terminal.
```

For linear sources the identity

```text
A^T A = 3I + Adj(G_A)
```

turns the large-nullity branch into the graph-spectral problem:

```text
large multiplicity of eigenvalue -3
inside a 6-regular graph whose edges are partitioned into source triangles.
```

This is the highest-value next attack surface.

## 12. Global verdict

```text
NEW EXACT RESULTS:
  rational-nullity FPT terminal;
  source-aligned clique-cover UNSAT theorem;
  explicit PG15_UNSAT local certificate;
  toroidal square+cubic+linear family with unbounded treewidth;
  exact SAT iff 3|k classification for that family;
  nullity 0/2 spectral classification for that family.

ROUTE KILLED:
  universal bounded-treewidth claim for cubic monotone associated graphs.

UNRESOLVED:
  polynomial handling of arbitrary large rational nullity / large (-3)-eigenspace.

P_VS_NP = OPEN.
```
