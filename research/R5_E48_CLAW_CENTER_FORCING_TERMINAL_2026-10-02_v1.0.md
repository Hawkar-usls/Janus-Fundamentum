# R5 E48 — Claw-Center Forcing Terminal

Date: 2026-10-02

Status:
`EXACT_SAT_IMPLIES_2N_OVER_3_CLAW_CENTERS__NONCLAW_VERTICES_FORCED_SELECTED__POLYNOMIAL_FORCING_AND_UNSAT_CERTIFICATES`

Scientific ceiling:

```text
FOR EVERY SQUARE+CUBIC+LINEAR EXACT-ONE CARRIER A WITH CONFLICT GRAPH G_A,
EVERY UNSELECTED VERTEX OF ANY EXACT-ONE WITNESS IS THE CENTER OF AN
INDUCED CLAW K_1,3 WHOSE THREE LEAVES ARE SELECTED VARIABLES.

THEREFORE EVERY VERTEX THAT IS NOT A CLAW CENTER IS FORCED INTO EVERY
EXACT-ONE WITNESS.

CONSEQUENCES:
  #nonclaw-centers > n/3        -> UNSAT;
  two adjacent nonclaw-centers  -> UNSAT;
  #nonclaw-centers = n/3        -> the witness is uniquely forced and can be
                                   checked directly.

THIS IS A NEW EXACT POLYNOMIAL FORCING TERMINAL ON THE CONFLICT-GRAPH AXIS.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be square+cubic+linear:

```text
every source row has weight 3,
every variable column has weight 3,
any two distinct source rows intersect in at most one variable.
```

Let `G_A` be the conflict graph on variables: two variables are adjacent exactly
when they occur together in a source row.

R5 E45 proves

```text
A is Exact-One SAT
iff
G_A has an independent set S of size n/3.
```

Such an `S` is exactly the set of selected variables in an Exact-One witness.

## 2. Every unselected variable sees three selected neighbors

Assume `S` is an Exact-One witness and fix a vertex

```text
v not in S.
```

The variable `v` occurs in exactly three source rows. Call them

```text
R_1,R_2,R_3.
```

Because the witness selects exactly one variable in every row and `v` itself is not
selected, each `R_i` contains a selected co-variable

```text
s_i in S.
```

Thus `v` is adjacent in `G_A` to each of

```text
s_1,s_2,s_3.
```

## 3. The three selected neighbors are distinct

Suppose

```text
s_i=s_j=s
```

for two different source rows `R_i,R_j`.

Then both rows contain both variables

```text
v and s.
```

So the two distinct rows intersect in at least two columns, contradicting linearity.

Therefore

```text
boxed:
s_1,s_2,s_3 are pairwise distinct.
```

## 4. The three selected neighbors are pairwise nonadjacent

The witness set `S` is independent in the conflict graph. Hence no two selected
variables occur together in one source row.

Therefore

```text
s_i s_j not in E(G_A)
```

for all distinct `i,j`.

Combining Sections 2--4, the induced subgraph on

```text
{v,s_1,s_2,s_3}
```

contains the three edges from `v` to the leaves and no edges among the leaves.
Thus it is an induced claw

```text
K_1,3
```

centered at `v`.

Hence:

### Theorem CLAW-NECESSITY

```text
boxed:
In every Exact-One witness of a square+cubic+linear carrier, every unselected
variable is a claw center in the conflict graph.
```

Moreover the three claw leaves can be chosen from the selected witness itself.

## 5. Counting consequence

Every Exact-One witness contains exactly

```text
n/3
```

selected vertices and therefore exactly

```text
2n/3
```

unselected vertices.

By CLAW-NECESSITY all `2n/3` unselected vertices are claw centers.

Thus:

```text
boxed:
SAT => at least 2n/3 vertices of G_A are claw centers.
```

Equivalently, if fewer than `2n/3` vertices can center an induced claw, return
UNSAT.

## 6. Non-claw centers are forced selected

Define

```text
F={v in V(G_A) : N(v) contains no independent 3-set}.
```

These are exactly the vertices that are not centers of induced claws.

By CLAW-NECESSITY no vertex of `F` may be unselected. Therefore every Exact-One
witness `S` must satisfy

```text
boxed:
F subseteq S.
```

Since every witness has size `n/3`, this gives several exact polynomial rules.

### Rule F1 — cardinality obstruction

If

```text
|F| > n/3,
```

then no witness can contain all forced vertices, so return UNSAT.

### Rule F2 — conflict obstruction

If two vertices of `F` are adjacent, they cannot both belong to the independent
witness set. But both are forced selected.

Therefore

```text
boxed:
E(G_A[F]) != empty => UNSAT.
```

### Rule F3 — exact forced witness

If

```text
|F|=n/3,
```

then every witness must equal `F` exactly.

So check directly whether the incidence vector of `F` satisfies

```text
A x=1.
```

If yes, return SAT with witness `F`; otherwise return UNSAT.

No search remains.

## 7. Polynomial computability

For the frozen linear cubic carrier the conflict graph is 6-regular by R5 E47.

To decide whether a vertex `v` is a claw center, inspect the at most

```text
binom(6,3)=20
```

triples of neighbors and test whether one triple is pairwise nonadjacent.

Thus the full forced set `F` is computable in

```text
O(n)
```

local triple checks after constructing `G_A`.

Rules F1--F3 are therefore polynomial and in fact linear-time up to graph
construction.

## 8. Exact finite controls

The companion checker includes two square+cubic+linear carriers.

### SAT control

On `n=9`, use source rows

```text
036
125
028
237
014
456
167
478
358
```

The instance has the Exact-One witness

```text
S={0,5,7}.
```

The checker verifies that the non-claw-center set is exactly

```text
F={0,5,7}=S.
```

So Rule F3 reconstructs the SAT witness with no branching.

### UNSAT control

For the 7-point Fano carrier of R5 E47,

```text
G_A=K7.
```

No vertex of `K7` can center a claw, so

```text
F=V(G_A),
|F|=7>7/3.
```

Rule F1 returns UNSAT immediately.

## 9. Relation to chordal and line-graph terminals

R5 E47 proves every chordal linear-cubic conflict graph is a disjoint union of `K7`
components, hence UNSAT.

E48 strictly abstracts the local reason needed for forcing: a vertex does not need
to lie in a chordal component. It is enough that the vertex itself cannot be a claw
center.

Thus E48 can force selected coordinates inside globally nonchordal conflict graphs.

Likewise the rule is independent of the R5 E46 line-graph matching terminal.
It may close instances that are neither chordal nor line graphs.

## 10. Iterated forcing

Once a non-claw vertex is forced selected, all six of its conflict neighbors are
forced unselected. Original Exact-One rows incident to those variables may then
force additional coordinates through the already registered R5 E40/E43 local
propagation rules.

After propagation, rebuild the residual active conflict structure and repeat the
claw-center test whenever the reduced carrier still preserves the required exact
interpretation.

The one-shot Rules F1--F3 above are unconditional on the original square+cubic+linear
carrier; iterative residual use must preserve the residual-row semantics and should
be routed through the generic forcing engine rather than assumed automatically.

## 11. Updated frontier

A genuine unresolved SAT-capable hard carrier must have enough local conflict
freedom that

```text
at least 2n/3 vertices are claw centers,
```

and its non-claw forced set must neither overfill nor conflict.

So after E48 the conflict-graph survivor must simultaneously evade:

```text
chordal rigidity,
line-graph matching,
non-claw forcing/count obstructions,
registered polynomial-MIS languages/backdoors,
```

as well as all earlier kernel-language, quotient, decomposition, and arithmetic
terminals.

The next graph-side target is to exploit the stronger witness-dependent fact:

```text
for every v outside S, the claw leaves can all be chosen inside the same global
independent witness S.
```

This couples local claws globally and is stronger than merely counting claw centers.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e48_claw_center_forcing.py
```
