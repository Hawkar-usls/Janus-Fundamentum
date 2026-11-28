# Parity route — Trade smooth-count / separator frontier

Date: 2026-10-09

Predecessor main SHA:
`e7d6790d533f9acd3c4fe7f2439542dfbfa3361c`

Branch:
`research/parity-isolation-trade-checkpoint-20261009`

Scientific ceiling:

```text
THIS CHECKPOINT DOES NOT PROVE A POLYNOMIAL ISOLATING FAMILY.
IT DOES NOT PROVE A POLYNOMIAL PARITY SOLVER.
IT DOES NOT PROVE P=NP.

P_VS_NP = OPEN.
```

This checkpoint sharpens the deterministic parity/isolation route from
`proof_attempts/PARITY_ISOLATION_TRADE_CHECKPOINT_2026-10-09.md`.

It also cross-checks the route against the admitted mainline frontier:

* E109-E111: direct-sum / branch-DP / constructible low-width terminals;
* E112: generic high-connectivity cubic normal geometry alone is insufficient;
* E116: faithful cographic 3-cuts give exact width-2 separators;
* E118: satisfiability hardness bridge, but its 9-clause equality gadget is not parsimonious at boundary 000;
* E119: perfect conflict graphs are already a complete polynomial terminal.

The present route is therefore specifically about deterministic isolation / parity on the
remaining all-input target, not a replacement for E119.

## 1. Conflict graph

Let H be a square, 3-uniform, 3-regular, linear hypergraph representing the
Positive Exact-One instance:

* hypergraph vertices = clauses;
* hyperedges = variables;
* a perfect matching of H = a satisfying Exact-One assignment.

Let G be the conflict graph on E(H): two variables are adjacent iff they share
a clause.

Because H is 3-uniform, 3-regular and linear:

* G is simple and 6-regular;
* every clause produces one triangle;
* every conflict edge belongs to exactly one clause triangle.

This is the same conflict graph used by E119.

## 2. Exact local-trade characterization

### Theorem

For a nonempty set U of variables, the following are equivalent.

A. U is the support of a connected local Exact-One trade: there is a
bipartition

```text
U = P disjoint_union Q
```

such that P and Q are disjoint partial exact covers of exactly the same set of
clauses, and the trade is connected.

B. The induced conflict graph G[U] is connected, cubic and bipartite.

### A => B

Take the bipartition P,Q.

A variable in P covers three clauses.  In each of those clauses Q contains
exactly one variable, because Q covers exactly the same clause set exactly once.
Hence every P-variable has exactly three Q-neighbours.  Symmetrically every
Q-variable has degree three.

There are no P-P or Q-Q conflict edges because each side is a partial matching.

Thus G[U] is cubic and bipartite; connectedness is the connected-trade
assumption.

### B => A

Let P,Q be the bipartition of the connected cubic graph G[U].

Fix u in U.  The three clauses containing u correspond to three edge-disjoint
triangles through u in the full conflict graph.

Because G[U] is bipartite, at most one other U-variable can occur with u in
any one of those clause triangles; otherwise G[U] would contain a triangle.

But u has degree three in G[U], so exactly one U-neighbour occurs in each of
its three clauses.

The neighbour is always on the opposite bipartition side.  Therefore P and Q
each cover every active clause exactly once and cover the same active clause
set.

So P,Q form a local trade.

### Consequence

Connected trade supports can be recognized and enumerated without knowing any
global perfect matching.

This is important for isolation: we may safely hash all local trades, an
over-approximation of the trades that are actually relevant to a particular
minimum face.

Status:

```text
CONNECTED_CUBIC_BIPARTITE_TRADE_CHARACTERIZATION = PROVED_LOCALLY
```

## 3. Polynomial smooth-count for logarithmic trades

Let N=|E(H)|=|V(G)|.

The maximum degree of G is six.

For any fixed root and support size k, the number of connected k-vertex sets
containing the root is at most

```text
(4 Delta)^(k-1) = 24^(k-1).
```

One elementary over-count is:

* choose a rooted plane spanning-tree shape (fewer than 4^(k-1) choices);
* for each tree edge choose one of at most Delta=6 neighbours of its parent.

Collisions and duplicate encodings only increase the over-count.

Hence the total number of connected supports of size at most 2L is bounded by

```text
N * sum_{k<=2L} 24^(k-1) < N * 24^(2L).
```

Every volume-r connected trade has support size 2r.

Therefore for

```text
L = C log_2 N
```

with any fixed constant C, all connected trades of volume at most L form a
polynomial-size family

