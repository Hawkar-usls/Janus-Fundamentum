# R5 E12 — Linear Cubic Hardness Bridge

Date: 2026-10-02

Status:
`SELF_CONTAINED_POLYNOMIAL_REDUCTION__RXC3_TO_SQUARE_CUBIC_LINEAR_EXACTONE__P_VS_NP_STILL_OPEN`

Scientific ceiling:

```text
THIS NOTE PROVES THAT THE SQUARE + CUBIC + LINEAR EXACT-ONE CLASS
IS NP-HARD (AND IS CLEARLY IN NP).

THEREFORE A DETERMINISTIC POLYNOMIAL ALGORITHM FOR THIS NARROW CLASS
WOULD IMPLY P=NP.

THIS NOTE DOES NOT PROVIDE THAT ALGORITHM.
P_VS_NP = OPEN.
```

## 1. Source problem: RXC3

Restricted Exact Cover by 3-Sets (RXC3) is the following NP-complete problem.

Input:

```text
X = {x_1,...,x_q},   3 | q,
C = {C_1,...,C_q},
|C_j| = 3,
every x_i occurs in exactly three C_j.
```

Question: is there a subcollection `C*` such that every element of `X` occurs in exactly one selected set?

The equality `|C|=|X|=q` follows by double counting incidences.

Classical source: T. F. Gonzalez, "Clustering to minimize the maximum intercluster distance", Theoretical Computer Science 38 (1985), 293-306.  The restricted exact-cover problem is commonly called RXC3 / RX3C.

The reduction below is written self-containedly so that the target hardness claim does not depend on silently importing an unverified property of a citation.

## 2. Target class

We reduce RXC3 to Exact-One instances whose incidence matrix `A` satisfies simultaneously:

```text
A is square;
every row has exactly three ones;
every column has exactly three ones;
any two distinct rows overlap in at most one column.
```

Equivalently, the dual exact-cover hypergraph is:

```text
3-uniform,
3-regular,
linear,
with the same number of vertices and hyperedges.
```

This is precisely the square+cubic+linear source class used by the R5 spectral route.

## 3. Gadget for one RXC3 triple

Fix one source triple

```text
C_j = {x_1,x_2,x_3}.
```

(The subscripts `1,2,3` here are local positions inside `C_j`.)

Create six fresh elements

```text
z_1,...,z_6
```

and five triples

```text
L_1 = {x_1,z_1,z_4}
L_2 = {x_2,z_2,z_5}
L_3 = {x_3,z_3,z_6}
L_4 = {z_1,z_2,z_3}
L_5 = {z_4,z_5,z_6}.
```

Create a disjoint primed copy

```text
x'_1,x'_2,x'_3,
z'_1,...,z'_6,
L'_1,...,L'_5.
```

The original elements `x_i` and their primed copies are global across gadgets: the same `x` is used in every gadget corresponding to a source triple that contains it.

Finally introduce three fresh local elements

```text
t_1,t_2,t_3
```

and seven dummy triples

```text
D_1 = {z_2, z_6, t_1}
D_2 = {z_3, z_4, t_2}
D_3 = {z_1, z_5, t_3}
D_4 = {z'_2,z'_6,t_2}
D_5 = {z'_3,z'_4,t_3}
D_6 = {z'_1,z'_5,t_1}
D_7 = {t_1,t_2,t_3}.
```

Thus each source triple is replaced by

```text
15 fresh internal elements
17 target triples,
```

in addition to using the six boundary elements `x_1,x_2,x_3,x'_1,x'_2,x'_3`.

## 4. Degree audit

Every target triple has size exactly three.

For an original boundary element `x`, the source RXC3 promise says that `x` belongs to exactly three source triples.  In each corresponding gadget it appears in exactly one of `L_1,L_2,L_3`, hence its target degree is exactly three.  The same holds for `x'`.

Each unprimed `z_i` occurs in exactly two `L` triples and exactly one of `D_1,D_2,D_3`; each primed `z'_i` occurs in exactly two `L'` triples and exactly one of `D_4,D_5,D_6`.  Hence every `z,z'` has degree three.

The `t` elements satisfy

```text
t_1 in D_1,D_6,D_7,
t_2 in D_2,D_4,D_7,
t_3 in D_3,D_5,D_7,
```

so each also has degree three.

Therefore the target hypergraph is 3-uniform and 3-regular.

## 5. Square audit

Let the RXC3 instance have `q` elements and hence `q` triples.

The target has

```text
2q boundary elements x,x'
+ 15q internal elements
= 17q elements.
```

Each source triple produces exactly

```text
5 L + 5 L' + 7 D = 17
```

target triples, hence the target has `17q` triples.

Therefore the target incidence matrix is square.

## 6. Linearity audit

Inside one gadget, direct inspection shows that any two distinct target triples intersect in at most one element.  The index shifts in `D_4,D_5,D_6` are essential here.

