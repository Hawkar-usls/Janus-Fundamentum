# R5 E9 — Signed-Trade Polynomial-Size Boundary Projection Theorem

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_REPRESENTATION_CHANGE_DONOR__BOUNDARY_APPLICABILITY_CLOSED_FOR_EXPLICIT_CONNECTED_TRADE__NOT_UNIVERSAL__NO_D1_PROMOTION`

Parent:
`research/R5_E9_BINARY_KERNEL_BIPARTITE_TRADE_DONOR_2026-09-27_v1.0.md`

Checker:
`experiments/r5_e9_signed_trade_polysize_boundary_projection.py`

Scientific firewall:

```text
EXPLICIT CONNECTED SIGNED TRADE = INPUT CERTIFICATE.
TRADE DISCOVERY / UNIVERSAL COVERAGE = OPEN.
MIXED-CARRIER GLOBAL SOLVABILITY = OPEN.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `K=(L dot-union R,E)` be one connected bipartite support component of an explicit signed trade in a positive Exact-One-3 instance. Every touched Exact-One clause contains exactly one `l in L`, one `r in R`, and one third variable outside the trade support. Write that boundary variable as `z_{lambda(e)}`. Repeated boundary labels are allowed.

Thus every touched clause has the exact Boolean equation

```text
x_l + x_r + z_{lambda(e)} = 1.
```

Orient every support edge from `L` to `R`.

## 2. Difference-coordinate lemma

Define

```text
y_l = x_l          for l in L,
y_r = 1 - x_r      for r in R.
```

Then each touched Exact-One equation is equivalent to

```text
y_r - y_l = z_{lambda(e)}.
```

Because all variables are Boolean, the only allowed local transformed states are

```text
(y_l,y_r,z) = (0,0,0), (0,1,1), (1,1,0).
```

In particular `y_l <= y_r` on every oriented support edge.

## 3. Spanning-tree boundary projection

Choose any spanning tree `T` of `K` and any root `v0`.

For each vertex `v`, define an integer linear path potential `p_v(z)` along the unique root-to-`v` tree path. Traversing an edge in its canonical `L -> R` orientation adds its boundary bit; traversing it in reverse subtracts its boundary bit. Set

```text
p_v0(z) = 0.
```

Therefore every tree edge `(l,r)` satisfies identically

```text
p_r(z) - p_l(z) = z_{lambda(e)}.
```

Introduce one new Boolean bit

```text
q = y_v0.
```

### Theorem STBP-1

The touched Exact-One block has an assignment to all internal variables `x_v`, `v in V(K)`, for a boundary assignment `z` iff there exists `q in {0,1}` satisfying

for every non-tree edge `e=(l,r)`:

```text
p_r(z) - p_l(z) = z_{lambda(e)},
```

and for every vertex `v`:

```text
0 <= q + p_v(z) <= 1.
```

Whenever these constraints hold, an internal assignment is reconstructed by

```text
x_l = q + p_l(z)          for l in L,
x_r = 1 - q - p_r(z)      for r in R.
```

### Proof: forward direction

Assume an internal Exact-One assignment exists and form the transformed bits `y`. Along every tree edge,

```text
y_r - y_l = z_{lambda(e)}.
```

Telescoping on the unique tree path from `v0` to `v` gives

```text
y_v = y_v0 + p_v(z) = q + p_v(z).
```

Every non-tree edge also obeys the original transformed equation, hence

```text
p_r(z)-p_l(z)=z_{lambda(e)}.
```

Finally every `y_v` is Boolean, giving the range inequalities.

### Proof: reverse direction

Assume the displayed chord equalities and range inequalities hold for a Boolean `q`. Define

```text
y_v = q + p_v(z).
```

The range inequalities and integrality imply every `y_v` is Boolean. Tree-edge equations hold by construction of `p`; non-tree edge equations are exactly the chord constraints. Therefore

```text
y_r-y_l=z_{lambda(e)}
```

for every support edge. Reversing the coordinate change yields the displayed `x_l,x_r`, and every touched Exact-One equation sums to one. QED.

## 4. Fixed-boundary fibre corollary

For a fixed boundary assignment `z`, the connected block has at most two internal assignments.

