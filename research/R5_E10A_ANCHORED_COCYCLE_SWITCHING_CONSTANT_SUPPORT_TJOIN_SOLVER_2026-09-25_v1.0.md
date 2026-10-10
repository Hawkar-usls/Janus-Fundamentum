# R5 E10A — Anchored Cocycle Switching and Constant-Support T-Join Solver

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_DETERMINISTIC_SOLVER_AFTER_PA0008__CURRENT_DISTINGUISHED_REAL_TORSO_GATE_CLOSED__NO_GLOBAL_P_EQ_NP_CLAIM`

Authorizing audit:
`PA-0008-DISTINGUISHED-REAL-TORSO-4-COCYCLE-SPAN`

Parent gate:
`R5_E10A_DISTINGUISHED_REAL_TORSO_4_COCYCLE_SPAN_CONTRACTION_GATE_V1`

Checker:
`experiments/r5_e10a_anchored_cocycle_support_tjoin_solver.py`

## 1. Frozen input

Let a promised distinguished real torso be represented over `GF(2)` as

```
A = [ B_G
      S   ],
```

where:

- `B_G` is a reduced incidence matrix of an undirected graph `G`;
- `S` has at most two independent signature rows modulo the graphic cut row
  space;
- `f` is the distinguished element;
- the torso satisfies the NM-0012 promise

```
C*(N)
=
span {
  D in C*(N):
  f in D and |D| <= 4
}.
```

Edge weights are nonnegative and polynomially represented.

The aim is exact minimum-weight circuit through `f`, with witness
reconstruction.

## 2. Quotient formulation

Let

```
U = rowspan(B_G)
```

be the graphic cut space and

```
W = C*(N) / U.
```

Because the representation has at most two signature rows,

```
q = dim W <= 2.
```

Let

```
K_f =
{
  D in C*(N):
  f in D,
  |D| <= 4
}.
```

NM-0012 gives

```
span(K_f)=C*(N).
```

Therefore the quotient images of `K_f` span `W`.

If `q=0`, the torso is graphic and the shortest-f circuit is source-bound
graphic shortest-cycle machinery.

If `q=1`, choose one `D_1 in K_f` with nonzero quotient image.

If `q=2`, choose

```
D_1,D_2 in K_f
```

whose quotient images are linearly independent.

For the live rank-two case write

```
chi(D_i) = y_i B_G + alpha_i S,
i=1,2,
```

where `alpha_1,alpha_2 in GF(2)^2` are independent.

## 3. Theorem — ANCHORED_COCYCLE_SUPPORT_SEVEN

Apply the invertible `GL(2,2)` row transformation whose two new signature
coordinates are `alpha_1,alpha_2`.  Then add the cut row `y_i B_G` to
signature row `i`.

These are elementary row operations on the full representation, so the
represented binary matroid is unchanged.

The resulting representation is

```
A' = [ B_G
       chi(D_1)
       chi(D_2) ].
```

Equivalently, in `GF(2)^2` group-labelled language this is a vertex
switching / shifting normalization.

Hence every edge outside

```
F = D_1 union D_2
```

has signature label `00`.

Since both selected cocycles contain `f` and have support at most four,

```
|F|
<=
|D_1|+|D_2|-1
<=
7.
```

Thus:

```
TWO-ROW
+
DISTINGUISHED f-CONTAINING <=4 COCYCLE SPAN
        =>
