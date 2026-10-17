# R5 E9 — Directed Perfect-Code Normal Form

Date: 2026-09-27

Status:
`JANUS_EXACT_NORMAL_FORM__NO_UNIVERSAL_PROMOTION`

## 1. Construction

Let `A` be a connected cubic square incidence matrix and choose any perfect matching `M0` in its cubic bipartite Levi graph. Pair each source row with the column matched to it and relabel the pairs by `i in [n]`.

Removing `M0` leaves a 2-regular bipartite graph. Orient every remaining incidence from the row-side pair `i` to the column-side pair `j`. The result is a loopless directed graph `D` with

```text
outdegree(i)=2
indegree(i)=2
```

for every vertex. Equivalently, if the two outgoing neighbors of `i` are `p(i),q(i)`, then the normalized incidence matrix is exactly

```text
A' = I+P+Q.
```

## 2. Exact equivalence

For a Boolean vector `x`, the row indexed by `i` is

```text
x_i + x_{p(i)} + x_{q(i)} = 1.
```

Therefore

```text
Ax=1
iff
for every i, |N_D^+[i] intersect S|=1,
```

where

```text
S={i:x_i=1}
N_D^+[i]={i,p(i),q(i)}.
```

Thus the frozen cubic Exact-One problem is exactly the existence of a directed perfect code / efficient dominating set in the associated 2-in/2-out permutation digraph.

Important correction: this is **not** the ordinary digraph-kernel condition. A kernel only requires at least one selected out-neighbor for a nonselected vertex; Exact-One requires exactly one selected vertex in the closed out-neighborhood.

### Theorem DPC-1

```text
CUBIC-LINEAR EXACT-ONE
= PERFECT-CODE EXISTENCE
  on a loopless 2-in/2-out digraph that is the union of two permutation arc sets.
```

The conversion in both directions is linear after the Levi perfect matching is known, and witness transport is the identity on the paired indices.

## 3. Relation to the two-permutation theorem

The digraph is precisely the directed form of the existing normalization

```text
A'=I+P+Q.
```

So this theorem does not change computational power; it exposes an external graph-theoretic language for the residual.

If `P,Q` commute and the action is connected, the digraph is a strongly connected 2-valent Cayley digraph on an abelian group. The previously proved JANUS commuting terminal is therefore a special case of the published perfect-code theory for 2-valent abelian Cayley digraphs.

External source binding:
- S. Yu, Y. Yang, Y. Fan, X. Ma, *Perfect codes in 2-valent Cayley digraphs on abelian groups*, Discrete Applied Mathematics 357 (2024), 236–240, DOI `10.1016/j.dam.2024.06.002`, arXiv `2310.19017`.
- That paper classifies strongly connected 2-valent abelian Cayley digraphs admitting perfect codes and determines their perfect codes.

The source is corroboration / a donor for the abelian branch, not a theorem for arbitrary noncommuting permutation digraphs.

## 4. New attack language

The current hard core can equivalently be stated as

```text
connected loopless 2-in/2-out permutation digraph D
+ D comes from a linear cubic Levi carrier
+ associated A=I+P+Q has nullity_Q(A)=omega(log n)
+ chosen P,Q do not commute
+ admitted OET / fixed-leaf decompositions fail
+ decide whether D has a perfect code.
```

This language exposes possible donors from perfect-code / efficient-domination theory while preserving the exact JANUS carrier restrictions.

## 5. Anti-loop

Do not replace the exact condition by ordinary kernel existence:

```text
kernel:        x_i=0 => at least one selected out-neighbor
perfect code:  x_i+x_p(i)+x_q(i)=1 exactly.
```

Do not import NP-hardness or tractability for generic perfect-code instances unless the theorem matches the exact `2-in/2-out + two permutation arc sets + linear Levi` restrictions.

## 6. Ceiling

```text
DIRECTED PERFECT-CODE EQUIVALENCE = PROVED
WITNESS BIJECTION                  = PROVED
COMMUTING/ABELIAN SOURCE BINDING   = VERIFIED
NONCOMMUTING PERFECT-CODE CORE     = OPEN
UNIVERSAL POLYNOMIAL SOLVER        = NOT PROVED
E8_D1                              = EMPTY
P_VS_NP                            = OPEN
```
