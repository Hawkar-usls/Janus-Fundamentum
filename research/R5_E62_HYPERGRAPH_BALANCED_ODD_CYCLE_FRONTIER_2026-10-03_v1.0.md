# R5 E62 — Hypergraph Matching / Balanced Strong-Odd-Cycle Frontier

Date: 2026-10-03

Status:
`EXACT_ONE_IS_PERFECT_MATCHING__BALANCED_IMPLIES_SAT__STRONG_TRIANGLES_AFFINE__FIRST_NONAFFINE_ODD_CYCLE_LENGTH_5`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT REEXPRESSES THE POST-E61 HARD CORE AS PERFECT MATCHING IN A
3-UNIFORM 3-REGULAR LINEAR HYPERGRAPH, IDENTIFIES BALANCEDNESS AS AN EXACT
POLYNOMIAL INTEGRALITY REGION, AND DERIVES THE COMPLETE INTERFACE SIGNATURE
OF A STRONG ODD CYCLE.

EVERY SUCH HYPERGRAPH HAS THE CANONICAL FRACTIONAL PERFECT MATCHING

    z_e = 1/3.

IF THE HYPERGRAPH IS BALANCED, CLASSICAL BERGE/LOVASZ THEORY MAKES THE
SET-PARTITION POLYTOPE INTEGRAL; IN THE 3-REGULAR CASE THE EDGE SET EVEN
DECOMPOSES INTO THREE PERFECT MATCHINGS.  HENCE BALANCED => SAT.

THEREFORE EVERY UNSAT INSTANCE MUST CONTAIN A STRONG ODD CYCLE.

A STRONG ODD CYCLE OF LENGTH l HAS AN EXACT EXTERNAL SIGNATURE R_l IN
BIJECTION WITH THE INDEPENDENT SETS OF THE ORDINARY CYCLE C_l, SO

    |R_l| = L_l

WHERE L_l IS THE l-TH LUCAS NUMBER.

FOR l=3,

    R_3 = {001,010,100,111}

IS JUST XOR=1 AND CAN BE ABSORBED AFFINELY.

FOR l=5, |R_5|=11 AND R_5 IS NOT AFFINE.  THUS LENGTH 5 IS THE FIRST
STRONG-ODD-CYCLE INTERFACE THAT CANNOT BE REPLACED BY PURE GF(2) GAUSSIAN
ELIMINATION.

A SECOND EXACT SOLVER FOLLOWS: GIVEN t HYPEREDGES WHOSE DELETION MAKES THE
HYPERGRAPH BALANCED, PERFECT MATCHING CAN BE DECIDED IN 2^t * poly(n).

P_VS_NP = OPEN.
```

## 1. Exact-One is a hypergraph perfect matching problem

Let `A` be a square `n x n` 0/1 matrix with every row and every column of
weight 3.  Build the dual incidence hypergraph

```text
H_A=(R,E),
R = row indices,
e_j = { i : A_ij=1 } for every column j.
```

Then every hyperedge has size 3 because every column has weight 3, and every
vertex of `H_A` has degree 3 because every row has weight 3.

If the carrier is linear, any two columns of `A` meet in at most one row, so any
two hyperedges of `H_A` intersect in at most one vertex.  Therefore the E61
linear class becomes exactly

```text
3-uniform + 3-regular + linear hypergraphs.
```

For a Boolean vector `x`, let

```text
M={e_j : x_j=1}.
```

The integer equations

```text
A x = 1
```

say exactly that every row vertex lies in one selected hyperedge.  Hence the
selected hyperedges are pairwise disjoint and cover all row vertices:

```text
boxed:
Exact-One(A)
iff
H_A has a perfect matching.
```

This is the same hard object seen in E58/E61 through a different global lens.
It is not a known automatic polynomial closure: perfect matching is NP-complete
for 3-uniform hypergraphs, and the literature contains NP-hardness reductions
already for linear 3-uniform hypergraphs.

Useful external anchor:

* Han et al., "The complexity of almost perfect matchings and other packing
  problems in uniform hypergraphs with high codegree", European Journal of
  Combinatorics 33 (2012).  The paper explicitly uses the problem `PM_lin(3)`,
  perfect matching restricted to linear 3-uniform hypergraphs, in an
  NP-completeness reduction.

## 2. The canonical fractional perfect matching

Because every row has exactly three 1s,

```text
z = (1/3) * 1
```

always satisfies

```text
A z = 1,
z >= 0.
```

Thus every square-cubic carrier has a canonical fractional perfect matching.
The universal decision problem is therefore an integrality question:

```text
Does the nonempty set-partition polytope

    P(A)={z>=0 : A z=1}

