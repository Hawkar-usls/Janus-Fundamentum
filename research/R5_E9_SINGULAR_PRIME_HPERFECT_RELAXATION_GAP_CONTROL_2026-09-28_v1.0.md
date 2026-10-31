# R5 E9 — Singular Prime h-Perfect Relaxation Gap Control

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_SOURCE_VALID_POLYHEDRAL_COUNTERCONTROL__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS IS AN EXPLICIT LINEAR-CUBIC EXACT-ONE UNSAT CONTROL INSIDE THE
SINGULAR / NONTRIVIAL-<=3-CUT-IRREDUCIBLE RESIDUAL.

ITS CONFLICT GRAPH HAS omega=3 AND alpha=4, BUT THE FULL h-PERFECT
RELAXATION (NONNEGATIVITY + ALL CLIQUE + ALL INDUCED ODD-HOLE
INEQUALITIES) HAS OPTIMUM 5=n/3.

THEREFORE CLIQUE + ODD-HOLE CUTS, EVEN TAKEN ALL AT ONCE, DO NOT GIVE
A UNIVERSAL EXACT POLYHEDRAL SOLVER FOR THE JANUS CARRIER.

THIS IS NOT A LOWER BOUND FOR SAT OR FOR GENERAL EXTENDED FORMULATIONS.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen 15_3 instance

Let A be the 15 x 15 incidence matrix with row supports

```text
(0,6,9)
(1,2,12)
(2,4,11)
(1,3,13)
(3,4,10)
(0,5,12)
(6,8,13)
(5,7,10)
(4,8,9)
(1,7,9)
(8,10,14)
(3,7,11)
(6,11,12)
(5,13,14)
(0,2,14)
```

Every row has weight three. Every column has weight three. Any two distinct
rows meet in at most one column. Hence this is a square linear cubic Exact-One
carrier.

Its Levi graph is connected.

Exact rational elimination gives

```text
rank_Q(A)=14,
nu_Q(A)=1.
```

So this control survives the full-rank UNSAT terminal.

## 2. Exact UNSAT / conflict-graph independence number

Let G be the conflict graph on the 15 columns: two columns are adjacent iff they
occur together in a source row.

For every Boolean Exact-One witness x, the selected column set S is independent
in G and, because every selected column covers exactly three source rows while
every source row must be covered once,

```text
|S|=15/3=5.
```

Exact enumeration of all independent subsets gives

```text
alpha(G)=4.
```

For example `{2,3,5,6}` is independent, so alpha(G)>=4; exhaustive checking of
all 5-subsets shows no independent 5-set exists.

Therefore

```text
A is Boolean Exact-One UNSAT.
```

The checker performs the finite exhaustive verification; the mathematical
implication `alpha(G)<5 => UNSAT` is exact.

## 3. No nontrivial <=3-edge separator

The bipartite Levi graph has 30 vertices and 45 edges and exact edge
connectivity three.

The exact cut census is

```text
1-edge cuts: 0
2-edge cuts: 0
3-edge cuts: 30
```

Every 3-edge cut is the star of one cubic Levi vertex and isolates exactly that
single vertex. There is no nontrivial edge cut of size at most three.

Thus the instance survives the admitted exact <=3-edge separator router.

## 4. Clique number

Exact maximal-clique enumeration gives

```text
omega(G)=3.
```

The 15 source rows themselves induce triangles in G, and there is no clique of
size four.

Consequently the uniform point

\[
x^* = \frac13\mathbf 1
\]

satisfies every clique inequality

\[
\sum_{v\in K}x_v\le1
\]

because every clique has size at most three.

## 5. Every odd-hole inequality also accepts x*=1/3

For an induced odd cycle C of length `|C|=2r+1>=5`, the h-perfect odd-hole
inequality is

\[
\sum_{v\in C}x_v\le r=\frac{|C|-1}{2}.
\]

At x*=1/3 the left side is `|C|/3`. For every odd `|C|>=5`,

\[
\frac{|C|}{3}\le\frac{|C|-1}{2}
\]

because `2|C| <= 3|C|-3` iff `|C|>=3`.

Hence x* satisfies **every** induced odd-hole inequality without needing an
odd-hole census.

Nonnegativity is immediate.

## 6. Exact h-perfect-relaxation optimum

Every source row is a triangle clique. Summing the 15 corresponding clique
inequalities gives

\[
3\sum_{v=0}^{14}x_v\le 15
\]

because every conflict-graph vertex belongs to exactly three source-row
triangles. Therefore every point of the clique relaxation obeys

\[
\sum_v x_v\le5.
\]

The uniform point x*=1/3 has objective exactly five and, by Sections 4--5,
satisfies nonnegativity, all clique inequalities, and all induced odd-hole
inequalities.

Thus the complete h-perfect relaxation has exact optimum

\[
\boxed{\alpha_h(G)=5}
\]

while

\[
\boxed{\alpha(G)=4}.
\]

So G is not h-perfect.

## 7. Consequence for the current polyhedral lane

The tempting universal rule

```text
conflict graph G
+ all clique inequalities
+ all induced odd-hole inequalities
-> exact stable-set polytope
-> polynomial target test alpha(G)>=n/3
```

is false already on a connected linear cubic singular 3-cut-prime source-valid
instance.

This is stronger than the earlier denominator-13 warning: here the failure is
stated directly in the exact conflict-graph objective used by the Hoffman /
independent-set route.

A surviving polyhedral proposal must therefore supply a genuinely stronger
global facet family together with polynomial exact separation/optimization; it
may not count clique/odd-hole closure alone as progress.

This result does not rule out:

- other extended formulations;
- source-specific global cuts beyond h-perfect inequalities;
- nonlinear or representation-changing polynomial algorithms;
- P=NP by another route.

## 8. External source boundary

The term `h-perfect` is used in its standard sense: the stable-set polytope is
described by nonnegativity, clique inequalities, and induced odd-hole
inequalities. Classical line-graph polyhedral work shows that h-perfection is a
special structural property, not an automatic property of all line graphs.
The JANUS conflict graph is a line graph of a linear 3-uniform hypergraph, not
an ordinary graph line graph, so no ordinary-line-graph h-perfection theorem is
imported.

## 9. Anti-loop freeze

```text
SINGULAR SOURCE-VALID CONTROL
= rank_Q(A)=14 / nullity_Q(A)=1

NONTRIVIAL <=3-EDGE CUTS
= NONE

CONFLICT CLIQUE NUMBER
= 3

TRUE INDEPENDENCE NUMBER
= 4

EXACT-ONE TARGET
= 5

FULL h-PERFECT RELAXATION OPTIMUM
= 5

CLIQUE + ALL ODD-HOLE POLYHEDRAL TERMINAL
= FALSIFIED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
