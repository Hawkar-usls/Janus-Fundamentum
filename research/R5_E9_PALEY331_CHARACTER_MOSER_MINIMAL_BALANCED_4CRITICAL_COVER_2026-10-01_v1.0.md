# R5 E9 — Paley(331) character-gain Moser cover and minimal balanced 4-critical order

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY331_BALANCED_MOSER_COVER__SCOPED_MINIMAL_ORDER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY_ORBIT_EXACT_F3_CONSTANT_GRADIENT_KERNEL_AFFINE_CHART_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_AF3_CHARACTER_SPLIT_AND_K4_MOTIF_FALSIFIER_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley331_character_moser_balanced_4critical_cover.py`

## 1. Why q=331 is the first hard control after the K4 motif

For

```text
q=331,
r=-2 mod 331,
L=ord_331(-2)=15,
```

we have `3|L`, so by the exact family theorem the full affine solution space of `A z=1` is

```text
z = r0 + c + grad(p),
```

with `c in F3` and one potential `p:Z_331->F3` modulo additive constants.

The support connection set is

```text
S=O union (-O),
O=<r>,
|O|=15,
|S|=30.
```

The previous exact checker proved that `Cay(Z_331,S)` is K4-free.  Hence the Paley19 three-gain-K4 terminal does not extend to this member.

## 2. Exact gain form

Index `O` as `r^k`, `k in Z_15`, and use

```text
r0(r^k)=k mod 3.
```

For traversal by a supported difference `d`, define the slice-c gain

```text
phi_c(r^k)   = -k-c mod 3,
phi_c(-r^k)  =  k+c mod 3.
```

A selected edge family is balanced for slice `c` precisely when there is a gauge `s(v)` satisfying

```text
s(v)-s(u)=phi_c(v-u)
```

on every selected edge.  After the shift `q(v)=p(v)-s(v)`, every selected forbidden hyperplane becomes the ordinary inequality

```text
q(v) != q(u).
```

Therefore any balanced 4-chromatic selected subgraph covers that whole affine `c`-slice.

## 3. Canonical balanced diamonds from the order-three character

Put

```text
m=L/3=5,
zeta=r^m.
```

Then `zeta^3=1`, `zeta!=1`, so

```text
1+zeta+zeta^2=0.
```

For any exponent `a`, there are two canonical balanced triangles rooted at zero.

### Type A

```text
x=r^a,
y=-r^(a+m),
y-x=r^(a+2m).
```

The identity `-zeta-1=zeta^2` gives the base-edge relation, and direct substitution in `phi_c` gives

```text
phi_c(y)-phi_c(x)=phi_c(y-x).
```

### Type B

```text
x=r^a,
y=-r^(a+2m),
y-x=r^(a+m).
```

Again the base and gain equations hold identically.

If `{0,x,y}` is either such balanced triangle, set

```text
t=x+y.
```

Then

```text
t-x=y,
t-y=x,
```

so the five edges

```text
0-x, 0-y, x-y, x-t, y-t
```

form a balanced `K4-e` diamond.  In every ordinary 3-colouring of this diamond, the nonadjacent vertices `0` and `t` are forced to have the same colour.

Two balanced diamonds with common root zero, whose tips are joined by one additional balanced edge, therefore form a Moser spindle and are not 3-colourable.

This replaces a generic seven-vertex subset search by a constant-type algebraic motif with only `2L` canonical triangle states and a polynomial bridge scan.

## 4. Explicit q=331 Moser certificates for all three slices

Use the Moser edge pattern consisting of two `K4-e` diamonds sharing root `0` and one edge joining their tips.

### c=0

```text
Diamond A: {0,1,32,33}
Gauge:     s(0)=0, s(1)=0, s(32)=2, s(33)=2

Diamond B: {0,203,327,199}
Gauge:     s(203)=2, s(327)=2, s(199)=1

Tip edge: 33--199
```

The oriented traversal difference `199-33=166` has `phi_0(166)=2=s(199)-s(33)`.

### c=1

A support-minimizing choice sharing the second diamond with the `c=0` certificate is

```text
Diamond A: {0,16,181,197}
Gauge:     s(0)=0, s(16)=1, s(181)=1, s(197)=2

Diamond B: {0,203,327,199}
Gauge:     s(203)=1, s(327)=0, s(199)=1

Tip edge: 197--199
```

The checker verifies every gain equation exactly.

### c=2

```text
Diamond A: {0,1,32,33}
Gauge:     s(0)=0, s(1)=1, s(32)=1, s(33)=2