contain a 0/1 point?
```

This is the hypergraph version of the gap between the easy fractional object and
the hard integral matching.

## 3. Balanced hypergraphs are an exact polynomial SAT region

A 0/1 matrix is balanced when it contains no square submatrix of odd order with
exactly two 1s in every row and every column.  Equivalently, its hypergraph has
no strong odd cycle.

Classical Berge/Lovasz/Fulkerson-Hoffman-Oppenheim theory gives, for a balanced
hypergraph, integrality of the set-partition polytope

```text
{z>=0 : A z=1}.
```

Since our polytope is never empty (`z=1/3` is always feasible), balancedness
immediately implies the existence of an integral point and therefore an
Exact-One solution.

There is also a purely combinatorial route.  Balanced hypergraphs satisfy the
colored-edge property: their edge chromatic number is their maximum degree.  A
3-regular balanced hypergraph therefore has a proper 3-edge-coloring.  At every
vertex the three incident edges have the three different colors, so each color
class hits every vertex exactly once.  Consequently

```text
boxed:
3-regular balanced H_A
=> E(H_A) decomposes into three perfect matchings
=> Exact-One(A) is SAT.
```

In particular this produces not merely one witness but three disjoint Exact-One
witnesses whose column sets partition all columns.

Literature anchors:

* Conforti, Cornuejols, Kapoor, Vuskovic, "Perfect, ideal and balanced
  matrices", European Journal of Operational Research 133 (2001), 455-461.
  Balancedness is reviewed as the hypergraph generalization of bipartiteness;
  balanced matrices have integral packing/covering behavior, and balancedness
  is polynomially recognizable.
* Beckenbach, "Matchings in balanced hypergraphs" (open manuscript/thesis),
  Theorem 2.36 records the Lovasz/FHO integrality of
  `{y>=0:Ay=1}`, and the regular balanced case decomposes into edge-disjoint
  perfect matchings.  The manuscript also notes constructive polynomial
  coloring/matching algorithms.

Therefore

```text
boxed:
UNSAT => H_A is unbalanced => H_A contains a strong odd cycle.
```

The converse is false: SAT12 below is unbalanced and still has a perfect
matching.  Strong odd cycles are an integrality obstruction family, not an
automatic UNSAT certificate.

## 4. Exact transfer relation of one strong odd cycle

Let

```text
C=(v_0,e_0,v_1,e_1,...,v_(l-1),e_(l-1),v_0)
```

be a strong cycle in the 3-regular hypergraph `H_A`.  At cycle vertex `v_i`,
the two cycle hyperedges are `e_(i-1)` and `e_i`.  Because the vertex degree is
3, there is exactly one third incident hyperedge; call it `f_i`.

Let

```text
c_i = 1 iff cycle edge e_i is selected,
s_i = 1 iff external edge f_i is selected.
```

The perfect-matching equation at `v_i` is exactly

```text
c_(i-1) + c_i + s_i = 1.                  (1)
```

Equation (1) gives two immediate facts.

First, adjacent cycle edges can never both be selected, so `c` is an independent
set of the ordinary cycle graph `C_l`.

Second, once `c` is fixed,

```text
boxed:
s_i = 1 - c_(i-1) - c_i.                 (2)
```

Conversely every independent set `c` of `C_l` makes the right side of (2)
Boolean and satisfies all cycle-vertex equations.  Hence the complete external
interface relation is

```text
R_l = {
  s in {0,1}^l :
  exists an independent set c of C_l with
  s_i=1-c_(i-1)-c_i
}.
```

If some external hyperedge `f_i` occurs at several cycle vertices, the
corresponding interface coordinates are simply identified as the same global
Boolean variable.  The local transfer theorem itself is unchanged.

### Odd cycles: injectivity and Lucas count

For odd `l`, the map `c -> s` is injective.  If `c,c'` have the same interface,
then

```text
d_(i-1)+d_i=0,
d_i=c_i-c'_i.
```

Thus the `d_i` alternate sign around the cycle.  Odd length forces `d=0`.
Therefore

```text
boxed:
|R_l| = number of independent sets of C_l = Lucas(l)
```

for every odd `l`.

The replay checker obtains

```text
l=3 :  4 states
l=5 : 11 states
l=7 : 29 states
l=9 : 76 states.
```

## 5. Strong triangles are affine; length 5 is the first non-affine interface

For `l=3`, direct elimination gives

