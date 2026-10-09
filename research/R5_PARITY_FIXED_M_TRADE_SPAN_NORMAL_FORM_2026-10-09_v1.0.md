# R5 Parity — Fixed-M trade-span normal form and firewall

Date: 2026-10-09

Predecessor checkpoint:
`research/R5_PARITY_TRADE_SMOOTH_COUNT_SEPARATOR_FRONTIER_2026-10-09_v1.0.md`

Mainline provenance anchor:
`e7d6790d533f9acd3c4fe7f2439542dfbfa3361c`

Scientific ceiling:

```text
THIS CHECKPOINT DOES NOT PROVE
  SUPERPOLYNOMIAL NEAR-TRADE COUNT => LOW CONNECTIVITY.

IT DOES NOT CONSTRUCT A POLYNOMIAL ISOLATING FAMILY.
IT DOES NOT CONSTRUCT A UNIVERSAL POLYNOMIAL EXACTONE SOLVER.

P_VS_NP = OPEN.
```

The purpose of this checkpoint is to derive the exact object that must be
controlled after fixing one minimum perfect matching M.

## 1. Fixed-M residual cubic graph

Let H be a square, 3-uniform, 3-regular, linear hypergraph and let M be one
perfect matching.

Delete the matching hyperedges M.

Every clause-vertex of H had degree three and exactly one incident hyperedge
from M, so exactly two non-M hyperedges remain at that clause.

Define R_M:

* V(R_M) = E(H) - M, the variables outside M;
* each clause becomes one edge joining its two non-M variables.

Then:

* every non-M variable belongs to exactly three clauses, so R_M is cubic;
* linearity of H forbids two non-M variables from sharing two clauses, so R_M
  is simple.

For m in M, its three clauses become three edges of R_M.  Denote this triple
by B_m.

The three edges in B_m form a matching: if two shared a residual endpoint u,
then u and m would occur together in two clauses, contradicting linearity.

Hence:

```text
E(R_M) = disjoint union over m in M of B_m,
|B_m| = 3,
each B_m is a matching.
```

This is an exact canonical normal form relative to M.

## 2. Integer block-cut characterization

Let N be another perfect matching.

Put

```text
S = N - M subset V(R_M),
P = M - N subset M.
```

For a clause belonging to m in M, let uv be the corresponding edge of R_M.

Exact cover gives exactly:

```text
1_S(u) + 1_S(v) = 1_P(m).          (*)
```

Thus:

* if m is retained, all three edges B_m have endpoints 00;
* if m is removed, every edge of B_m has endpoints 01 or 10.

Equivalently,

```text
delta_R(S) = union_{m in P} B_m
```

and S is independent.

Conversely, any pair (S,P) satisfying (*) produces the perfect matching

```text
N = (M-P) union S.
```

Because R_M is cubic and the block triples have size three,

```text
|S| = |P|.
```

So fixed-M trades are exactly independent-shore cuts whose crossing set is a
union of whole 3-edge matching blocks.

This is substantially narrower than arbitrary cuts and substantially narrower
than arbitrary binary kernel words.

## 3. Square fixed-M trade matrix

Introduce variables y_u for u in V(R_M) and z_m for m in M.

The homogeneous trade equations are

```text
y_u + y_v - z_m = 0
```

for every R_M edge uv in B_m.

There are:

```text
2r residual y variables,
r block z variables,
3r equations,
```

where r=|M|.

Thus the fixed-M system is square.

Binary solutions (y,z) in {0,1}^{3r} are exactly unions of fixed-M trade
components.

This is just the original Exact-One incidence kernel viewed in the orthant
determined by M, but the R_M/block form exposes additional structure.

## 4. Connected trade = real and binary column-matroid circuit

Let T=(S,P) be a connected fixed-M trade.

The corresponding signed vector d has:

```text
d_u = +1 for u in S,
d_m = -1 for m in P,
d = 0 otherwise.
```

For every active clause, exactly two support columns occur: one S-column and
one P-column.  Hence A d=0.

