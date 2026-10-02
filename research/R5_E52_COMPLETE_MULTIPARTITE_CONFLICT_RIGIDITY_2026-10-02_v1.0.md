# R5 E52 — Complete-Multipartite Conflict Rigidity

Date: 2026-10-02

Status:
`EXACT_COMPLETE_MULTIPARTITE_6REGULAR_CLASSIFICATION__K333_ONLY_SAT_COMPONENT__MULTICLAW_GLOBAL_RIGIDITY`

Scientific ceiling:

```text
FOR A SQUARE+CUBIC+LINEAR EXACT-ONE CARRIER, THE CONFLICT GRAPH IS 6-REGULAR.

IF A CONNECTED CONFLICT COMPONENT IS COMPLETE MULTIPARTITE, REGULARITY FORCES
ALL PARTS TO HAVE THE SAME SIZE s AND
  (r-1)s=6,
WHERE r IS THE NUMBER OF PARTS.

THUS THE ONLY CONNECTED 6-REGULAR COMPLETE-MULTIPARTITE POSSIBILITIES ARE
  K_{6,6}, K_{3,3,3}, K_{2,2,2,2}, K_7.

K_{6,6} CANNOT OCCUR BECAUSE EVERY SOURCE ROW CREATES A TRIANGLE.
AMONG THE REMAINING TYPES, ONLY K_{3,3,3} HAS alpha=n/3.

THEREFORE A COMPLETE-MULTIPARTITE CONFLICT CARRIER IS EXACT-ONE SAT IFF
EVERY CONNECTED COMPONENT IS K_{3,3,3}.

THIS GIVES A NEW POLYNOMIAL TERMINAL INSIDE THE MULTICLAW REGIME:
EVERY VERTEX OF K_{3,3,3} HAS TWO DISTINCT CLAW TRIPLES, SO E49 DOES NOT
APPLY, YET THE INSTANCE IS SOLVED GLOBALLY BY MULTIPARTITE RIGIDITY.

P_VS_NP = OPEN.
```

## 1. Setting

Let `A` be square+cubic+linear and let `G=G_A` be its conflict graph.
By R5 E47,

```text
boxed:
G is 6-regular.
```

By R5 E45,

```text
boxed:
A is Exact-One SAT iff alpha(G)=n/3.
```

Assume now that every connected component of `G` is complete multipartite.

## 2. Regular complete multipartite graphs have equal parts

Consider one connected component

```text
H=K_{s_1,...,s_r},
r>=2.
```

A vertex in part `i` has degree

```text
|V(H)|-s_i.
```

Since `H` is 6-regular, this quantity equals six for every part. Hence all `s_i`
are equal. Write the common part size as `s`.

Then

```text
|V(H)|=rs
```

and every vertex has degree

```text
(r-1)s=6.
```

Therefore the positive integer factorization of six completely classifies the
component.

## 3. Four algebraic possibilities

The pairs

```text
(r-1,s)
```

are

```text
(1,6),
(2,3),
(3,2),
(6,1).
```

Hence

```text
H in {
  K_{6,6},
  K_{3,3,3},
  K_{2,2,2,2},
  K_7
}.
```

No other connected 6-regular complete-multipartite graph exists.

## 4. K_{6,6} is impossible for a nonempty Exact-One carrier

Every source row of `A` contains exactly three variables. Those three variables are
pairwise adjacent in the conflict graph, so every source row creates a triangle.

But `K_{6,6}` is bipartite and triangle-free.

Therefore a connected conflict component arising from a nonempty source cannot be
`K_{6,6}`.

So only

```text
K_{3,3,3},
K_{2,2,2,2},
K_7
```

remain.

## 5. Independence ratios

For a complete multipartite graph with equal part size `s`, a maximum independent
set is exactly one whole part. Hence

```text
alpha(H)=s.
```

For the three remaining component types:

```text
K_{3,3,3}:    n_H=9, alpha=3, alpha/n_H=1/3;
K_{2,2,2,2}:  n_H=8, alpha=2, alpha/n_H=1/4;
K_7:           n_H=7, alpha=1, alpha/n_H=1/7.
```

