# R5 E47 — Chordal Conflict Rigidity Terminal

Date: 2026-10-02

Status:
`EXACT_CHORDAL_CONFLICT_RIGIDITY__CONNECTED_6REGULAR_CHORDAL_EQUALS_K7__LINEAR_CUBIC_CHORDAL_SECTOR_UNSAT`

Scientific ceiling:

```text
FOR EVERY SQUARE+CUBIC+LINEAR EXACT-ONE CARRIER A, THE CONFLICT GRAPH G_A
IS 6-REGULAR.

IF G_A IS CHORDAL, THEN EVERY CONNECTED COMPONENT OF G_A IS K7.

THEREFORE EVERY NONEMPTY SUCH INSTANCE IS EXACT-ONE UNSAT, BECAUSE
  alpha(G_A)=#components
WHILE
  n/3 = 7#components/3.

THIS IS A NEW EXACT CONFLICT-GRAPH TERMINAL. IT DOES NOT PROVE P=NP.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be square+cubic+linear:

```text
every row has weight 3,
every column has weight 3,
any two distinct rows overlap in at most one column.
```

Let `G_A` be the variable conflict graph from R5 E45: two columns are adjacent iff
they occur together in one source row.

R5 E45 proves

```text
A is Exact-One SAT
iff
alpha(G_A)=n/3.
```

## 2. Conflict degree is exactly six

Fix a variable-column `v`.

Because the source is cubic, `v` lies in exactly three source rows. Each such row
contains exactly two other variables, so these three rows contribute six neighbor
occurrences.

Linearity makes those six neighbors distinct. Indeed, if the same variable `u`
occurred with `v` in two different rows, those two rows would overlap in both `u`
and `v`, contradicting row intersection at most one.

Hence

```text
boxed:
deg_G(v)=6
```

for every variable `v`.

Therefore

```text
boxed:
G_A is 6-regular.
```

## 3. Regular chordal rigidity lemma

We use an elementary fact.

### Lemma

Every connected `k`-regular chordal graph is `K_(k+1)`.

### Proof

Every nonempty chordal graph has a simplicial vertex `v`: its neighborhood `N(v)`
is a clique.

If the graph is `k`-regular, then

```text
|N(v)|=k.
```

Thus

```text
{v} union N(v)
```

induces a clique `K_(k+1)`.

Take any neighbor `u in N(v)`. Inside this clique, `u` is already adjacent to the
other `k` vertices of the clique. Since the entire graph is `k`-regular, `u` cannot
have any neighbor outside the clique.

The same is true for every vertex of the clique. Hence this `K_(k+1)` is a connected
component.

If the graph is connected, it is the whole graph.

Therefore

```text
boxed:
connected + k-regular + chordal => K_(k+1).
```

## 4. Apply the lemma to the carrier

Since `G_A` is 6-regular, every connected chordal component is

```text
K7.
```

Thus if `G_A` has `c` connected components,

```text
n=7c
```

and

```text
alpha(G_A)=c,
```

because an independent set can contain at most one vertex from each `K7`, and one
vertex from each component is achievable.

Therefore

```text
3 alpha(G_A)=3c < 7c=n
```

for every nonempty instance.

Equivalently,

```text
alpha(G_A)=c < n/3.
```

By R5 E45:

```text
boxed:
Every nonempty square+cubic+linear carrier with chordal conflict graph is UNSAT.
```

## 5. Finite control: the Fano carrier

The companion checker uses the standard 7-point Steiner triple system

```text
013
025
046
126
145
234
356
```

as the source rows.

Its incidence matrix is

```text
7 x 7,
row weight 3,
column weight 3,
linear.
```

Every pair of variables lies in exactly one source triple, so

```text
G_A=K7.
```

Hence

```text
alpha(G_A)=1
```

and no Exact-One witness exists.

This is the smallest canonical control for the theorem.

## 6. Router branch

Add the exact graph-language branch:

```text
CHR0  build conflict graph G_A;
CHR1  verify square+cubic+linear carrier and therefore 6-regularity;
CHR2  run polynomial chordal recognition / verify a perfect-elimination order;
CHR3  if chordal and nonempty -> UNSAT;
CHR4  certificate: component partition into K7 blocks or a verified PEO plus 6-regularity.
```

No maximum-independent-set optimization is needed after recognition.

## 7. Relation to E45/E46

R5 E45 introduced conflict-graph polynomial languages through MIS.
R5 E46 instantiated that principle with line graphs and matching.

E47 is different:

```text
chordal + 6-regularity
```

does not merely make MIS easy; it completely rigidifies the carrier to disjoint
`K7` components and forces UNSAT.

So the graph axis now contains both:

```text
line-graph matching terminals,
chordal rigidity terminals.
```

## 8. Updated frontier

A genuine unresolved square+cubic+linear survivor must now have a conflict graph
that is simultaneously

```text
non-chordal,
not closed by the registered polynomial-MIS languages/backdoors,
```

in addition to surviving all kernel-language, quotient, separator, and arithmetic
terminals from the earlier R5 route.

The next useful graph attack is to weaken chordality while preserving enough local
rigidity from

```text
6-regularity + unique source-triangle edge partition + lambda_min >= -3.
```

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e47_chordal_conflict_rigidity.py
```