Now let q be any real kernel vector supported inside supp(d).

At every active clause the two supported coefficients sum to zero, so their
magnitudes agree and signs alternate across the trade incidence graph.

Since the trade graph is connected, either q=0 or q is a scalar multiple of d.

Therefore supp(d) is a circuit of the real column matroid M(A).

The same propagation over GF(2) shows it is a binary circuit as well.

So connected trades are not merely codewords; they are a special signed class
of genuine matroid circuits with coefficient pattern +/-1.

## 5. TU / regular shortcut firewall

Eliminate z_m by choosing one reference edge in each B_m and equating the
three endpoint sums.

The resulting fixed-M matrix D_M has rows of the form

```text
y_u + y_v - y_p - y_q = 0.
```

On the frozen 18x18 control, D_M is 12x12 of rank 9 and contains a 2x2 minor

```text
[-1 -1]
[ 1 -1]
```

with determinant 2.

Therefore:

```text
D_M is not totally unimodular.
```

Even after fixing M, the trade system does not automatically enter the
regular/TU regime used by known near-minimum circuit counting theorems.

This is a local exact obstruction, not an asymptotic heuristic.

External near-neighbour:
Gurjar and Vishnoi prove polynomial near-minimum circuit counts for regular
matroids, using regularity in an essential decomposition argument:
DOI 10.1137/20M1338642.

## 6. Coherent cut code over GF(2)

For z in GF(2)^M, repeat z_m on the three edges B_m.

A block vector z is coherent iff that repeated edge vector is a cut of R_M.

Equivalently, there exists x in GF(2)^{V(R_M)} satisfying

```text
x_u + x_v = z_m
```

for every uv in B_m.

Eliminating x gives the cycle equations

```text
sum_m |C intersect B_m| z_m = 0 mod 2
```

for every cycle C of R_M.

Thus the coherent block vectors form a binary linear code

```text
C_M = { z : repeat_B(z) in Cut(R_M) }.
```

Actual trades are a nonlinear subset: one shore of the coherent cut must be
independent, equivalently equation (*) must hold over the integers, not only
modulo two.

This separates the linear span question from the integrality / trade question.

## 7. Why ordinary Karger counting does not close the problem

A trade of volume g gives an ordinary cut of R_M of size 3g.

But R_M is cubic, so its ordinary edge connectivity is at most three (a
single-vertex star is a 3-cut).

Therefore Karger's polynomial bound on alpha-near cuts relative to the
*ordinary minimum cut* would compare 3g with a denominator at most three and
gives an exponent depending on g.

It is useful only while g=O(log n), exactly the sector already handled by the
logarithmic trade enumeration theorem.

The difficult regime is the block-coherent minimum, not the ordinary graph
minimum cut.

## 8. Natural defect function and its firewall

Let K_M be the bipartite incidence graph between residual vertices and M-blocks:
u is adjacent to m once for every clause containing u and m.

For S subset V(R_M), define

```text
Psi(S) = 3|N_K(S)| - 3|S| + 2 e_R(S).
```

Block by block this is nonnegative.

For a touched block B_m, let q be the number of its three paired R_M edges
with exactly one endpoint in S.  Its contribution is 3-q.

Hence

```text
Psi(S)=0
iff
every touched block has exactly one selected endpoint on all three paired edges
iff
S is a union of fixed-M trade components.
```

This gives an exact scalar defect.

However the frozen control supplies explicit pairs A,B with

```text
Psi(A)+Psi(B) < Psi(A union B)+Psi(A intersect B)
```

and other pairs with the reverse strict inequality.

So Psi is neither submodular nor supermodular.

The direct E110/E111 connectivity-function shortcut therefore does not arise
from this most natural defect function.

## 9. Minimum-face polymer representation

Fix a weight vector w and let M be a w-minimum perfect matching.

Every other w-minimum matching N decomposes uniquely, through M xor N, into
connected fixed-M trades.

By the minimum-face component-flip lemma, every such component has zero
w-circulation.