```text
|D_L| <= N^(1 + 2 C log_2 24) * O(1).
```

They can be enumerated in polynomial time for fixed C by standard
bounded-degree connected-set generation and filtered by the theorem in
Section 2.

External near-neighbour:

Kangas, Kaski, Korhonen, Koivisto,
"On the Number of Connected Sets in Bounded Degree Graphs",
Electronic Journal of Combinatorics 25(4), P4.34 (2018),
DOI 10.37236/7462.

The bound above is intentionally elementary and weaker; it is sufficient for
the polynomial conclusion.

Status:

```text
LOGARITHMIC_TRADE_SMOOTH_COUNT = PROVED_LOCALLY
```

## 4. Deterministic bounded hash killing every short trade

Orient one bipartition of every enumerated trade U and let

```text
d_U in {-1,0,1}^N
```

be +1 on one side, -1 on the other, 0 outside.

Let D=D_L and choose a prime

```text
p > (N-1)|D|,  p>2.
```

For t in F_p define integer weights

```text
w_t(i) = t^i mod p,   0 <= w_t(i) < p.
```

For a nonzero trade vector d define

```text
f_d(t) = sum_i d_i t^i  in F_p.
```

Because p>2 and d is nonzero, f_d is a nonzero polynomial of degree <N.
It has at most N-1 roots.

The union of the root sets of all d in D has size strictly less than p.
Therefore scanning t in F_p deterministically finds one value satisfying

```text
< w_t, d > != 0 mod p
```

for every d in D.

In particular every corresponding ordinary integer circulation is nonzero.

Since |D| is polynomial for L=C log N, p and every weight are
N^{O_C(1)}.  A suitable prime can be found deterministically in polynomial
time.

### Minimum-face consequence

Fix the resulting weight w.

If M and N are two minimum-weight perfect matchings, every connected component
of M xor N has zero weight circulation individually: a negative component
could be flipped to improve M, while all component changes sum to zero.

But w has nonzero circulation on every connected trade of volume <=L.

Hence:

```text
every connected difference component between two w-minimum matchings
has volume > C log N.
```

This gives a one-shot deterministic logarithmic trade purge using polynomially
bounded weights.

It does NOT imply that the minimum face is a singleton.

Status:

```text
DETERMINISTIC_LOG_TRADE_PURGE = PROVED_LOCALLY
FULL_ISOLATION = OPEN
```

## 5. Arbitrary cubic-bipartite trade realization

The separator side needs a firewall: a large trade need not possess a small
separator.

### Theorem

Let B=(L union R,E_B) be any connected simple cubic bipartite graph with

```text
|L|=|R|=r
```

and r divisible by three.

Then there is a square, 3-uniform, 3-regular, linear hypergraph H_B with two
perfect matchings M and N whose single connected symmetric-difference trade
graph is exactly B.

### Construction

Take the vertices of H_B to be the edges of B.

For every l in L add one hyperedge consisting of the three B-edges incident
with l.  These r hyperedges form M.

For every r-vertex in R add its three-edge star.  These r hyperedges form N.

Because B is cubic bipartite, its edges decompose into three 1-factors

```text
F1,F2,F3.
```

Partition each Fi into triples.  Since r is divisible by three this produces
r additional triples in total; call the resulting family P.

Every triple inside one Fi is a matching in B.

Now:

* |V(H_B)|=|E(B)|=3r;
* |E(H_B)|=r+r+r=3r, so H_B is square;
* every H_B vertex (one B-edge) lies in exactly one L-star, one R-star and one
  P-triple, so H_B is 3-regular;
* every H_B hyperedge has size three;
* two L-stars are disjoint, as are two R-stars and two P-triples;
* an L-star and R-star meet in at most one B-edge because B is simple;
* a P-triple meets any L-star or R-star in at most one edge because it is a
  matching in B.

Therefore H_B is linear.

M, N and P are all perfect matchings of H_B.

The conflict graph induced on M union N is exactly B.  Thus M xor N is one
connected trade with trade graph B.

Status:

```text
ARBITRARY_CUBIC_BIPARTITE_TRADE_REALIZATION = PROVED_LOCALLY
```

## 6. Expander obstruction to a naive separator theorem

There are infinite families of cubic bipartite expanders.  In bounded-degree
graphs, expansion, linear-size separators and linear treewidth are tightly
related.

Choose such a family B_r with r divisible by three and apply Section 5.

Then H_{B_r} contains two perfect matchings whose connected trade graph is
B_r, while the conflict graph of H_{B_r} contains B_r as an induced subgraph.

Consequently:

* the trade itself may have linear balanced-separator size;
* the ambient conflict graph may have linear treewidth;
* the trade volume may be Theta(N).

So the statement

```text
LONG TRADE => SMALL GRAPH SEPARATOR
```

is false for the exact JANUS target class.

This does NOT refute the stronger multiplicity statement

```text
MANY RELEVANT NEAR-MINIMUM TRADES => SOME ALGEBRAIC/PRODUCT DECOMPOSITION.
```

It only proves that the separator cannot be inferred from the geometry of one
large trade.

External support:

Böttcher, Pruessmann, Taraz, Würfl,
"Bandwidth, expansion, treewidth, separators and universality for bounded-degree graphs",
European Journal of Combinatorics 31 (2010), 1217-1227,
DOI 10.1016/j.ejc.2009.10.010.

Cavenagh and Griggs,
"Subcubic trades in Steiner triple systems",
Discrete Mathematics 340 (2017), 1351-1358,
DOI 10.1016/j.disc.2016.10.021,
independently connect restricted Steiner trades with 3-regular
1-factorisable graphs.  This is a near-neighbour, not an identity with the
construction above.

## 7. Interaction with E109-E111 and E116

E109-E111 already provide exact decomposition / branch-DP machinery once a
suitable low-order subspace separator is available.

E116 proves an exact width-2 separator for nontrivial 3-edge cuts in a faithful
cographic normal core.

Section 6 shows that the parity route cannot hope to manufacture such a
separator merely from the existence of a large connected trade: the trade may
itself be an expander.

Therefore the useful successor theorem must be stated in the solution-space /
trade-span language, not solely as a graph-separator theorem.

## 8. Revised theorem target

The sharpened target is:

```text
TRADE SMOOTH-COUNT / ALGEBRAIC-SEPARATOR DICHOTOMY

Given the current minimum perfect-matching face F and its minimum connected
trade volume g, construct in polynomial time one of:

A. SMOOTH COUNT:
   a polynomially enumerable set containing every relevant connected
   zero-circulation trade of volume <= alpha*g, for the constant alpha needed
   by the isolation refinement;

or

B. ALGEBRAIC / PRODUCT SEPARATOR:
   a nontrivial low-order separation of the trade span / normal arrangement /
   exact-cover interface such that the two sides admit additive polynomial
   dynamic programming and can be recombined without multiplicative branching.
```

The word "algebraic" is essential.

A physical small separator of each individual trade is impossible in general
by Section 6.

## 9. What has actually advanced

Before this checkpoint:

```text
bounded hashing worked only if a polynomial trade family was handed to us.
```

After this checkpoint:

```text
ALL connected trades of volume <= C log N
are polynomially enumerable from the instance alone,
and one polynomially bounded deterministic weighting kills all of them at once.
```

Thus every surviving non-unique minimum face can be normalized to have

```text
minimum connected trade volume > C log N
```

for any fixed C.

The unresolved core is therefore no longer "short trades".

It is:

```text
HIGH-DISTANCE MINIMUM FACES WITH LONG, POSSIBLY EXPANDING TRADE COMPONENTS.
```

## 10. Replay

Companion checker:

```text
experiments/r5_parity_trade_smooth_count_separator_frontier.py
```

It constructs an 18-vertex / 18-hyperedge square-cubic-linear control from a
connected cubic bipartite graph with six vertices per side and verifies:

```text
SQUARE_3UNIFORM_3REGULAR_LINEAR = PASS
THREE_EXPLICIT_PERFECT_MATCHINGS = PASS
EMBEDDED_CUBIC_BIPARTITE_TRADE = PASS
```

It then exhausts all 2^18 hyperedge subsets and verifies every induced
connected cubic bipartite support is a valid local trade.

Frozen control counts:

```text
connected local trade supports = 6
volumes:
  3 -> 2
  6 -> 4
```

These finite counts are only replay controls; the theorems in Sections 2-6 are
symbolic.

## 11. Claim boundary

```text
LOGARITHMIC_TRADE_SMOOTH_COUNT = PROVED LOCALLY.
DETERMINISTIC_LOG_TRADE_PURGE = PROVED LOCALLY.
ARBITRARY_CUBIC_BIPARTITE_TRADE_REALIZATION = PROVED LOCALLY.

POLYNOMIAL NEAR-MINIMUM TRADE COUNT FOR ARBITRARY g = OPEN.
TRADE-SPAN / ALGEBRAIC-SEPARATOR DICHOTOMY = OPEN.
POLYNOMIAL ISOLATING FAMILY = OPEN.
POLYNOMIAL PARITY SOLVER = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.
```