If two solutions exist, their `y`-difference has zero derivative on every connected support edge, so it is a global constant. If any boundary edge has `z=1`, that edge forces `(y_l,y_r)=(0,1)` and the constant ambiguity disappears. Hence:

```text
compatible all-zero boundary  -> exactly 2 internal states,
compatible nonzero boundary   -> exactly 1 internal state,
incompatible boundary         -> 0 internal states.
```

This is a corollary of the exact projection, not a separate algorithmic assumption.

## 5. Polynomial construction and size

Given the explicit connected trade component:

1. find a spanning tree in `O(|V|+|E|)` time;
2. build every path potential by tree traversal;
3. emit `|E|-|V|+1` chord equalities;
4. emit `2|V|` range inequalities;
5. keep one new Boolean bit `q`;
6. store the reconstruction formulas above.

With naive sparse coefficient dictionaries the total path-expression size is `O(|V||E|)`. Repeated boundary labels only combine integer coefficients; every coefficient magnitude is at most the path length, so coefficient bit length is `O(log |V|)`.

Thus the representation change, verification, and witness reconstruction are deterministic polynomial time and polynomial size.

## 6. R6 consequence

The parent theorem required every boundary variable to be structurally pinned to zero before a connected trade became immediately useful. STBP-1 removes that requirement completely for an explicit connected trade.

The local block can be replaced exactly by:

```text
one Boolean root bit q
+ polynomially many linear equalities/inequalities over the existing boundary bits.
```

Therefore the number of internal Boolean dimensions drops from `|V(K)|` to one, a strict drop of `|V(K)|-1` for every nontrivial connected trade component.

This is an exact representation-changing R6 donor. It does not assert that the resulting mixed pseudo-Boolean carrier is globally polynomial-time decidable.

## 7. What remains open

This theorem closes the old `BOUNDARY_PINNING_REQUIRED` applicability gap only after a useful trade is explicitly supplied.

The live universal frontier is now:

```text
R5_E9_SIGNED_TRADE_POLY_DISCOVERY_OR_MIXED_CARRIER_CLOSURE_GATE_V1
```

Required future work:

1. polynomially discover a useful nonzero signed trade whenever the universal algorithm needs progress, or prove a different polynomial move for the no-trade residue;
2. prove polynomial closure/composition for repeated STBP projections in the mixed linear/PB carrier;
3. solve or contract trade-free / unique-model residuals without a semantic SAT oracle;
4. prove an arbitrary-input polynomial coverage theorem.

The parent difference-of-models theorem guarantees that two distinct Exact-One models imply existence of a trade. It does not give polynomial trade discovery, and it does not solve the zero-versus-one-model case.

## 8. Prior-art / anti-loop boundary

The signed-trade / bipartite-support language is source-bound to combinatorial trade/bitrade literature. Graph closure and order-ideal structures with monotone edge constraints are classical; Picard's maximal-closure framework is a standard source-bound donor. The checked literature did not supply the exact STBP-1 spanning-tree projection specialized to this JANUS Exact-One support component. No world-priority claim is made.

Representative sources checked:

- J.-C. Picard, *Maximal Closure of a Graph and Applications to Combinatorial Problems*, Management Science 22(11), 1976, DOI `10.1287/mnsc.22.11.1268`.
- N. J. Cavenagh and T. S. Griggs, *Subcubic trades in Steiner triple systems*, Discrete Mathematics 340(6), 2017, DOI `10.1016/j.disc.2016.10.021`.
- D. S. Krotov, I. Y. Mogilnykh, V. N. Potapov, *To the theory of q-ary Steiner and other-type trades*, Discrete Mathematics 339(3), 2016, DOI `10.1016/j.disc.2015.11.002`.

## 9. Ceiling

```text
EXPLICIT_CONNECTED_TRADE_BOUNDARY_PINNING_REQUIREMENT
= CLOSED

EXACT_BOUNDARY_PROJECTION
= PROVED POLYNOMIAL-SIZE

INTERNAL_BOOLEAN_DIMENSION
= |V(K)| -> 1

REPEATED_BOUNDARY_LABELS
= ALLOWED

TRADE_DISCOVERY
= OPEN

MIXED_CARRIER_GLOBAL_CLOSURE
= OPEN

UNIVERSAL_SELECTOR / E8_D1
= OPEN / EMPTY

P_VS_NP
= OPEN
```