Diamond B: {0,323,248,240}
Gauge:     s(323)=1, s(248)=0, s(240)=1

Tip edge: 33--240
```

Again all eleven selected Moser edges satisfy the exact slice gain equations.

Each selected graph is a Moser spindle: seven vertices, eleven edges, chromatic number four, and deletion of any one selected edge makes it 3-colourable.

Therefore each one covers its complete affine `c`-slice.

## 5. Minimal balanced 4-critical order for q=331

The checker performs an independent finite graph catalog for all labelled simple graphs on at most six vertices.

For edge-4-critical connected graphs it obtains exactly

```text
n=4: 1 labelled type  -> K4
n=5: 0
n=6: 72 labelled copies of one type -> odd wheel W5
```

The degree sequence of every six-vertex critical graph is

```text
(3,3,3,3,3,5),
```

which forces the unique unlabeled type to be the five-rim odd wheel.

Exact gain-embedding search, normalized by translation of the root to base vertex zero and by additive gauge shift to root gauge zero, finds for every `c in F3`:

```text
balanced K4 embeddings = 0,
balanced W5 embeddings = 0.
```

The explicit seven-vertex Moser embeddings above exist.

Hence:

```text
minimum number of vertices in a balanced ordinary 4-chromatic obstruction
for each q=331 affine slice = 7.
```

This is a scoped minimality statement for **balanced ordinary-colouring obstructions**.  It is not a lower bound against genuinely non-coboundary gain obstructions.

## 6. Explicit full three-slice cover of normal rank 13

Choose the three Moser certificates above.  Their union has

```text
13 active base vertices,
23 distinct source arcs.
```

The selected underlying graph is connected.  Direct Gaussian elimination over `F3` on the selected normal rows

```text
N_E=[1 | D_E]
```

gives

```text
rank(D_E)=12,
rank(N_E)=13.
```

Thus

```text
rho_min(Paley331) <= 13.
```

The checker also exhausts the ten distinct normalized Moser edge sets available in each slice within the exact gain graph.  Over all `10^3` triples, thirteen active vertices is the minimum possible union support, and the displayed triple attains it.

This does **not** prove `rho_min(Paley331)=13`: a lower-rank cover could use larger/nonbalanced gain structures not decomposing into one balanced Moser spindle per slice.

## 7. Literature / anti-loop alignment

The ordinary graph fact used here is classical: the Moser spindle is a seven-vertex 4-chromatic graph.  Complete small critical-graph catalogs list `K4` at order four, the odd wheel at order six, and the Moser spindle among the two order-seven 4-critical graphs.  The checker does not rely on that catalog for the <=6 minimality claim; it regenerates the <=6 catalogue exhaustively.

The gain-graph step is standard switching/balance machinery: a balanced gain subgraph is switching-equivalent to the trivial-gain graph.  The new content here is the exact embedding of those critical graphs into the frozen Paley character gain instance.

## 8. Constructive significance

The Paley19 `K4` motif was too narrow.  q=331 shows the next critical graph already repairs that failure:

```text
K4 absent
-> W5 absent
-> Moser spindle present
```

and it is found by a polynomial exact motif scan rather than by enumerating affine assignments.

However this is not yet a family theorem.  The next gate is to determine whether a fixed finite catalogue of character-balanced 4-critical motifs suffices for every AF3-consistent Paley-orbit member, or whether the minimum obstruction order grows.

## 9. Next target

Freeze

```text
R5_E9_PALEY_CHARACTER_CRITICAL_ORDER_GROWTH_GATE_V1
```

Tasks:

1. scan AF3-consistent members in increasing `q` using exact fixed-pattern embedding;
2. for each member record the minimum balanced 4-critical order;
3. use the complete edge-4-critical graph catalog only as a finite control, never as a heuristic proof;
4. if a uniform order bound emerges, derive an algebraic construction / polynomial extractor;
5. if the minimum order grows, freeze the first exact counterexample and move to non-coboundary gain obstructions;
6. keep normal-rank accounting separate from motif order.

## 10. Ceiling

```text
q=331 exact F3 affine chart                 = COMPLETE
balanced K4 obstruction                     = ABSENT
balanced W5 obstruction                     = ABSENT
balanced Moser obstruction                   = PRESENT for c=0,1,2
minimum balanced ordinary 4-critical order   = 7
explicit full cover normal rank              <= 13
rho_min(Paley331)                            = OPEN
universal fixed critical-motif theorem       = OPEN
universal polynomial SAT solver              = NOT PROVED
E8_D1                                        = EMPTY
P_VS_NP                                      = OPEN
```