Thus only `K_{3,3,3}` attains the Exact-One ratio `1/3`.

## 6. Connected classification theorem

For one connected complete-multipartite conflict component:

```text
boxed:
Exact-One SAT iff G=K_{3,3,3}.
```

Indeed, R5 E45 requires

```text
alpha(G)=n/3,
```

and the table above shows this only for `K_{3,3,3}`.

## 7. Disconnected case

Let the conflict graph have components

```text
H_1,...,H_c.
```

Since independent-set number and vertex count add over components,

```text
alpha(G)=sum_i alpha(H_i),
n=sum_i |V(H_i)|.
```

Every admissible non-`K_{3,3,3}` component has independence ratio strictly less
than `1/3`. Therefore

```text
alpha(G)=n/3
```

holds iff every component has ratio exactly `1/3`, i.e. iff every component is
`K_{3,3,3}`.

Hence:

### Theorem COMPLETE-MULTIPARTITE-TERMINAL

```text
boxed:
A square+cubic+linear Exact-One carrier with complete-multipartite conflict graph
is SAT iff every connected component of the conflict graph is K_{3,3,3}.
```

Otherwise it is UNSAT.

Recognition and component classification are polynomial.

## 8. SAT reconstruction for K_{3,3,3}

Let one component have parts

```text
P_1,P_2,P_3,
|P_i|=3.
```

Any whole part is an independent set of size three. Since the component has nine
vertices,

```text
|P_i|=9/3.
```

By R5 E45, the incidence vector of any part is an Exact-One witness on that
component.

For multiple `K_{3,3,3}` components, choose one part in each component and take the
union.

This reconstructs a global witness directly.

## 9. Exact Latin-square control

The companion checker builds the canonical `K_{3,3,3}` carrier with parts

```text
A={0,1,2},
B={3,4,5},
C={6,7,8}.
```

Use the nine source rows of the `Z_3` Latin square:

```text
{A_i,B_j,C_(i+j)}
for i,j in Z_3.
```

Every row has weight three, every variable occurs in exactly three rows, and any
two rows intersect in at most one variable.

Two variables are adjacent iff they belong to different parts, so

```text
G=K_{3,3,3}.
```

Selecting all three variables of one part, say `A`, chooses exactly one variable in
every source row. Thus the checker verifies SAT explicitly.

## 10. Why this is beyond E49

For a vertex `v` of `K_{3,3,3}`, its six neighbors are the two other parts, each of
size three.

An independent 3-subset of `N(v)` must be exactly one whole neighboring part.
Therefore

```text
boxed:
c(v)=2
```

for every vertex.

So every vertex is multiclaw and the E49 exceptional set is the whole graph:

```text
t_multiclaw=n.
```

Yet E52 solves the family in polynomial time by a global multipartite normal form.

This is an explicit warning that linear multiclaw ambiguity is not itself hardness.

## 11. Relation to E47

`K_7` is the chordal endpoint already closed by R5 E47.

E52 strictly extends the conflict rigidity picture to a nonchordal SAT family:

```text
K_{3,3,3}
```

contains many induced 4-cycles and is therefore not chordal, but remains exactly
tractable.

## 12. E45 backdoor consequence

Complete multipartite graphs form a hereditary class and maximum independent set is
trivial once the parts are known.

Therefore the generic R5 E45 conflict-backdoor theorem also gives:

```text
an explicit t-vertex deletion set whose removal leaves a complete multipartite
conflict graph -> O(2^t poly(n)).
```

For the frozen 6-regular carrier, E52 gives the stronger zero-backdoor
classification above.

## 13. Updated frontier

After E52, a genuine unresolved multiclaw carrier must avoid not only binary local
state structure, but also this global multipartite collapse.

The graph-side survivor must now be simultaneously:

```text
nonchordal,
not a line graph terminal,
not complete multipartite,
rich in multiclaw ambiguity,
and outside registered polynomial-MIS/backdoor classes.
```

This reinforces the current lesson of R5 E48--E52:

```text
local ambiguity must be combined with global incompatibility complexity before it
can represent the true hard core.
```

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e52_complete_multipartite_conflict.py
```
