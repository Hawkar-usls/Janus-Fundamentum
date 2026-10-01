# R5 E15 — Hoffman-Tight Coclique / Perfect-2-Coloring Equivalence

Date: 2026-10-02

Status:
`EXACT_SPECTRAL_EQUIVALENCE__HARD_CORE_RENAMED_WITHOUT_LOSS__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE IDENTIFIES SQUARE+CUBIC+LINEAR EXACT-ONE EXACTLY WITH
HOFFMAN-TIGHT INDEPENDENT SETS / (0,3)-REGULAR SETS / PERFECT 2-COLORINGS
IN THE ASSOCIATED 6-REGULAR POINT GRAPH.

IT DOES NOT GIVE A POLYNOMIAL ALGORITHM FOR FINDING SUCH A SET.
THE CLASS IS NP-COMPLETE BY R5 E12.
P_VS_NP = OPEN.
```

## 1. Source class

Let

```text
A in {0,1}^{n x n}
```

satisfy

```text
every row has weight 3,
every column has weight 3,
any two distinct rows overlap in at most one column.
```

Let `G=G_A` be the conflict / point graph on the columns of `A`: two columns are adjacent iff some source row contains both.

Because every variable lies in three source rows and linearity prevents the two co-variables from repeating, every vertex has exactly six distinct neighbors.  Thus

```text
G is 6-regular.
```

Each source row induces a triangle of `G`, and the edges of `G` are partitioned by these source triangles.

## 2. Gram identity and spectral floor

For columns `u,v`,

```text
(A^T A)_{uu}=3,
(A^T A)_{uv}=1 iff uv is an edge of G,
(A^T A)_{uv}=0 otherwise.
```

Hence

```text
A^T A = 3I + Adj(G).
```

Since `A^T A` is positive semidefinite,

```text
lambda_min(G) >= -3.
```

Moreover

```text
ker_Q(A) = eigenspace_{-3}(G)
```

over characteristic zero, and

```text
nullity_Q(A) = multiplicity_G(-3).
```

Thus the R5 rational-nullity parameter is exactly the multiplicity of the least permitted point-graph eigenvalue.

## 3. Exact-One witnesses are independent sets of size n/3

Let `x in {0,1}^n` satisfy

```text
A x = 1.
```

No source triangle can contain two selected vertices, so

```text
S={v:x_v=1}
```

is an independent set of `G`.

Summing all source equations gives

```text
1^T A x = n.
```

Every column of `A` has weight three, hence

```text
3 |S| = n,
```

so

```text
|S|=n/3.
```

Conversely, let `S` be any independent set of `G` with `|S|=n/3`.
Every source triangle contains at most one vertex of `S`.  Counting incidences between selected vertices and source rows gives

```text
3|S|=n.
```

There are exactly `n` source rows, each containing at most one selected vertex, so every source row must contain exactly one selected vertex.  Therefore its indicator vector satisfies

```text
A 1_S = 1.
```

Hence

```text
boxed:
A is Exact-One SAT
iff
G_A has an independent set of size n/3.
```

## 4. Hoffman ratio bound becomes exact

For a `k`-regular graph on `n` vertices with least eigenvalue `tau<0`, the Hoffman ratio bound gives

```text
alpha(G) <= n * (-tau)/(k-tau).
```

Here `k=6` and `tau>=-3`.
The right-hand side is monotone decreasing as `tau` increases from `-3`, so

```text
alpha(G) <= n/3.
```

If `tau>-3`, then in fact

```text
alpha(G) < n/3,
```

and the source is immediately UNSAT.  This is the same full-rank terminal as R5 E10/E11, now seen spectrally.

If `tau=-3`, then

```text
alpha(G) <= n/3,
```

and by Section 3 the source is SAT exactly when the Hoffman bound is attained.

Therefore

```text
boxed:
Exact-One SAT
iff
G_A has a Hoffman-tight coclique.
```

## 5. Equality case = perfect 2-coloring

The equality case of the Hoffman bound says that if an independent set `S` attains the ratio bound, the partition

```text
S | V\S
```

is equitable and every vertex outside `S` has exactly `-tau` neighbors in `S`.

With `k=6` and `tau=-3`, every vertex in `S` has zero neighbors in `S` and therefore six outside, while every vertex outside has exactly three neighbors in `S` and three outside.

The quotient matrix is

```text
Q = [[0,6],
     [3,3]].
```

Thus `S` is equivalently:

```text
a (0,3)-regular set,
a perfect 2-coloring with quotient [[0,6],[3,3]],
a Hoffman-tight coclique.
```

All are exact names for the same Exact-One witness in this source class.

## 6. Centered eigenvector form

Let `x=1_S`.  The perfect-2-coloring equations give

```text
Adj(G) x = 3(1-x).
```

Define

```text
y = 3x - 1.
```

Then

```text
Adj(G) y = -3 y,
```

and

```text
y in {-1,2}^n.
```

Conversely, any `-3` eigenvector with entries in `{-1,2}` reconstructs

```text
x=(y+1)/3 in {0,1}^n
```

and satisfies the Exact-One equations.

Therefore the following formulations are exactly equivalent:

```text
A x = 1 with x in {0,1}^n;
ker(A) intersects {-1,2}^n;
G_A has an independent set of size n/3;
G_A has a Hoffman-tight coclique;
G_A has a (0,3)-regular set;
G_A has a perfect 2-coloring with quotient [[0,6],[3,3]].
```

## 7. Why this is useful but not itself an algorithm

R5 E12 proves that the source class is NP-complete.  Therefore none of the equivalent formulations above can simply be assumed polynomially solvable.

The value of this equivalence is structural:

```text
large rational nullity
=
large multiplicity of eigenvalue -3,
```

while a witness asks for an extremely special two-valued vector inside that eigenspace.

The universal hard core can now be stated without SAT language:

```text
Given a 6-regular point graph of an n_3 configuration,
whose least eigenvalue is -3 with large multiplicity,
decide whether the -3 eigenspace contains a {-1,2}-valued vector.
```

Equivalently:

```text
find or refute a perfect 2-coloring with quotient [[0,6],[3,3]].
```

## 8. Polynomial certificates and terminals preserved

All previous exact terminals translate cleanly:

```text
lambda_min > -3
  <=> A full Q-rank
  -> UNSAT.

small mult_{-3}(G)=d
  -> enumerate 2^d kernel/free-coordinate states exactly.

clique-LP infeasible
  -> UNSAT.

commuting I+P+Q
  -> exact Z3 propagation.

small distance t to a commuting normal form
  -> O(2^(3t) poly(n)).
```

The formulations are complementary, not competing.

## 9. Literature alignment

The equality condition used here is the classical Hoffman ratio-bound equality theorem: a ratio-tight independent set in a regular graph induces an equitable partition, and every outside vertex has exactly `-lambda_min` neighbors in the set.

Useful terminology in the literature includes:

```text
Hoffman-tight / ratio-tight independent set,
regular set,
perfect 2-coloring,
equitable bipartition.
```

These terms should be included in future literature sweeps to avoid rediscovering known structural results under SAT-specific vocabulary.

## 10. New frontier

The strongest current target is now:

```text
LARGE (-3)-EIGENSPACE
+ source-triangle decomposition
+ extensive noncommutativity
+ no clique-LP obstruction

=> either
   construct a {-1,2}-valued -3 eigenvector,
   or derive a polynomially checkable obstruction,
   or decompose the instance into smaller exact subproblems.
```

A polynomial exhaustive dichotomy of that form on the NP-complete R5 E12 class would imply `P=NP`.

P_VS_NP = OPEN.
