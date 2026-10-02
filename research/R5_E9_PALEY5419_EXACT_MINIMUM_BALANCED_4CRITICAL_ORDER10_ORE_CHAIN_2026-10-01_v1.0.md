# R5 E9 — Paley(5419) exact minimum balanced 4-critical order 10 and Ore-chain witness

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY5419_BALANCED_CRITICAL_ORDER10__ORE_CHAIN_WITNESS__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY5419_BALANCED_4CRITICAL_ORDER_GT9_FALSIFIER_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY331_CHARACTER_MOSER_MINIMAL_BALANCED_4CRITICAL_COVER_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley5419_exact_minimum_balanced_4critical_order10.py`

## 1. Exact result

For the frozen AF3-consistent Paley-orbit member

```text
q = 5419,
r = -2 mod q,
L = ord_q(r) = 21,
S = <r> union -<r>,
|S| = 42,
```

the previous exact checker proved that no balanced ordinary edge-4-critical obstruction of order at most 9 embeds in any affine slice `c in F3`.

A complete scan of the public 150-type order-10 edge-4-critical catalogue found the same order-10 type in all three slices:

```text
graph6 = ICOcePkL_
```

The new checker does not rely on the external catalogue for correctness of the witness: it decodes this graph, verifies connectedness, non-3-colourability, and edge-4-criticality directly, then checks the gain embedding equations exactly.

Therefore, for each `c=0,1,2`,

```text
minimum balanced ordinary edge-4-critical obstruction order = 10.
```

## 2. Explicit embeddings

Using graph vertices `0..9` in graph6 order, the checker verifies the following injective embeddings `x:V(H)->Z_5419` and gauges `g:V(H)->F3`.

### c=0

```text
x = [3516,1,4064,3520,128,5387,4028,129,0,4032]
g = [1,0,1,2,1,1,1,1,0,2]
```

### c=1

```text
x = [2839,1,3371,2843,128,5403,3351,129,0,3355]
g = [1,2,0,1,2,2,2,1,0,2]
```

### c=2

```text
x = [5040,1,1016,5072,128,5411,976,129,0,1008]
g = [1,1,1,2,0,1,1,1,0,2]
```

For every graph edge `uv` the checker proves

```text
x(v)-x(u) in S,
g(v)-g(u) = phi_c(x(v)-x(u)) mod 3.
```

Hence switching by `g` turns the selected gain subgraph into the ordinary 4-critical graph, so the whole affine `c`-slice is covered.

## 3. The order-10 graph is an Ore extension of the q=331 Moser type

The decoded graph has

```text
|V| = 10,
|E| = 16,
degree multiset = (3,3,3,3,3,3,3,3,4,4).
```

The vertex cut `{8,9}` separates the pair `{2,5}` from the other six non-cut vertices.

On vertices

```text
{2,5,8,9}
```

the induced side is exactly `K4-e`, with missing edge `8--9`.

On the other side, identifying `8~9` produces the seven-vertex graph6 type

```text
FQjRo
```

which is the same Moser-type order-7 edge-4-critical graph used by the q=331 layer.

Thus the q=5419 witness is exactly an Ore composition of `K4` with the q=331 Moser-type graph.

This is stronger than a catalogue hit: the first three observed balanced minima now form the 4-Ore chain

```text
q=19,   L=9   -> order 4  -> K4
q=331,  L=15  -> order 7  -> Moser-type = Ore(K4,K4)
q=5419, L=21  -> order 10 -> Ore(K4,Moser-type)
```

and numerically satisfy

```text
order = (L-1)/2
```

for these three members.

That equality is **not** promoted to a family theorem from three data points.

## 4. Constructive significance

The fixed-small-motif route failed at q=5419 through order 9, but the first surviving motif is not arbitrary: it lies on a recursive 4-Ore chain.

This creates a sharply defined next constructive gate:

```text
R5_E9_PALEY_CHARACTER_ORE_RECURSION_GATE_V1
```

Instead of enumerating all critical graphs of growing order, test whether the character gain geometry itself admits a recursive Ore extension.

The next natural AF3-consistent control is obtained at

```text
L = 27,
q = 87211,
q | (2^27+1),
ord_q(-2)=27.
```

If the observed law continues, the predicted balanced critical order is

```text
(L-1)/2 = 13.
```

The required test is exact:

1. construct the canonical next 4-Ore graph from the order-10 witness;
2. search for a gain-balanced embedding in q=87211 using translation/switching normalization;
3. if present, derive the embedding algebraically from the multiplicative character rather than by generic subset search;
4. independently test all smaller relevant Ore-chain orders before any minimum claim;
5. if absent, freeze q=87211 as a falsifier of the recursive hypothesis and move to non-coboundary gain obstructions.

## 5. Ceiling

```text
q=5419 AF3 branch                              = CONSISTENT
balanced ordinary critical order <=9           = NONE
balanced ordinary critical order 10             = PRESENT in all three slices
minimum balanced ordinary critical order        = 10
order-10 witness                                = 4-Ore extension of q=331 Moser type
observed order=(L-1)/2 law                      = THREE-MEMBER CONJECTURAL PATTERN ONLY
rho_min(Paley5419)                              = OPEN
non-balanced gain obstruction order             = OPEN
family-wide polynomial constructor              = NOT PROVED
universal polynomial SAT solver                 = NOT PROVED
E8_D1                                           = EMPTY
P_VS_NP                                         = OPEN
```
