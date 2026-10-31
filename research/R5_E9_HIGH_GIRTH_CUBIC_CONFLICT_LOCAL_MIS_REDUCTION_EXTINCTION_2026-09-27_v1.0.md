# R5 E9 high-girth cubic conflict local MIS reduction extinction

Status: `THEOREM_CANDIDATE__R5_NEGATIVE_CONTROL__NOT_E8_D1__NOT_BASE_LEDGER_PROMOTED`

```text
E8_D1 = EMPTY
UNIVERSAL_SELECTOR = OPEN
P_VS_NP = OPEN
```

## 1. Setup

Let \(\mathcal H=(V,\mathcal E)\) be a finite hypergraph satisfying:

1. every hyperedge has size exactly 3 (`3-uniform`);
2. every vertex belongs to exactly 3 hyperedges (`3-regular`);
3. two distinct hyperedges meet in at most one vertex (`linear`).

Let \(G=G(\mathcal H)\) be the conflict graph / 2-section:

\[
uv\in E(G)\iff u\ne v\text{ and }\exists e\in\mathcal E:\{u,v\}\subseteq e.
\]

Let \(B(\mathcal H)\) be the bipartite incidence graph of vertices versus hyperedges.

For Exact-One, an independent set of size \(|\mathcal E|\) in \(G\) is the familiar conflict-graph representation of a satisfying exact transversal; this document does **not** claim a polynomial algorithm for finding such a set.

---

## 2. Lemma — the conflict graph is 6-regular and contains triangles

Fix \(v\in V\). It lies in exactly three source hyperedges. Each such hyperedge contributes the two other vertices as conflict neighbors of \(v\). Linearity prevents the same neighbor from occurring in two distinct source hyperedges, because then those two hyperedges would share both \(v\) and that neighbor.

Hence

\[
\deg_G(v)=3\cdot2=6.
\]

Every source hyperedge \(\{a,b,c\}\) induces the triangle \(abc\) in \(G\).

Therefore every connected component of \(G\) is 6-regular and non-bipartite.

---

## 3. Theorem — unique all-half optimum of the standard edge LP

Consider the standard fractional independent-set edge relaxation

\[
\max \sum_{v\in V(G)}x_v
\]

subject to

\[
x_u+x_v\le1\qquad(uv\in E(G)),
\qquad x_v\ge0.
\]

Because \(G\) is 6-regular,

\[
\sum_{uv\in E(G)}(x_u+x_v)=6\sum_vx_v.
\]

There are \(|E(G)|=6|V|/2=3|V|\) edge inequalities. Summing them gives

\[
6\sum_vx_v\le3|V|,
\]

hence

\[
\sum_vx_v\le |V|/2.
\]

The vector

\[
x_v=1/2\quad\forall v
\]

is feasible and attains \(|V|/2\). Thus it is optimal.

Now let \(x\) be any optimum. The sum of all edge slacks is zero. Every individual slack is nonnegative, so every edge inequality must be tight:

\[
x_u+x_v=1\qquad\forall uv\in E(G).
\]

On a connected component, these equations alternate values along paths. Because every component contains a triangle, following an odd cycle back to the start forces

\[
x_v=1-x_v,
\]

thus \(x_v=1/2\), and then connectivity forces every coordinate in the component to equal \(1/2\).

Therefore:

\[
\boxed{\text{the unique optimum is }x\equiv1/2.}
\]

### R5 consequence

The standard half-integral LP / Nemhauser–Trotter persistency donor has no integral `0/1` coordinate to fix on the untouched cubic-linear conflict carrier.

```text
R5_EDGE_LP_PERSISTENCY = NO_MOVE
```

This is a negative result about a preprocessing donor, not a lower bound against other algorithms.

---

## 4. Corollary — degree-2 folding is absent

Every conflict vertex has degree 6. Therefore any standard folding rule whose entry condition is a degree-2 vertex cannot trigger.

```text
R5_DEGREE2_FOLDING = NO_MOVE
```

---

## 5. High-girth lemma — adjacent vertices have exactly one common open neighbor

Assume from now on that

\[
\operatorname{girth}(B(\mathcal H))\ge8.
\]

Let \(u,v\) be adjacent in \(G\). By linearity there is a unique source hyperedge

\[
e_{uv}=\{u,v,w\}.
\]

Therefore \(w\in N_G(u)\cap N_G(v)\).

Suppose another vertex \(z\ne w\) were a common neighbor. Then there are source hyperedges \(e_{uz}\) and \(e_{vz}\). Linearity and \(z\ne w\) make these distinct from \(e_{uv}\) and from each other. The incidence graph then contains