ROW-EQUIVALENT / SWITCH-EQUIVALENT REPRESENTATION
WITH AT MOST SEVEN NONZERO-LABEL ELEMENTS.
```

For quotient rank one the same proof gives support at most four.

### Algorithmic construction

The normalization is polynomially constructible.

Enumerate all sets

```
{f} union X,
|X| <= 3.
```

There are `O(m^3)` candidates.  Test cocycle-space membership by Gaussian
elimination and compute each candidate's class modulo `U`.  Since the
promise says these candidates span the full cocycle space, they contain a
quotient basis.  Select one or two such cocycles and perform the row
operations above.

No hidden search over exponentially many gauges is used.

## 4. Source binding for switching

Vertex shifting/switching is standard group-labelled graph machinery.
For an abelian group it changes edge labels by vertex potentials while
preserving closed-walk labels; in matrix language the same operation is
addition of incidence/cut rows to signature rows.

Joglekar--Shah--Diwan,
*Balanced group-labeled graphs*,
Discrete Mathematics 312 (2012), 1542--1549,
DOI 10.1016/j.disc.2011.09.021,
source-binds the switching language.

Kawase--Kobayashi--Yamaguchi likewise use shifting as standard machinery in
prescribed/forbidden-label path theory.

The JANUS contribution here is **not** switching itself.  It is the derivation
of the constant support bound from the NM-0012 anchored cocycle-span promise.

## 5. Cycle formulation of shortest-f

A binary cycle is a disjoint union of circuits.

Therefore, with nonnegative weights,

```
shortest_f(N)
=
min {
  w(X):
  X is a binary cycle of N,
  f in X
}.
```

Indeed, every feasible cycle `X` containing `f` decomposes into disjoint
circuits and exactly one component circuit contains `f`; that circuit has
weight at most `w(X)`.

In the normalized two-row representation a set `X` is a binary cycle iff

```
partial_G(X)=empty
```

and

```
XOR_{e in X} lambda(e)=00.
```

All nonzero labels lie in `F`, with `|F|<=7`.

## 6. Exact constant-support reduction to ordinary T-join

For every subset

```
R subseteq F
```

such that

```
f in R
```

and

```
XOR_{e in R} lambda(e)=00,
```

define

```
T_R = partial_G(R),
```

the set of vertices of odd degree in `R`.

Every remaining edge in

```
E(G)-F
```

has zero group label.  Hence an edge set

```
Y subseteq E(G)-F
```

completes `R` to a binary cycle exactly when

```
partial_G(Y)=T_R.
```

That is, `Y` is an ordinary `T_R`-join in `G-F`.

Conversely every binary cycle through `f` has a unique exceptional part

```
R = X intersect F
```

and its zero-label remainder is exactly such a `T_R`-join.

Therefore:

```
shortest_f(N)
=
min over
R subseteq F,
f in R,
lambda(R)=00

[
  w(R)
  +
  tau_{G-F}(partial R)
],
```

where `tau_H(T)` is the minimum weight of a `T`-join in `H`.

This equality is exact.

## 7. Polynomial running time

There are at most

```
2^7 = 128
```

exceptional subsets.

Moreover,

```
|T_R| <= 2|R| <= 14.
```

Minimum-weight `T`-join in an undirected graph with nonnegative weights is
classical deterministic polynomial machinery: compute shortest-path distances
between terminals and solve minimum perfect matching in the terminal metric.

Here the terminal set is even bounded by 14, so the matching step can instead
be done by a constant-size subset pairing DP.

Thus the full algorithm is deterministic polynomial time:

```
O(m^3 * poly(m))
+
128 * poly(|V|+|E|).
```

The displayed bound is intentionally coarse; polynomiality is the theorem-level
claim.

## 8. Witness reconstruction

For the minimizing subset `R`, reconstruct the minimum `T_R`-join `Y`.

Then

```
X=R union Y
```

is a binary cycle containing `f`.

To extract a circuit witness, take a maximal independent subset `B` of
`X-{f}`.  Since `X` is a cycle containing `f`, the distinguished element
is in `span(B)`.  Its fundamental circuit with respect to `B` is contained
in

```
B union {f} subseteq X
```

and therefore has weight no larger than `X`.

By optimality it has exactly the shortest-f value.

Everything is reconstructible by Gaussian elimination plus the ordinary
T-join witness.

## 9. Finite controls

The checker contains two independent controls.

### C1 — hidden-gauge normalization

A finite two-row multigraph instance is built with a full anchored
support-at-most-four cocycle spanning family.  The two small quotient-basis
cocycles are hidden behind:

- an invertible `GL(2,2)` signature transformation;
- additions of graphic cut rows.

The checker re-enumerates all small distinguished cocycles, finds two
quotient-independent members, and verifies that replacing the signature rows
by them preserves the full row space and leaves support at most seven.

### C2 — solver vs exhaustive cycle search

On deterministic random small labelled graphs with nonnegative weights and
signature support at most six, the checker compares:

1. exhaustive minimum binary-cycle cost through `f`;
2. the constant exceptional-subset + ordinary `T`-join algorithm.

The values must agree exactly on every instance.

## 10. Anti-loop correction

A tempting interpretation after the support-seven theorem is:

```
"enumerate exceptional edges,
then solve a shortest simple path through them"
```

which appears to lead toward shortest fixed-linkage / disjoint-path
optimization.

That route is unnecessary and would reopen a harder neighboring problem.

The authoritative object is a **shortest binary circuit through f**.
Passing through the binary cycle space first preserves the exact optimum and
turns the zero-label remainder into an ordinary T-join.

Freeze:

```
CONSTANT LABEL SUPPORT
-> SIMPLE-PATH / DISJOINT-PATH ORDER ENUMERATION
=
DO NOT USE