```text
R_3={001,010,100,111}.
```

This is exactly

```text
boxed:
s_0 XOR s_1 XOR s_2 = 1.
```

So a single strong triangle can be removed from the Exact-One constraints and
replaced by one affine GF(2) equation, with no branching.

This sharpens the post-E61 target: the mere existence of strong triangles is
not yet a non-linear barrier.  Their local interface is already Gaussian.

For `l=5`, `R_5` contains 11 states.  It is not an affine relation over GF(2).
For example the three allowed states

```text
00001,
00010,
01000
```

have ternary XOR

```text
01011,
```

which is not in `R_5`.  Any affine relation is closed under ternary XOR, so this
is an exact non-affinity witness.

Thus

```text
boxed:
strong 3-cycle  -> affine interface,
strong 5-cycle  -> first non-affine strong-odd-cycle interface.
```

This does not prove that every hard instance can be reduced to independent
5-cycles.  Interactions and overlaps among strong odd cycles can carry the
remaining complexity.  It does prove that a universal method based solely on
"find an odd cycle and Gaussian-eliminate it" stops no later than the 5-cycle
signature unless it uses additional global structure.

## 6. Exact FPT solver from a balanced edge modulator

E62 gives a second exact parameterized algorithm, orthogonal to E61's real
nullity parameter.

Suppose a set of hyperedges

```text
F subset E(H)
```

is supplied such that

```text
H-F
```

is balanced, and write `t=|F|`.

Enumerate every subset `M subset F`.

* Reject `M` immediately if two edges of `M` intersect.
* Let `U` be the vertices covered by `M`.
* Delete `U`, delete all edges of `F`, and from `H-F` retain only hyperedges
  disjoint from `U`.

Call the resulting residual hypergraph `H_M`.  It is a partial subhypergraph of
`H-F`, hence it is balanced because balancedness is hereditary under deleting
vertices and edges.

Now test in polynomial time whether `H_M` has a perfect matching using balanced
hypergraph matching machinery.

The equivalence is exact:

* if `N` is a perfect matching of `H`, choose `M=N intersect F`; then `N-M` is a
  perfect matching of `H_M`;
* if `M` and a perfect matching `N_M` of `H_M` exist, then `M union N_M` is a
  perfect matching of `H`.

Therefore, given a balanced edge modulator of size `t`,

```text
boxed:
T(n,t) = 2^t * poly(n).
```

In particular the problem is polynomial when `t=O(log n)`.

This is not a universal closure.  E62 does not prove that every hard carrier has
a logarithmic balanced modulator, nor does it claim a polynomial algorithm for
finding a minimum such modulator.

## 7. Replay controls

The companion checker uses the two frozen linear `n=12` carriers from E61.

For each carrier it verifies:

```text
* dual H_A is 3-uniform, 3-regular and linear;
* Exact-One witnesses are exactly hypergraph perfect matchings;
* z=1/3 is a fractional perfect matching;
* an explicit strong 3-cycle exists;
* an explicit strong 5-cycle exists.
```

The controls are deliberately opposite:

```text
SAT12        : one perfect matching,
UNSAT12_E57  : zero perfect matchings.
```

Both contain strong odd cycles, demonstrating that unbalancedness is necessary
for UNSAT but not sufficient for it.

The generic cycle replay independently verifies `R_l` against brute force for
`l=3,5,7,9`, checks the Lucas counts, proves `R_3=XOR=1`, and freezes the
non-affinity witness for `R_5`.

Companion checker:

```text
experiments/r5_e62_hypergraph_balanced_odd_cycle_frontier.py
```

## 8. New universal frontier

E61 said that the hard discrete step is

```text
ker_R(A) intersect {-1,2}^n.
```

E62 identifies the same obstruction polyhedrally and combinatorially:

```text
canonical fractional perfect matching 1/3
        |
        v
balanced region -> integral -> SAT
        |
        v
unbalanced residual = interacting strong odd cycles
        |
        +-- strong triangles: affine, eliminable by XOR
        |
        +-- strong 5+ cycles: non-affine interfaces begin
```

The next high-value question is therefore:

```text
Can the network of non-affine strong-odd-cycle interfaces in a
3-uniform 3-regular linear hypergraph be compressed without exponential
branching, using the overlap constraints forced by degree 3 and linearity?
```

Equivalently, can one prove that the global interaction graph of the `R_5,R_7,...`
interfaces has a polynomially exploitable structure on every square-cubic-linear
carrier?

Until such a theorem is proved:

```text
P_VS_NP = OPEN.
```
