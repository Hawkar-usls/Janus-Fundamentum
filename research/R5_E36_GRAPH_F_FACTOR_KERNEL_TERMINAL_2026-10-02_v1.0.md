# R5 E36 — Graph-Incidence / f-Factor Kernel Terminal

Date: 2026-10-02

Status:
`EXACT_NON_TU_GRAPH_KERNEL_POLYNOMIAL_TERMINAL__F_FACTOR_REDUCTION__NON_TU_NOT_HARDNESS`

Scientific ceiling:

```text
THIS NOTE EXTENDS THE POST-E33 GLOBAL-KERNEL ROUTER BEYOND TOTALLY
UNIMODULAR REPRESENTATIONS.

LET R BE THE 0/1 VERTEX-EDGE INCIDENCE MATRIX OF AN UNDIRECTED GRAPH H.
SUCH R IS GENERALLY NOT TU WHEN H CONTAINS AN ODD CYCLE.

IF
  ker_Q(R)=ker_Q(A),
THEN EXACT-ONE IS EQUIVALENT TO THE f-FACTOR PROBLEM

  deg_F(v)=deg_H(v)/3

ON H.

THE f-FACTOR PROBLEM IS POLYNOMIAL.

THEREFORE GENUINELY NON-TU KERNEL LANGUAGES CAN STILL BE EXACTLY TRACTABLE.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
H=(V,E)
```

be an undirected graph with

```text
E=[n].
```

Let

```text
R in {0,1}^{V x E}
```

be its ordinary unsigned vertex-edge incidence matrix:

```text
R_ve=1
```

iff edge `e` is incident with vertex `v`.

Assume

```text
boxed:
ker_Q(R)=ker_Q(A).
```

As before, Exact-One is equivalent to finding

```text
y=3x-1,
x in {0,1}^E,
y in ker_Q(R).
```

## 2. Vertex equations

For a vertex `v`, the `v`th row of

```text
R(3x-1)=0
```

is

```text
3 sum_{e incident v} x_e - deg_H(v)=0.
```

Therefore every Exact-One witness satisfies

```text
boxed:
deg_x(v)=deg_H(v)/3.
```

In particular a necessary condition is

```text
deg_H(v) == 0 mod 3
```

for every vertex.

## 3. Converse

Suppose a subset of edges

```text
F subseteq E
```

satisfies

```text
deg_F(v)=deg_H(v)/3
```

for every vertex.

Let `x` be its incidence vector. Then

```text
R x = (R1)/3.
```

Hence

```text
R(3x-1)=0,
```

so

```text
3x-1 in ker_Q(R)=ker_Q(A).
```

Using `A1=3 1`, as usual,

```text
A x=1.
```

Thus every such factor is an Exact-One witness.

## 4. Exact f-factor equivalence

Define

```text
f(v)=deg_H(v)/3.
```

When every degree is divisible by three, the condition

```text
deg_F(v)=f(v)
```

is exactly the classical **f-factor problem**.

Therefore:

### Theorem GRAPH-F-FACTOR-KERNEL

```text
boxed:
If ker_Q(A)=ker_Q(R_H) where R_H is the unsigned vertex-edge incidence
matrix of an undirected graph H, then

A is Exact-One SAT
iff
H has an f-factor with f(v)=deg_H(v)/3.
```

The f-factor problem is solvable in deterministic polynomial time by the standard
matching / factor machinery.

Hence this entire kernel language is polynomial.

## 5. Why this is genuinely beyond TU

Unsigned graph incidence matrices are not generally totally unimodular.

For a triangle, the full incidence matrix is

```text
[1 0 1]
[1 1 0]
[0 1 1]
```

with determinant

```text
-2.
```

Thus the E33 TU theorem does not apply to this representation.

Nevertheless E36 solves the kernel language exactly through f-factors.

Therefore

```text
boxed:
NON-TU DOES NOT IMPLY HARD.
```

The post-E33 frontier must be refined beyond regularity alone.

## 6. Cubic special case

If `H` is cubic, then

```text
f(v)=1
```

for every vertex.

The kernel Exact-One problem becomes

```text
Does H have a perfect matching?
```

which is polynomial.

So any source whose orthogonal kernel representation is the unsigned incidence
matrix of a cubic graph is exactly solvable by perfect matching.

## 7. Divisibility is not sufficient

Unlike the TU sector, degree divisibility alone does not guarantee SAT.

The companion checker includes a cubic graph built from one central vertex joined
by three bridges to three subdivided-K4 gadgets.

Every vertex has degree three, so

```text
deg(v)/3=1
```

is integral everywhere.

But removing the central vertex leaves three odd connected components.  Tutte's
condition therefore fails, so the graph has no perfect matching.

Thus E36 genuinely needs the polynomial f-factor solver; it is not merely another
mod-3 divisibility test.

## 8. SAT and UNSAT certificates

For SAT, an f-factor itself is the Boolean witness.

For UNSAT, the underlying matching / f-factor algorithm can return the standard
dual / blossom / Tutte-type obstruction used by the factor solver.

Once the graph representation `H` and kernel equality are verified, witness checking
is polynomial.

## 9. Relation to E32 and E33

The global kernel-language branches now include:

```text
E32 root/tension space:
  mod-3 vertex-potential propagation.

E33 TU orthogonal space:
  integral LP / modular criterion.

E36 unsigned graph-incidence space:
  f-factor / matching.
```

E36 is important because its representation may contain determinant-2 odd-cycle
minors and therefore lie outside the TU branch while remaining polynomial.

## 10. Wider graph-factor form

The proof uses only that each column of `R` is the incidence vector of one graph
edge and each selected Boolean variable contributes one unit to both endpoints.

Thus the same reduction applies componentwise to multigraphs as well, with parallel
edges treated as distinct source coordinates.

Loops require a separate convention and are excluded here.

## 11. Updated universal frontier

After E36, a genuine integer-feasible UNSAT hard core must avoid all currently known
global kernel languages:

```text
TU / regular orthogonal representations,
root/tension graph potentials,
flow/circulation network spaces,
unsigned graph-incidence f-factor spaces,
small distance-to-TU backdoors,
low projective quotient width,
commuting / near-commuting normal forms,
and bounded-interface decompositions.
```

So `non-TU` is only the beginning of the remaining frontier.

The next natural generalization is a **signed / bidirected graph kernel** where
columns may have endpoint signs

```text
(+,+),
(+,-),
(-,+),
(-,-).
```

Those systems interpolate between ordinary flow and f-factor languages and may
admit another polynomial factor / bidirected-flow reduction.

That is the next exact-language target.

```text
P_VS_NP = OPEN.
```

Companion finite controls:

```text
experiments/r5_e36_graph_f_factor_kernel.py
```
