# R5 E46 — Conflict Line-Graph Matching Terminal

Date: 2026-10-02

Status:
`EXACT_CONFLICT_LINE_GRAPH_TERMINAL__MAXIMUM_INDEPENDENT_SET_REDUCES_TO_MATCHING__E45_INSTANTIATION`

Scientific ceiling:

```text
THIS NOTE INSTANTIATES THE R5 E45 CONFLICT-GRAPH META-THEOREM WITH A
CONCRETE GRAPH LANGUAGE THAT IS POLYNOMIAL FOR A COMPLETELY DIFFERENT
REASON THAN THE KERNEL-LANGUAGE ROUTER.

IF THE CONFLICT GRAPH G_A IS THE LINE GRAPH L(H) OF SOME ROOT GRAPH H,
THEN

  alpha(G_A)=nu(H),

WHERE nu(H) IS THE MAXIMUM MATCHING SIZE OF H.

THEREFORE EXACT-ONE IS SAT IFF

  nu(H)=n/3.

MAXIMUM MATCHING IS DETERMINISTIC POLYNOMIAL, SO THIS IS AN EXACT
POLYNOMIAL TERMINAL INDEPENDENT OF NULLITY, TU, ROOT-KERNEL, OR
SIGNED-GRAPH ORTHOGONAL REPRESENTATIONS.

P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be square and cubic, and let `G_A` be its conflict graph as in R5 E45.

Assume a graph

```text
H=(V,E),
|E|=n
```

is supplied together with a bijection

```text
E <-> V(G_A)
```

such that

```text
boxed:
G_A=L(H).
```

This certificate is polynomially verifiable: two conflict vertices are adjacent
iff the corresponding root edges share an endpoint.

Standard line-graph recognition can also reconstruct a root graph, but the exact
terminal only needs a verifiable root certificate.

## 2. Independent sets in a line graph are matchings

By definition, vertices of `L(H)` are edges of `H`, and two line-graph vertices are
adjacent exactly when the corresponding root edges meet.

Therefore a set of vertices is independent in `L(H)` exactly when the corresponding
edges of `H` are pairwise vertex-disjoint.

That is precisely a matching.

Hence

```text
boxed:
alpha(L(H))=nu(H),
```

where `nu(H)` denotes maximum matching size.

## 3. Exact-One equivalence

R5 E45 proves for every square+cubic carrier

```text
A is Exact-One SAT
iff
alpha(G_A)=n/3.
```

Under the line-graph hypothesis,

```text
alpha(G_A)=alpha(L(H))=nu(H).
```

Therefore:

### Theorem LINE-MATCH

```text
boxed:
If G_A=L(H), then
A is Exact-One SAT
iff
H has a matching of size n/3.
```

Because a maximum matching can be found deterministically in polynomial time, this
is an exact polynomial terminal.

If `3` does not divide `n`, the cardinality test already returns UNSAT.

## 4. Witness reconstruction

If a matching

```text
M subseteq E(H)
```

of size `n/3` is found, take the corresponding `n/3` variable-columns of `A`.

They form an independent set in `G_A`, so by R5 E45 they touch `n` distinct source
rows and hence form an Exact-One witness.

Thus matching edges map directly to selected Boolean variables.

## 5. UNSAT certificate

If the maximum matching has size

```text
nu(H)<n/3,
```

then

```text
alpha(G_A)<n/3,
```

and R5 E45 implies UNSAT.

A maximum-matching certificate plus the verified equality `G_A=L(H)` is therefore
enough for the router branch.

## 6. Finite square+cubic+linear control

The companion checker uses the following exact carrier.

Take `H=K5`. Use its ten edges as Exact-One variables and its ten triangles as source
rows. A row contains the three edges of one triangle of `K5`.

Then:

```text
n=10,
every row has weight 3,
every edge of K5 lies in exactly 3 triangles,
so every column has weight 3,
any two distinct K5 triangles share at most one edge.
```

Hence the incidence matrix is square+cubic+linear.

Two variables conflict exactly when the corresponding K5 edges lie together in a
triangle. In `K5`, any two adjacent edges determine a unique triangle, while
disjoint edges lie in no common triangle. Therefore

```text
G_A=L(K5).
```

The checker verifies exactly

```text
alpha(G_A)=nu(K5)=2.
```

Since `n=10` is not divisible by three, the control is UNSAT, consistently with the
matching terminal.

## 7. Relation to earlier JANUS languages

E46 is graph-language rather than kernel-language.

It can close an instance even when none of the following is exposed:

```text
small rational nullity,
TU orthogonal representation,
signed-graphic f-factor kernel,
root/tension potential kernel,
small projective quotient width.
```

Conversely, many easy kernel-language instances need not have line-graph conflict
structure.

So E46 genuinely adds an orthogonal router axis.

## 8. Deletion backdoor

The line-graph class is hereditary under vertex deletion: deleting a vertex from
`L(H)` corresponds to deleting the associated edge from `H`.

Therefore R5 E45 immediately gives:

```text
boxed:
An explicit t-vertex deletion set D such that G_A-D is a line graph yields an
O(2^t poly(n)) Exact-One algorithm.
```

For each branch on `D`, the residual maximum-independent-set computation is just a
maximum matching computation in the corresponding root subgraph.

## 9. Updated frontier

After E46, a genuine survivor must avoid not only all known kernel languages and
backdoors, but also matching-like conflict structure.

The graph-language frontier now asks for broader polynomial-MIS classes that arise
naturally from square+cubic+linear conflict graphs and can be recognized/certified
without collapsing back to the already known low-width cases.

The hard E12 class proves that unrestricted conflict graphs cannot all admit such a
polynomial MIS reduction unless P=NP.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e46_conflict_line_graph_matching.py
```
