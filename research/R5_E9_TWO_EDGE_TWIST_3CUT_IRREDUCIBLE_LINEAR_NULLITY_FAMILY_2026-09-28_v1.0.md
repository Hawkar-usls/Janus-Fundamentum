# R5 E9 — Two-Edge-Twist 2-Lift: 3-Cut-Irreducible Unbalanced SAT Family with Linear Rational Nullity

Date: 2026-09-28

Status:
`JANUS_DERIVED_ARBITRARY_N_STRUCTURAL_FALSIFIER__CURRENT_RESIDUAL_LOW_NULLITY_ROUTE_CLOSED__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE FALSIFIES THE PROPOSED SHORTCUT
  3-CUT-IRREDUCIBLE + UNBALANCED => nu_Q(A)=O(log n).

IT DOES NOT PROVIDE A UNIVERSAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `R5_E9_THREE_EDGE_CUT_BOUNDARY_ALGEBRA_2026-09-28_v1.0.md`
- `R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`
- `R5_E9_ONE_EDGE_TWIST_2LIFT_DISSOCIATED_NULLITY_AMPLIFIER_2026-09-27_v1.0.md`
- `R5_E9_ONE_EDGE_TWIST_2LIFT_EXACT_SAT_CONTRACTION_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_two_edge_twist_3cut_irreducible_nullity.py`

## 1. Base configuration: the doily `GQ(2,2)`

Let the 15 columns be the 2-subsets of

```text
Omega={0,1,2,3,4,5}.
```

Let the 15 rows be the perfect matchings of `K_6` (partitions of `Omega` into three unordered pairs). Put

```text
A_0[M,e]=1  iff  e belongs to perfect matching M.
```

Every row contains exactly three pairs. Every pair belongs to exactly three perfect matchings of the remaining four points. Hence `A_0` is a square `15 x 15` cubic incidence matrix.

Two distinct perfect matchings cannot share two distinct edges: two shared disjoint pairs force the third pair. Therefore two rows share at most one column, so the carrier is linear.

Its Levi graph is the classical incidence graph of `GQ(2,2)` (the Tutte-Coxeter graph), but no external geometry theorem is needed for the algebra below.

## 2. Exact rational nullity of the base

Index the 15 columns by edges of `K_6`. Then

```text
A_0^T A_0 = 3 I + D,
```

where `D` is the adjacency matrix of the disjointness graph on 2-subsets of `Omega` (`KG(6,2)`).

For every ground vertex `a`, let `z_a` be the edge-indicator of the star at `a`. Then

```text
D z_a = 3(1-z_a).
```

Therefore

```text
y_a = z_a - (1/3)1
```

satisfies

```text
D y_a = -3 y_a.
```

The six vectors `y_a` have one relation `sum_a y_a=0`, and the five differences `y_a-y_5` are independent. Thus `-3` has multiplicity at least five.

Let `W` be the subspace of edge-vectors whose sum on every `K_6` star is zero. The six star-sum equations are independent over `Q` because the unoriented vertex-edge incidence matrix of non-bipartite `K_6` has full row rank six, hence `dim W=15-6=9`.

For `w in W`, the total edge sum is zero and for an edge `ij` the sum of `w` over edges disjoint from `ij` equals `w_ij`; hence

```text
D w = w.
```

Finally `D 1 = 6 1`. Therefore the complete spectrum decomposition is

```text
D : 6^(1), 1^(9), (-3)^(5),
A_0^T A_0 : 9^(1), 4^(9), 0^(5).
```

So

```text
rank_Q(A_0)=10,
nu_Q(A_0)=5.
```

## 3. Base SAT witness

Fix any ground vertex `a in Omega` and select the five pair-columns incident with `a`.

Every perfect matching of `K_6` contains exactly one edge incident with `a`. Hence this star is an Exact-One witness.

Thus `A_0` is SAT.

## 4. Base unbalanced certificate

The following five rows and five pair-columns form the forbidden odd cycle matrix

Rows:

```text
((0,2),(1,5),(3,4))
((0,1),(2,5),(3,4))
((0,4),(1,3),(2,5))
((0,5),(1,3),(2,4))
((0,3),(1,5),(2,4))
```

Columns in order:

```text
(3,4), (2,5), (1,3), (2,4), (1,5).
```

The induced `5 x 5` submatrix is

```text
1 0 0 0 1
1 1 0 0 0
0 1 1 0 0
0 0 1 1 0
0 0 0 1 1
```

so every selected row and column has degree two and the order is odd. Equivalently the Levi graph contains a chordless 10-cycle. Hence `A_0` is unbalanced and is not removed by the balanced terminal.

## 5. Super-edge-connected / 3-cut-irreducible convention

Call a connected cubic graph **3-cut-irreducible** here when

```text
no edge cut of size 1 or 2 exists,
and every 3-edge cut is the star delta(v) of one vertex.
```

The base doily Levi graph has this property. The executable checker verifies all `1`, `2`, and `3` edge subsets exactly:

```text
#1-cuts = 0
#2-cuts = 0
#3-cuts = 30
all 3-cuts isolate exactly one of the 30 Levi vertices.
```

For the arbitrary-size theorem below, only this stated base property is used.

## 6. Two-edge-twist signing

Let `G` be any cubic 3-cut-irreducible Levi graph. Choose two **nonadjacent** incidence edges `e,f`.

Define a 2-lift in which exactly `e,f` are crossed and every other incidence is parallel.

Equivalently, for the square incidence matrix `A`, let `E` have ones in exactly those two incidence positions and zeros elsewhere, put

```text
P=A-E,
```

and define

```text
Ahat = [ P  E
         E  P ].