CONSTANT LABEL SUPPORT
-> BINARY CYCLE
-> ORDINARY T-JOIN
=
EXACT
```

## 11. Source binding for T-joins

Edmonds--Johnson minimum-weight T-join machinery is standard.
For nonnegative edge weights, one computes shortest-path distances among the
vertices of `T`, solves minimum perfect matching in that metric, and maps the
matching edges back to paths.

This step is source-bound and is not claimed as new JANUS mathematics.

## 12. Gate verdict

```
R5_E10A_DISTINGUISHED_REAL_TORSO_4_COCYCLE_SPAN_CONTRACTION_GATE_V1
=
PASS_DETERMINISTIC_POLYNOMIAL_SOLVER
```

More explicitly:

```
ANCHORED <=4 COCYCLE SPAN
+
TWO-ROW LIFT
        ->
SIGNATURE SUPPORT <=7
        ->
<=128 ORDINARY T-JOIN INSTANCES
        ->
DETERMINISTIC POLYNOMIAL shortest-f
        +
POLYNOMIAL WITNESS RECONSTRUCTION.
```

This is stronger than a strict contraction: it closes the current
**distinguished real-torso** optimization gate outright.

## 13. What this does not yet prove

This artifact does **not** prove a polynomial algorithm for the full original
cubic exact-one problem and does not prove `P=NP`.

The old E10 firewall remains relevant: an S8-containing decomposition component
need not itself contain the original distinguished element `f`; its influence
may enter the distinguished side through virtual 2/3-sum separator elements.

NM-0012 and the theorem above solve the real torso that retains `f`.
They do not yet prove that every non-distinguished child/interface receives an
equivalent anchored bounded-support promise after virtual elements are added.

That is a changed scope and must be source-audited before new mathematics.

Freeze next required audit:

```
PA-0009
CUBIC-ORIGIN NONDISTINGUISHED-TORSO /
VIRTUAL-INTERFACE PROPAGATION SOURCE AUDIT
```

Primary question:

```
Does the punctured NM-0010 star-cocycle family
force an equally bounded-support normal form
for every non-f real torso together with
the <=3 virtual elements of one rooted 2/3-sum interface,
or is there a known decomposition obstruction/algorithm
that already settles this?
```

Do not extrapolate the current distinguished solver across that interface
without this audit.

## 14. Scientific ceiling

```
NM-0012 DISTINGUISHED 4-COCYCLE-SPAN PROMISE
=
USED EXACTLY

SUPPORT <=7 NORMAL FORM
=
PROVED

CONSTANT-SUPPORT -> T-JOIN FORMULA
=
PROVED

CURRENT DISTINGUISHED REAL-TORSO shortest-f
=
DETERMINISTIC POLYNOMIAL

FULL CUBIC DECOMPOSITION
=
NOT YET CLOSED

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
