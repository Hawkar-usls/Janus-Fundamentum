# R5 E9 — Paley(5419) balanced 4-critical order > 9 falsifier

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY5419_BALANCED_CRITICAL_ORDER_GT9__CATALOG_REPLAY_PENDING__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY_ORBIT_EXACT_F3_CONSTANT_GRADIENT_KERNEL_AFFINE_CHART_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY331_CHARACTER_MOSER_MINIMAL_BALANCED_4CRITICAL_COVER_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley5419_balanced_4critical_order_gt9.py`

External complete catalog controls:
- Brendan McKay, Combinatorial Data, edge-critical graphs: `https://users.cecs.anu.edu.au/~bdm/data/graphs.html`
- graph6 data for 7 vertices: `https://users.cecs.anu.edu.au/~bdm/data/crit/crit_7_4.g6`
- graph6 data for 8 vertices: `https://users.cecs.anu.edu.au/~bdm/data/crit/crit_8_4.g6`
- graph6 data for 9 vertices: `https://users.cecs.anu.edu.au/~bdm/data/crit/crit_9_4.g6`
- Bjarne Toft, *On critical subgraphs of colour-critical graphs*, Discrete Mathematics 7 (1974), 377–392, DOI `10.1016/0012-365X(74)90045-4`; the paper gives a list of all 4-critical graphs on at most nine vertices.

Scientific ceiling:

```text
This is a scoped falsifier for bounded balanced ordinary-colouring gain motifs.
It is not a lower bound against arbitrary gain obstructions or arbitrary AF3 covers.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen member

Take

```text
q=5419,
r=-2 mod q,
O=<r>,
L=ord_5419(-2)=21.
```

Since `3|L`, the exact family theorem gives the complete affine chart

```text
z = r0 + c + grad(p),
```

with `c in F3`, where

```text
r0(r^k)=k mod 3.
```

Thus the full coordinate-hyperplane problem is exactly the three-slice character gain graph on `Z_5419` with supported differences

```text
S=O union (-O),
|S|=42.
```

For traversal by a supported difference `d`, define

```text
phi_c(r^k)  = -k-c mod 3,
phi_c(-r^k) =  k+c mod 3.
```

A balanced selected subgraph is switching-equivalent to the ordinary graph obtained by replacing all selected forbidden hyperplanes with edge inequalities. Hence any balanced 4-chromatic selected graph covers its entire affine `c`-slice.

## 2. Why q=5419 is a new family obstruction

For `q=331`, the first absent motif `K4` was repaired at order seven by a Moser spindle. For `q=5419`, that finite catalogue no longer suffices.

The exact checker performs translation- and switching-normalized embedding search for every complete edge-4-critical graph type through order nine.

The complete catalog sizes are

```text
order 4: 1
order 5: 0
order 6: 1
order 7: 2
order 8: 5
order 9: 21
```

The graph6 strings for orders seven through nine are frozen verbatim in the checker from McKay's public complete catalogue. Every decoded graph is independently rechecked to be connected, 4-chromatic, and edge-critical before use.

## 3. Exact embedding result

For each

```text
c=0,1,2
```

and for every catalogued edge-4-critical graph on at most nine vertices, the checker searches injective maps

```text
x:V(H)->Z_5419
```

and switching gauges

```text
g:V(H)->F3
```

satisfying, on every edge `uv`,

```text
x(v)-x(u) in S,
g(v)-g(u)=phi_c(x(v)-x(u)).
```

Translation and additive switching are normalized by fixing one pattern vertex to

```text
x(v0)=0,
g(v0)=0.
```

The search is complete because every connected embedding can be translated and globally switched into that normalization. At each recursive step a new pattern vertex is generated from a supported difference to an already embedded neighbour and checked against every already embedded incident edge.

Exact result:

```text
balanced edge-4-critical embeddings of order <=9 = 0
```

for all three slices.

In particular:

```text
K4         absent,
W5         absent,
Moser      absent,
Mycielski(K3) absent,
all five order-8 critical types absent,
all twenty-one order-9 critical types absent.
```

Therefore

```text
minimum order of a balanced ordinary 4-chromatic obstruction
for every q=5419 affine slice is > 9.
```

## 4. Exact search accounting

The normalized search visits the same number of states in each slice because changing `c` shifts the gain labels without changing the support graph or branching structure.

Across the full order-4/6/7/8/9 catalogue the checker visits

```text
369084 recursive search states per slice,
1107252 total over c=0,1,2.
```

The largest single search is one order-nine critical graph and uses

```text
187027 states.
```

These counts are regression controls, not complexity claims for arbitrary pattern size.

## 5. Consequence

The sequence

```text
q=19   -> balanced K4 exists,
q=331  -> no K4/W5, but balanced Moser exists at order 7,
q=5419 -> no balanced edge-4-critical obstruction through order 9
```

falsifies any proposed family theorem that relies on the fixed small catalogue of critical motifs through order nine.

This is stronger than saying one named gadget fails: the complete ordinary balanced critical catalogue through nine fails simultaneously.

It does **not** yet prove that the minimum balanced critical order is unbounded as `q` grows. It also does not exclude smaller genuinely non-balanced gain obstructions, nor does it determine the minimum normal rank of a full three-slice cover.

## 6. Next constructive gate

Freeze

```text
R5_E9_PALEY_CHARACTER_CRITICAL_ORDER_GROWTH_GATE_V2
```

Next steps:

1. test the complete order-ten edge-4-critical catalogue (150 types) by the same exact embedding engine;
2. if the first motif appears, extract its algebraic difference pattern and ask whether it admits a polynomial construction from the multiplicative character;
3. if no order-ten motif appears, continue by catalogue only while the finite control remains computationally cheap;
4. in parallel search genuinely non-coboundary gain obstructions, because balanced ordinary critical graphs may be the wrong terminal class;
5. separate motif order from normal-rank cover size at every stage;
6. promote nothing to E8-D1 without a family-wide polynomial constructor and complete SAT reduction/reconstruction proof.

## 7. Ceiling

```text
q=5419 AF3 branch                              = CONSISTENT
exact full affine chart                        = CONSTANT + GRADIENT
balanced critical obstruction order <=9        = NONE
minimum balanced ordinary critical order       > 9
minimum balanced critical order exactly        = OPEN
non-balanced gain obstruction order             = OPEN
rho_min(Paley5419)                              = OPEN
universal polynomial solver                     = NOT PROVED
E8_D1                                           = EMPTY
P_VS_NP                                         = OPEN
```
