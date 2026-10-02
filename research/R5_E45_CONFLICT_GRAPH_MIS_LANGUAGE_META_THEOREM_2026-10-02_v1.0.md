# R5 E45 — Conflict-Graph MIS Language Meta-Theorem

Date: 2026-10-02

Status:
`EXACT_CONFLICT_GRAPH_INDEPENDENT_SET_EQUIVALENCE__HEREDITARY_POLY_MIS_CLASSES_GIVE_EXACT_TERMINALS_AND_VERTEX_DELETION_BACKDOORS`

Scientific ceiling:

```text
THIS NOTE ADDS A GLOBAL ROUTER AXIS INDEPENDENT OF THE KERNEL-LANGUAGE AXIS.

FOR EVERY SQUARE+CUBIC EXACT-ONE SOURCE, LET G_A BE THE CONFLICT GRAPH ON
VARIABLES: TWO VARIABLES ARE ADJACENT WHEN THEY OCCUR TOGETHER IN A SOURCE ROW.

THEN

  A IS EXACT-ONE SAT
  IFF
  G_A HAS AN INDEPENDENT SET OF SIZE n/3.

CONSEQUENTLY EVERY HEREDITARY GRAPH CLASS WITH DETERMINISTIC POLYNOMIAL
MAXIMUM-INDEPENDENT-SET ALGORITHM GIVES AN EXACT POLYNOMIAL TERMINAL.

MOREOVER, AN EXPLICIT t-VERTEX DELETION BACKDOOR TO SUCH A CLASS GIVES
AN O(2^t poly(n)) EXACT ALGORITHM.

THIS IS THE CONFLICT-GRAPH ANALOGUE OF THE R5 E42 RHS-STABLE KERNEL-
LANGUAGE META-THEOREM.

P_VS_NP = OPEN.
```

## 1. Conflict graph

Let

```text
A in {0,1}^{n x n}
```

be square and cubic:

```text
every row has weight 3,
every column has weight 3.
```

Define the conflict graph `G_A` on the `n` variable-columns. Distinct columns `i,j`
are adjacent iff there exists a row containing both.

No linearity assumption is needed for the basic equivalence below, although the R5
E12 target is linear.

## 2. Exact-One witness gives an independent set

Let

```text
x in {0,1}^n,
A x=1.
```

Let

```text
S={j:x_j=1}.
```

No source row can contain two selected variables, so no two vertices of `S` are
adjacent in `G_A`. Hence `S` is independent.

Double count selected incidences. Every selected variable occurs in exactly three
rows, while every one of the `n` rows contains exactly one selected variable.
Therefore

```text
3|S|=n,
```

so

```text
|S|=n/3.
```

Thus SAT implies an independent set of size `n/3`.

## 3. Independent set of size n/3 gives Exact-One

Conversely let `S` be independent with

```text
|S|=n/3.
```

Each selected variable occurs in exactly three rows. Because `S` is independent,
no row contains two selected variables. Therefore the selected columns touch

```text
3|S|=n
```

distinct source rows.

There are exactly `n` rows total, so every row is touched exactly once.

Hence the incidence vector of `S` satisfies

```text
A x=1.
```

Therefore:

### Theorem CONFLICT-MIS

```text
boxed:
A is Exact-One SAT
iff
alpha(G_A)=n/3.
```

Equivalently, because the same counting argument shows every independent set has
size at most `n/3`, it is enough to test

```text
alpha(G_A) >= n/3.
```

## 4. Polynomial MIS languages

Let `C` be any graph class for which:

```text
membership in C is polynomially recognizable,
maximum independent set on C is deterministic polynomial.
```

Then for a square+cubic Exact-One source:

```text
construct G_A;
recognize whether G_A in C;
if yes compute alpha(G_A);
return SAT iff alpha(G_A)=n/3.
```

Thus every such graph class is automatically an Exact-One polynomial language.

This branch is independent of whether the rational kernel has a TU, signed-graphic,
root/potential, or other known representation.

## 5. Hereditary deletion backdoor

Assume additionally that `C` is hereditary under vertex deletion.

Suppose an explicit set

```text
D subseteq V(G_A),
|D|=t
```

is given such that

```text
G_A-D in C.
```

Branch over every subset

```text
S subseteq D
```

interpreted as the selected exceptional vertices.

Reject a branch immediately if `S` is not independent.

Any extension of `S` to a global independent set must avoid

```text
D\S
```

and every neighbor of `S` outside `D`.

So define

```text
H_S = G_A - D - N(S).
```

Because `H_S` is an induced subgraph of `G_A-D` and `C` is hereditary,

```text
H_S in C.
```

Compute `alpha(H_S)` in polynomial time.

The branch extends to an Exact-One witness iff there exists an independent set in
`H_S` of size

```text
k=n/3-|S|.
```

Since every subset of an independent set is independent, such a set exists iff

```text
alpha(H_S) >= k.
```

Therefore:

### Theorem CONFLICT-BACKDOOR

```text
boxed:
An explicit t-vertex deletion backdoor from G_A to a hereditary polynomial-MIS
class C yields an exact O(2^t poly(n)) Exact-One algorithm.
```

SAT reconstruction concatenates `S` with a suitable subset of a maximum independent
set in `H_S`.

## 6. Relation to E42

R5 E42 concerns deletion backdoors in an orthogonal linear representation:

```text
kernel language -> arbitrary residual RHS solver.
```

E45 is genuinely different:

```text
conflict graph -> independent-set language.
```

The two axes can close different instances and should both run after cheap exact
forcing/quotient reductions.

## 7. Concrete polynomial graph languages

The meta-theorem can be instantiated with any verified polynomial-MIS class.

One especially transparent example is the class of line graphs, treated explicitly
in the next R5 note: maximum independent set in a line graph is exactly maximum
matching in its root graph.

Other hereditary polynomial-MIS classes may be added to the router when their
recognition and solver are implemented/certified.

## 8. Updated router

Add the graph-language layer:

```text
CG0  build conflict graph G_A;
CG1  test registered polynomial-MIS languages;
CG2  if matched, compute alpha(G_A);
CG3  SAT iff alpha(G_A)=n/3;
CG4  if an explicit small deletion backdoor D is known, branch only on D.
```

This layer does not replace the algebraic/kernel router. It runs in parallel with it.

## 9. Frontier

R5 E12 proves that the unrestricted conflict graphs arising from the square+cubic+
linear carrier cannot all belong to one polynomial-MIS class unless P=NP.

So E45 does not close the universal problem. It creates a new exact family of
polynomial islands and FPT neighborhoods on a graph-theoretic axis orthogonal to the
previous kernel-language axis.

A genuine survivor must therefore avoid both:

```text
known polynomial kernel languages/backdoors,
and
known polynomial conflict-graph MIS languages/backdoors.
```

```text
P_VS_NP = OPEN.
```