\[
u-e_{uv}-v-e_{vz}-z-e_{uz}-u,
\]

which is a 6-cycle, contradicting incidence girth at least 8.

Hence

\[
\boxed{|N_G(u)\cap N_G(v)|=1\quad\text{for every }uv\in E(G).}
\]

---

## 6. Theorem — closed-neighborhood domination is absent at incidence girth >= 8

Because \(G\) is 6-regular, every closed neighborhood has size 7.

Suppose distinct vertices satisfy

\[
N_G[u]\subseteq N_G[v].
\]

Equal cardinality forces equality. Since \(u\in N_G[u]=N_G[v]\), the distinct vertices \(u,v\) are adjacent. Equality of closed neighborhoods would then make the other five vertices of the size-7 set common open neighbors of \(u\) and \(v\), so

\[
|N_G(u)\cap N_G(v)|=5,
\]

contradicting the high-girth lemma.

Therefore no strict or equality-based closed-neighborhood domination pair exists:

```text
R5_CLOSED_NEIGHBORHOOD_DOMINATION = NO_MOVE
```

---

## 7. Theorem — the standard/simple unconfined rule is absent at incidence girth >= 8

Use the Akiba–Iwata simple unconfined procedure. Start from

\[
S=\{v\}.
\]

For any candidate \(u\in N_G(S)=N_G(v)\),

\[
|N_G(u)\cap S|=1.
\]

Because \(u\) and \(v\) are adjacent, the high-girth lemma says they have exactly one common open neighbor \(w\). Since \(\deg_G(u)=6\), the six neighbors of \(u\) consist of

- \(v\),
- the unique common neighbor \(w\),
- four vertices outside \(N_G[v]\).

Thus

\[
|N_G(u)\setminus N_G[S]|=4
\]

for every possible first-step candidate \(u\).

The simple unconfined procedure continues only when that outside set has size 0 or 1; when its minimum size is greater than 1 it returns `confined`. Therefore it stops immediately for every start vertex.

```text
R5_SIMPLE_UNCONFINED = NO_MOVE
```

This statement is intentionally scoped to the standard/simple unconfined procedure source-bound in the associated audit. No claim is made for every later generalized confinement rule.

---

## 8. Combined R5 negative-control consequence

Reuse the already materialized regular-uniform conflict-expansion theorem, which eliminates nonempty critical independent sets and the corresponding classic critical-set/crown entry object on this carrier.

For a linear 3-uniform 3-regular Exact-One source we therefore have, before any representation-changing move:

```text
R5_EDGE_LP_PERSISTENCY = NO_MOVE
R5_DEGREE2_FOLDING = NO_MOVE
R5_CRITICAL_SET_CROWN = NO_MOVE   [existing theorem reused]
```

and with incidence girth at least 8:

```text
R5_CLOSED_NEIGHBORHOOD_DOMINATION = NO_MOVE
R5_SIMPLE_UNCONFINED = NO_MOVE
```

The existing fixed-girth / prescribed-cycle survivor machinery makes this relevant to arbitrary-size high-girth negative controls rather than a single finite fixture.

---

## 9. What remains open

This theorem does **not** eliminate all imported MIS reductions. In particular, no universal closure is claimed here for all variants of:

```text
twin
alternative
packing
funnel
desk
struction
generalized confinement
other contextual exact replacements
```

Nor does it close:

```text
R1_BROADER_CERTIFIED_EQUIVALENCE = OPEN
R5_ALL_STRUCTURAL_DOMINANCE = OPEN
R6_RANKED_SR_MACRO = OPEN
UNIVERSAL_SELECTOR = OPEN
```

The correct scientific update is therefore:

```text
NEW_RESULT = ARBITRARY_CLASS R5 NEGATIVE-CONTROL STRENGTHENING
UNIVERSAL_POLYNOMIAL_SAT_SOLVER = NOT YET OBTAINED
P_VS_NP = OPEN
```

---

## 10. Regression role

`experiments/r5_e9_high_girth_cubic_conflict_local_mis_reduction_extinction.py`
uses the 15-point duad/syntheme configuration (the order-2 generalized quadrangle incidence structure) solely as a deterministic finite regression of the theorem hypotheses and local consequences:

- 3-uniform,
- 3-regular,
- linear,
- incidence girth 8,
- conflict degree 6,
- one common open neighbor per adjacent pair,
- no closed-neighborhood domination,
- first-step unconfined outside size exactly 4.

The executable fixture is **not** the proof of the arbitrary-size theorem.