Between two different gadgets, the only possible shared elements are global boundary elements `x` or `x'`.  Every target triple contains at most one boundary element.  Therefore two target triples belonging to different gadgets can share at most one element.

Hence the target hypergraph is linear.

Equivalently, in the Exact-One incidence matrix any two source rows overlap in at most one column.

## 7. Exact local state theorem

Treat the six boundary elements

```text
B_j={x_1,x_2,x_3,x'_1,x'_2,x'_3}
```

as ports and require every internal element of the gadget to be covered exactly once, while boundary elements are allowed to be covered zero or one times locally.

An exhaustive exact finite check gives exactly eight internal exact-cover states.  Their boundary signatures are only

```text
EMPTY,
{x_1,x_2,x_3},
{x'_1,x'_2,x'_3},
{x_1,x_2,x_3,x'_1,x'_2,x'_3}.
```

There is no valid local state that covers a nonempty proper subset of either source triple.

For completeness, the eight states can be written explicitly:

```text
1. L'_1,L'_2,L'_3,D_1,D_2,D_3
   signature C'_j

2. L'_4,L'_5,D_1,D_2,D_3
   signature EMPTY

3. L_1,L_2,L_3,D_4,D_5,D_6
   signature C_j

4. L_4,L_5,D_4,D_5,D_6
   signature EMPTY

5. L_1,L_2,L_3,L'_1,L'_2,L'_3,D_7
   signature C_j union C'_j

6. L_4,L_5,L'_1,L'_2,L'_3,D_7
   signature C'_j

7. L_1,L_2,L_3,L'_4,L'_5,D_7
   signature C_j

8. L_4,L_5,L'_4,L'_5,D_7
   signature EMPTY.
```

This finite gadget lemma is independently replayable by the companion checker; the global reduction proof below uses only the four-signature consequence.

## 8. Forward direction

Assume the RXC3 instance has an exact cover indexed by `J*`.

For each source triple `C_j`:

If `j in J*`, select

```text
L_1,L_2,L_3,
L'_1,L'_2,L'_3,
D_7.
```

If `j not in J*`, select

```text
L_4,L_5,
L'_4,L'_5,
D_7.
```

Every internal gadget element is covered exactly once.

Because `J*` is an exact cover, every global boundary element `x` is covered by exactly one selected source gadget.  The primed copy uses the same `J*`, so every `x'` is also covered exactly once.

Hence the target instance has an exact cover.

## 9. Reverse direction

Assume the target instance has an exact cover.

Restrict it to each gadget.  By the exact local state theorem, on the unprimed boundary a gadget covers either

```text
none of C_j
```

or

```text
all three elements of C_j.
```

Let `J` be the set of source triples whose gadget covers its unprimed boundary triple.

Every original boundary element `x` must be covered exactly once in the global target exact cover.  Therefore among the three source gadgets incident to `x`, exactly one belongs to `J`.

Thus

```text
{C_j : j in J}
```

is an exact cover of the original RXC3 instance.

(The primed layer independently induces another exact cover; it is redundant for logical equivalence but is what allows all internal degrees to be raised to exactly three while preserving linearity.)

Therefore

```text
RXC3 SAT  iff  target square+cubic+linear Exact-One SAT.
```

## 10. Complexity conclusion

The construction has constant size per source triple, so it is polynomial time.

The target problem is in NP because a selected set / Boolean vector is directly checkable.

Therefore:

```text
SQUARE + CUBIC + LINEAR EXACT-ONE IS NP-COMPLETE.
```

In matrix language:

```text
Given A in {0,1}^{n x n}
with row-sum=3,
column-sum=3,
and pairwise row intersections <=1,
deciding whether there exists x in {0,1}^n with A x = 1
is NP-complete.
```

## 11. Consequence for the JANUS route

For this linear class,

```text
A^T A = 3I + Adj(G_A),
```

so

```text
nullity_Q(A) = multiplicity_{G_A}(-3).
```

R5 E10/E11 therefore did not narrow the problem into a potentially easy subclass: the exact spectral class currently under attack is already NP-complete.

Hence a deterministic polynomial algorithm that closes the remaining

```text
large rational nullity / large -3 eigenspace
```

branch for this class would imply

```text
P = NP.
```

This is now an explicit theorem-level bridge, not an assumption.

## 12. Current frontier

The target can now be frozen without fear of losing universality:

```text
INPUT:
  square 0/1 incidence matrix A,
  row sum = column sum = 3,
  pairwise row overlap <= 1.

DECIDE:
  ker_Q(A) intersects {-1,2}^n ?
```

because

```text
A x = 1, x in {0,1}^n
iff
A(3x-1)=0, 3x-1 in {-1,2}^n.
```

Known exact polynomial/FPT terminals remain:

```text
rank full -> UNSAT;
small nullity d -> O(2^d poly(n));
clique LP infeasible -> UNSAT;
decomposition terminals -> recurse.
```

The unresolved universal branch is still:

```text
large nullity,
clique LP feasible,
connected/nondecomposed source.
```

P_VS_NP = OPEN.