Conversely any collection of clause-disjoint zero-circulation fixed-M trades
can be flipped simultaneously and remains a w-minimum perfect matching.

Thus the minimum face can be viewed combinatorially as compatible packings of
connected zero-circulation M-trades.

This explains why a large family of *disjoint* trades is already a product
decomposition; the unresolved case is many heavily overlapping near-minimum
trade circuits.

## 10. Generic span-only theorem is impossible

The desired implication cannot follow merely from:

```text
binary linear span + minimum distance.
```

General binary codes can have exponentially many codewords within any fixed
factor alpha>1 of minimum distance by choosing positive-rate codes whose
relative minimum distance is sufficiently close to 1/2.

Moreover any nonzero codeword of weight <2d is support-minimal: if a nonzero
word c' had proper support inside c, then c' and c+c' would be disjoint
nonzero words of total weight wt(c), forcing wt(c)>=2d.

So generic binary spans can have exponentially many near-minimum circuits.

Any successful theorem must use the exact fixed-M block-cut / cubic-linear
geometry above.

## 11. Current exact hard core

The requested implication remains open:

```text
SUPERPOLYNOMIALLY MANY ZERO-CIRCULATION
CONNECTED FIXED-M TRADES OF VOLUME <= alpha*g
    =>
LOW-CONNECTIVITY CUT OF THEIR GF(2)/INTEGER SPAN.
```

What this checkpoint proves is that any counterexample can now be normalized
to the following object:

```text
R:
  simple cubic graph;

B:
  partition E(R) into 3-edge matchings B_m;

M-trades:
  nonempty binary solutions of
      y_u + y_v = z_m
  whose support is connected;

g:
  minimum connected trade volume;

hard family:
  superpolynomially many connected zero-circulation solutions
  of volume <= alpha*g;

forbidden easy exits:
  g = O(log n);
  low-width E109-E111 decomposition;
  ordinary graph min-cut counting;
  automatic TU/regularity.
```

This is a much narrower combinatorial object than an arbitrary binary matroid.

## 12. Next theorem target

```text
BLOCK-COHERENT CIRCUIT COUNT / SPAN-SEPARATOR THEOREM

For the cubic graph + 3-edge-matching-block system above, and a fixed linear
weight w, prove that for some absolute alpha>1:

either

  the connected zero-w-circulation block-coherent circuits of volume
  <= alpha*g are polynomially many,

or

  their signed/linear span admits a polynomially discoverable low-order
  separation compatible with E109-E111 additive branch DP.
```

The separator must be a separator of the circuit/trade span or exact-cover
interface.  Section 5 and the previous expander-trade realization show that it
cannot be inferred from a physical separator of one trade.

## 13. Replay

Companion checker:

`experiments/r5_parity_fixed_m_trade_span_normal_form.py`

Frozen control verifies:

* R_M is simple cubic;
* every B_m is a 3-edge matching and the blocks partition E(R_M);
* all 4096 residual vertex subsets satisfy the exact integer block-cut
  characterization;
* there are 5 fixed-M trade unions including the empty state and 4 nonempty
  connected trades on this control;
* connected trade volumes are 3 (two trades) and 6 (two trades);
* every connected trade support has column rank |support|-1 and every
  one-column deletion is independent;
* D_M has a determinant-2 minor;
* Psi zeros are exactly the fixed-M trade unions;
* Psi is neither submodular nor supermodular.

## Claim boundary

```text
FIXED_M_BLOCK_CUT_NORMAL_FORM = PROVED_LOCALLY.
CONNECTED_TRADE_IS_COLUMN_MATROID_CIRCUIT = PROVED_LOCALLY.
FIXED_M_AUTOMATIC_TU = REFUTED.
ORDINARY_KARGER_SHORTCUT = INSUFFICIENT FOR LARGE g.
NATURAL_PSI_SUBMODULARITY = REFUTED.

SUPERPOLY_NEAR_TRADES => LOW SPAN CONNECTIVITY = OPEN.
POLYNOMIAL ISOLATING FAMILY = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.
```