```

The signed block is

```text
S=P-E=A-2E.
```

### Lemma TET-1 — frustration index is exactly two

Switching a signed graph adds a cut vector modulo two to the negative-edge set.

The two-edge support `{e,f}` cannot switch to zero negatives, because that would make `{e,f}` a 2-edge cut.

It cannot switch to one negative edge `g`:

- if `g` equals `e` or `f`, the symmetric difference is a 1-edge cut;
- otherwise `{e,f,g}` would be a 3-edge cut, hence a vertex star by 3-cut irreducibility, forcing `e,f` to be adjacent at that vertex, contrary to construction.

Thus the minimum number of negative edges over the switching class is exactly two.

In particular the signing is unbalanced and the 2-lift is connected.

## 7. Preservation of 3-cut irreducibility

### Theorem TET-2

If `G` is cubic and 3-cut-irreducible and the lift signing has frustration index at least two, then the connected 2-lift `Ghat` is again 3-cut-irreducible.

### Proof

Take any nonempty proper vertex set `S` in `Ghat`. For each base vertex classify its two lifts as:

```text
0 : neither lift lies in S,
2 : both lifts lie in S,
1 : exactly one lift lies in S.
```

Let `U` be the set of base vertices of type `1`.

Every base edge with exactly one endpoint in `U` contributes exactly one lifted edge to `delta_Ghat(S)`, independent of its sign. Therefore

```text
|delta_Ghat(S)| >= |delta_G(U)|.
```

If `U` is empty, `S` is a union of full fibers and every crossing base edge contributes two lifted cut edges. Any nontrivial such cut has size at least `2*3=6`.

If `U=V(G)`, the choice of one lift in each fiber is a switching assignment. The lifted cut size is twice the number of frustrated base edges in that switching, hence at least `2*frustration >=4`.

Assume now `U` is nonempty and proper and the lifted cut has size at most three. Then

```text
|delta_G(U)| <=3.
```

By base 3-cut irreducibility, equality is three and one shore of the base cut is a single vertex.

If `U={v}`, there can be no additional lifted crossing edges. Since a 3-edge-connected cubic graph has no cut vertex, `G-v` is connected, so every unsplit fiber outside `v` must be in the same `0` or `2` state. Therefore `S` is exactly one lifted vertex, or its complement. The cut is a vertex star.

If `U=V(G)-{v}`, absence of extra crossings means the signing is balanced on `G-v`. After switching on `G-v`, all negative edges lie among the three edges incident with `v`. Switching at `v` replaces `r` negative incident edges by `3-r`, so the global frustration index is at most one. This contradicts the assumed frustration index at least two.

Hence every cut of size at most three in `Ghat` is a vertex star. QED.

Combining TET-1 and TET-2, every two-edge-twist by nonadjacent edges preserves the current 3-cut-irreducible residual condition.

## 8. Rational-nullity amplification

Over `Q`, the symmetric/antisymmetric change of coordinates block-diagonalizes the lift:

```text
Ahat ~ diag(A,S),
S=A-2E.
```

Therefore

```text
nu_Q(Ahat)=nu_Q(A)+nu_Q(S).
```

Because `E` has exactly two nonzero entries,

```text
rank(E)<=2,
rank(S)<=rank(A)+2,
```

and hence

```text
nu_Q(S)>=nu_Q(A)-2.
```

Thus

```text
boxed( nu_Q(Ahat) >= 2 nu_Q(A) - 2 ).
```

## 9. Preservation of cubic-linearity, SAT, and unbalancedness

A graph 2-cover preserves degree and bipartiteness. A cover cannot create a new 4-cycle when the base has no 4-cycle, so linearity of the cubic hypergraph is preserved.

SAT lifts diagonally: if

```text
A x = 1
```

for Boolean `x`, then for every signing

```text
Ahat (x,x)^T = (1,1)^T.
```

To preserve unbalancedness, fix one chordless Levi 10-cycle and at every lift choose the two crossed edges outside that cycle. Its signing parity is then zero, so the 10-cycle lifts to two disjoint 10-cycles. Either copy may be frozen as the designated cycle for the next stage.

There always exist two nonadjacent incidence edges outside the designated 10-cycle: a cubic Levi graph at every level has at least 45 edges, only ten of which lie on the designated cycle, and in a simple bipartite graph a pairwise-intersecting edge set is a star of size at most three.

Hence the recursion can continue indefinitely.

## 10. Infinite current-residual family

Start from the doily `A_0`. At stage `t`, choose two nonadjacent incidences outside the designated lifted 10-cycle and form the two-edge-twist lift `A_{t+1}`.

Then for every `t>=0`:

```text
n_t = 15 * 2^t,
connected = true,
cubic = true,
linear = true,
SAT = true,
unbalanced = true,
no nontrivial edge cut of size <=3 = true.
```

Let `k_t=nu_Q(A_t)`. Since `k_0=5` and

```text
k_{t+1} >= 2 k_t - 2,
```

putting `h_t=k_t-2` gives `h_{t+1}>=2h_t`, `h_0=3`. Therefore

```text
boxed(
k_t >= 3*2^t + 2
    = n_t/5 + 2.
)
```

This is an explicit infinite family **inside the current separator-resistant unbalanced residual** with linear rational nullity.

### Corollary TET-3

The proposed residual theorem

```text
3-cut-irreducible + unbalanced linear-cubic
=> nu_Q(A)=O(log n)
```

is false.

The low-nullity enumeration router remains valid as a terminal when low nullity happens, but low nullity cannot be the universal residual currency.

## 11. Finite executable replay

The checker constructs `A_0` from the 15 perfect matchings of `K_6` and verifies:

```text
base rank_Q=10, nullity_Q=5,
base SAT witness,
base forbidden 5x5 odd-cycle submatrix,
base 1-cuts=0, 2-cuts=0, 3-cuts=30 and all are vertex stars.
```

It chooses two nonadjacent incidences outside the fixed 10-cycle, builds the first 2-lift, and verifies exactly:

```text
n_1=30,
rank_Q=22,
nullity_Q=8,
connected/cubic/linear,
diagonal SAT witness,
fixed 10-cycle lifts,
1-cuts=0, 2-cuts=0, 3-cuts=60 and all are vertex stars.
```

It also builds a second canonical lift and verifies

```text
n_2=60,
nullity_Q=14,
```

matching the recurrence lower bound with equality on these first levels.

Finite replay is regression evidence only; the arbitrary-size conclusion is Sections 6--10.

## 12. Updated frontier

Freeze:

```text
R5_E9_RESIDUAL_LOW_NULLITY_AFTER_3CUT_BALANCED_PREPROCESSING
= FALSIFIED.
```

The universal solver must therefore use a currency that can handle

```text
3-cut-irreducible
+ unbalanced
+ SAT
+ rational nullity Theta(n)
```

without enumerating the rational/binary kernel.

The primary strong-odd-cycle transfer-composition gate remains open. This family is now a mandatory hostile replay for every proposed cycle-transfer / syndrome-compression theorem.

## 13. Ceiling

```text
DOILY BASE nu_Q = 5                         = PROVED
DOILY BASE SAT                              = PROVED
DOILY BASE UNBALANCED                       = EXPLICIT 5x5 ODD CYCLE
DOILY BASE 3-CUT-IRREDUCIBLE                = EXACTLY CHECKED

TWO NONADJACENT TWISTS FRUSTRATION          = 2
3-CUT-IRREDUCIBILITY UNDER SUCH 2-LIFT      = PROVED
NULLITY RECURRENCE k' >= 2k-2               = PROVED
SAT / LINEARITY / UNBALANCEDNESS PRESERVED  = PROVED

INFINITE RESIDUAL FAMILY
n_t=15*2^t, nu_Q>=n_t/5+2                   = PROVED

RESIDUAL O(log n) NULLITY SHORTCUT          = FALSIFIED
UNIVERSAL POLYNOMIAL DECIDER                = OPEN
E8_D1                                       = EMPTY
P_VS_NP                                     = OPEN
```